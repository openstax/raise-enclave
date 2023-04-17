from datetime import datetime
import json
from typing import Literal
from uuid import UUID, uuid4
from math import isnan
import os
import boto3
import argparse
import pandas as pd
from io import BytesIO
from pydantic import BaseModel, Extra, validator

MODEL_FILE_USERS = "users.csv"
MODEL_FILE_COURSES = "courses.csv"
MODEL_FILE_ENROLLMENTS = "enrollments.csv"
MODEL_FILE_ASSESSMENTS = "assessments.csv"
MODEL_FILE_GRADES = "grades.csv"
MODEL_QUIZ_QUESTIONS = "quiz_questions.csv"
MODEL_QUIZ_QUESTION_CONTENTS = "quiz_question_contents.csv"
MODEL_MULTICHOICE_ANSWERS = "quiz_multichoice_answers.csv"
MODEL_INPUT_INSTANCES = "ib_input_instances.csv"
MODEL_PSET_PROBLEMS = "ib_pset_problems.csv"
MODEL_COURSE_CONTENTS = "course_contents.csv"
MODEL_QUIZ_ATTEMPTS = "quiz_attempts.csv"
MODEL_QUIZ_ATTEMPT_MULTICHOICE_RESPONSES = \
     "quiz_attempt_multichoice_responses.csv"


class Demographic(BaseModel):
    user_uuid: UUID
    birth_date: str
    sex: Literal['male', 'female']
    american_indian_or_alaska_native: Literal['true', 'false']
    asian: Literal['true', 'false']
    black_or_african_american: Literal['true', 'false']
    native_hawaiian_or_other_pacific_islander: Literal['true', 'false']
    white: Literal['true', 'false']
    demographic_race_two_or_more_races: Literal['true', 'false']
    hispanic_or_latino_ethnicity: Literal['true', 'false']

    class Config:
        extra = Extra.forbid

    @validator('birth_date')
    def birthdate_format(cls, v):
        datetime.strptime(v, "%Y-%m-%d")
        return v


class Assessment(BaseModel):
    id: int
    name: str

    class Config:
        extra = Extra.forbid


class Course(BaseModel):
    id: int
    name: str

    class Config:
        extra = Extra.forbid


class Enrollment(BaseModel):
    user_uuid: UUID
    course_id: int
    role: Literal['student', 'teacher']

    class Config:
        extra = Extra.forbid


class Grade(BaseModel):
    assessment_id: int
    user_uuid: UUID
    course_id: int
    grade_percentage: float
    time_submitted: int

    class Config:
        extra = Extra.forbid

    @validator('grade_percentage')
    def grade_value(cls, v):
        if isnan(v):
            raise ValueError('Grade value is nan')
        if v < 0.0 or v > 100.0:
            raise ValueError(f'Grade value {v} is out of expected range')
        return v


class User(BaseModel):
    uuid: UUID
    first_name: str
    last_name: str
    email: str

    class Config:
        extra = Extra.forbid


class QuizQuestion(BaseModel):
    assessment_id: int
    question_number: int
    question_id: UUID

    class Config:
        extra = Extra.forbid


class QuizQuestionContents(BaseModel):
    id: UUID
    text: str
    type: Literal['multichoice', 'multianswer', 'numerical', 'essay']

    class Config:
        extra = Extra.forbid


class QuizMultichoiceAnswer(BaseModel):
    id: int
    question_id: UUID
    text: str
    grade: float
    feedback: str

    class Config:
        extra = Extra.forbid


class InputInteractiveBlock(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    content: str
    prompt: str

    class Config:
        extra = Extra.forbid


class ProblemSetProblem(BaseModel):
    id: UUID
    content_id: UUID
    variant: str
    pset_id: UUID
    content: str
    problem_type: Literal['input', 'dropdown', 'multiselect', 'multiplechoice']
    solution: str
    solution_options: str

    class Config:
        extra = Extra.forbid


class CourseContents(BaseModel):
    section: str
    activity_name: str
    lesson_page: str
    content_id: UUID

    class Config:
        extra = Extra.forbid


class QuizAttempts(BaseModel):
    id: int
    assessment_id: int
    user_uuid: UUID
    course_id: int
    attempt_number: int
    grade_percentage: float
    time_started: int
    time_finished: int

    class Config:
        extra = Extra.forbid


class QuizAttemptMultichoiceResponses(BaseModel):
    attempt_id: int
    question_number: int
    question_id: UUID
    answer_id: int

    class Config:
        extra = Extra.forbid


def multichoice_answer_model(clean_raw_df):
    quiz_multichoice_answer_df = clean_raw_df['quiz_multichoice_answers']
    quiz_multichoice_answer_df.insert(
        0, 'id', quiz_multichoice_answer_df.index
    )
    for item in quiz_multichoice_answer_df.to_dict(orient='records'):
        QuizMultichoiceAnswer.parse_obj(item)
    return quiz_multichoice_answer_df


def question_contents_model(clean_raw_df):
    quiz_question_contents_df = clean_raw_df['quiz_question_contents']
    for item in quiz_question_contents_df.to_dict(orient='records'):
        QuizQuestionContents.parse_obj(item)
    return quiz_question_contents_df


def questions_model(clean_raw_df, assessments_df):
    quiz_questions_df = clean_raw_df['quiz_questions']
    quiz_questions_df = pd.merge(
        quiz_questions_df, assessments_df, left_on='quiz_name', right_on='name'
    )
    quiz_questions_df.rename(columns={'id': 'assessment_id'}, inplace=True)
    quiz_questions_df = quiz_questions_df[
        ['assessment_id',
         'question_number',
         'question_id']
    ]
    for item in quiz_questions_df.to_dict(orient='records'):
        QuizQuestion.parse_obj(item)
    return quiz_questions_df


def courses_model(clean_raw_df):
    courses_df = clean_raw_df['courses']

    for item in courses_df.to_dict(orient='records'):
        Course.parse_obj(item)

    return courses_df


def enrollments_model(clean_raw_df):
    enrollments_df = clean_raw_df['enrollments']
    users_df = clean_raw_df['moodle_users'][['user_id', 'uuid']]
    enrollments_df = pd.merge(enrollments_df, users_df, on='user_id')
    enrollments_df.rename(columns={'uuid': 'user_uuid'}, inplace=True)
    enrollments_df = enrollments_df[['user_uuid', 'course_id', 'role']]

    for item in enrollments_df.to_dict(orient='records'):
        Enrollment.parse_obj(item)

    return enrollments_df


def users_model(clean_raw_df):
    users_df = clean_raw_df['moodle_users']
    users_df = users_df[['uuid', 'first_name', 'last_name', 'email']]

    for item in users_df.to_dict(orient='records'):
        User.parse_obj(item)

    return users_df


def assessments_and_grades_model(clean_raw_df):
    grades_df = clean_raw_df['grades']
    assessments_df = pd.DataFrame(
        grades_df['assessment_name'].unique(), columns=['name']
    )
    assessments_df['id'] = assessments_df.index
    grades_df = pd.merge(
        grades_df, assessments_df, left_on='assessment_name', right_on='name'
    )
    grades_df.rename(columns={'id': 'assessment_id'}, inplace=True)
    moodle_users = clean_raw_df['moodle_users'][['user_id', 'uuid']]
    grades_df = pd.merge(grades_df, moodle_users, on='user_id')
    grades_df.rename(columns={'uuid': 'user_uuid'}, inplace=True)
    grades_df = grades_df[
        ['assessment_id',
         'user_uuid',
         'course_id',
         'grade_percentage',
         'time_submitted'
         ]
    ]

    def convert_percentage(x):
        if x == '-':
            return None
        return float(x.strip("%"))

    grades_df['grade_percentage'] = grades_df['grade_percentage'].map(
        convert_percentage
    )
    grades_df = grades_df[grades_df['grade_percentage'].notnull()]
    grades_df['time_submitted'] = grades_df['time_submitted'].astype(int)

    for item in assessments_df.to_dict(orient='records'):
        Assessment.parse_obj(item)
    for item in grades_df.to_dict(orient='records'):
        Grade.parse_obj(item)

    return assessments_df, grades_df


def ib_input_model(clean_raw_df):
    ib_input_df = clean_raw_df['ib_input_instances']
    ib_input_df = ib_input_df[
                ['id',
                 'content_id',
                 'variant',
                 'content',
                 'prompt']]

    for item in ib_input_df.to_dict(orient='records'):
        InputInteractiveBlock.parse_obj(item)

    return ib_input_df


def ib_problem_model(clean_raw_df):
    ib_problem_df = clean_raw_df['ib_pset_problems']
    ib_problem_df = ib_problem_df[
                  ['id',
                   'content_id',
                   'variant',
                   'pset_id',
                   'content',
                   'problem_type',
                   'solution',
                   'solution_options']]

    for item in ib_problem_df.to_dict(orient='records'):
        ProblemSetProblem.parse_obj(item)

    return ib_problem_df


def course_contents_model(clean_raw_df):
    course_contents_df = clean_raw_df['course_contents']
    course_contents_df = course_contents_df[
                  ['section',
                   'activity_name',
                   'lesson_page',
                   'content_id']]

    for item in course_contents_df.to_dict(orient='records'):
        CourseContents.parse_obj(item)

    return course_contents_df


def quiz_attempts_and_multichoice_responses_model(
    clean_raw_df, assessments_df, quiz_multichoice_answers_df
):

    quiz_data = clean_raw_df['quiz_data']
    quiz_questions = clean_raw_df['quiz_questions']
    attempts_summary = clean_raw_df['attempts_summary']
    attempt_multichoice_response = clean_raw_df['attempt_multichoice_response']
    quiz_attempts_df = pd.merge(
        attempts_summary, quiz_data[['quiz_id', 'max_grade', 'quiz_name']],
        on='quiz_id'
    )
    users_df = clean_raw_df['moodle_users'][['user_id', 'uuid']]
    quiz_attempts_df = pd.merge(quiz_attempts_df, users_df, on='user_id')
    quiz_attempts_df.rename(columns={'uuid': 'user_uuid'}, inplace=True)
    quiz_attempts_df = pd.merge(
        quiz_attempts_df, assessments_df, left_on='quiz_name', right_on='name'
    )
    quiz_attempts_df.rename(columns={'id': 'assessment_id'}, inplace=True)
    quiz_attempts_df['id'] = quiz_attempts_df.index
    quiz_attempt_multichoice_responses_df = pd.merge(
        attempt_multichoice_response,
        quiz_attempts_df[['id', 'attempt_id']],
        on='attempt_id',
    )
    quiz_attempt_multichoice_responses_df.rename(
        columns={'attempt_id': 'moodle_attempt_id'}, inplace=True
    )
    quiz_attempt_multichoice_responses_df.rename(
        columns={'id': 'attempt_id'}, inplace=True
    )
    quiz_attempt_multichoice_responses_df = pd.merge(
        quiz_attempt_multichoice_responses_df,
        quiz_data[['quiz_id', 'quiz_name']],
        on='quiz_id',
    )
    quiz_attempt_multichoice_responses_df = pd.merge(
        quiz_attempt_multichoice_responses_df,
        quiz_questions,
        on=['quiz_name', 'question_number'],
    )
    quiz_attempt_multichoice_responses_df = pd.merge(
        quiz_attempt_multichoice_responses_df,
        quiz_multichoice_answers_df[['id', 'question_id', 'text']],
        left_on=['question_id', 'answer'],
        right_on=['question_id', 'text'],
    )
    quiz_attempt_multichoice_responses_df.rename(
        columns={'id': 'answer_id'}, inplace=True
    )
    quiz_attempts_df['grade_percentage'] = 100 * (
        quiz_attempts_df['attempt_grade'] / quiz_attempts_df['max_grade']
    )
    quiz_attempts_df = quiz_attempts_df[
        [
            'id',
            'assessment_id',
            'user_uuid',
            'course_id',
            'attempt_number',
            'grade_percentage',
            'time_started',
            'time_finished',
        ]
    ]

    quiz_attempt_multichoice_responses_df = \
        quiz_attempt_multichoice_responses_df[['attempt_id',
                                               'question_number',
                                               'question_id',
                                               'answer_id']]

    for item in quiz_attempts_df.to_dict(orient='records'):
        QuizAttempts.parse_obj(item)

    for item in quiz_attempt_multichoice_responses_df\
            .to_dict(orient='records'):
        QuizAttemptMultichoiceResponses.parse_obj(item)
    return quiz_attempts_df, quiz_attempt_multichoice_responses_df


def scrub_raw_dfs(all_raw_dfs):
    moodle_users_df = all_raw_dfs['moodle_users']

    moodle_users_df['email'] = moodle_users_df['email'].apply(
        lambda col: col.lower())

    grade_df = all_raw_dfs['grades']
    grade_df = grade_df[grade_df['assessment_name'].notnull()]

    all_raw_dfs['moodle_users'] = moodle_users_df
    all_raw_dfs['grades'] = grade_df
    return all_raw_dfs


def create_models(output_path, all_raw_dfs):

    clean_raw_df = scrub_raw_dfs(all_raw_dfs)

    assessments_df, grades_df = assessments_and_grades_model(clean_raw_df)
    users_df = users_model(clean_raw_df)
    enrollments_df = enrollments_model(clean_raw_df)
    courses_df = courses_model(clean_raw_df)
    quiz_questions_df = questions_model(clean_raw_df, assessments_df)
    quiz_question_contents_df = question_contents_model(clean_raw_df)
    quiz_multichoice_answers_df = multichoice_answer_model(clean_raw_df)
    ib_input_df = ib_input_model(clean_raw_df)
    ib_problem_df = ib_problem_model(clean_raw_df)
    course_contents_df = course_contents_model(clean_raw_df)
    (
        quiz_attempts_df,
        quiz_attempt_multichoice_responses_df,
    ) = quiz_attempts_and_multichoice_responses_model(
        clean_raw_df, assessments_df, quiz_multichoice_answers_df
    )

    with open(f"{output_path}/{MODEL_FILE_USERS}", "w") as f:
        users_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_FILE_GRADES}", "w") as f:
        grades_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_FILE_ENROLLMENTS}", "w") as f:
        enrollments_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_FILE_COURSES}", "w") as f:
        courses_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_FILE_ASSESSMENTS}", "w") as f:
        assessments_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_QUIZ_QUESTIONS}", "w") as f:
        quiz_questions_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_QUIZ_QUESTION_CONTENTS}", "w") as f:
        quiz_question_contents_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_MULTICHOICE_ANSWERS}", "w") as f:
        quiz_multichoice_answers_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_INPUT_INSTANCES}", "w") as f:
        ib_input_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_PSET_PROBLEMS}", "w") as f:
        ib_problem_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_COURSE_CONTENTS}", "w") as f:
        course_contents_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_QUIZ_ATTEMPTS}", "w") as f:
        quiz_attempts_df.to_csv(f, index=False)
    with open(
        f"{output_path}/{MODEL_QUIZ_ATTEMPT_MULTICHOICE_RESPONSES}", "w")\
            as f:
        quiz_attempt_multichoice_responses_df.to_csv(f, index=False)


def generate_grade_df(grade_dict):
    grade_data = []
    for course_id in grade_dict.keys():
        for user in grade_dict[course_id]['usergrades']:
            for grade in user['gradeitems']:
                grade_data.append({
                    'user_id': user['userid'],
                    'grade_percentage': grade['percentageformatted'],
                    'assessment_name': grade['itemname'],
                    'course_id': course_id,
                    'time_submitted': grade['gradedatesubmitted']
                })
    return pd.DataFrame(grade_data)


def generate_quiz_data_df(grade_dict):

    quiz_data = []
    for course_id in grade_dict.keys():
        for quiz in grade_dict[course_id]['quizzes']:
            quiz_data.append({
                'quiz_id': quiz['id'],
                'quiz_name': quiz['name'],
                'max_grade': quiz['sumgrades'],
                'course_id': quiz['course']
            })
    return pd.DataFrame(quiz_data)


def generate_attempts_summary_df(grade_dict):

    attempt_data = []
    for course_id in grade_dict.keys():
        for _, users in grade_dict[course_id]['attempts'].items():
            for _, quiz in users.items():
                for attempt_summary in quiz['summaries']:
                    attempt_data.append({
                        'course_id': course_id,
                        'user_id': attempt_summary['userid'],
                        'quiz_id': attempt_summary['quiz'],
                        'attempt_id': attempt_summary['id'],
                        'attempt_number': attempt_summary['attempt'],
                        'time_started': attempt_summary['timestart'],
                        'time_finished': attempt_summary['timefinish'],
                        'attempt_grade': attempt_summary['sumgrades']
                    })
    return pd.DataFrame(attempt_data)


def generate_attempt_multichoice_response_df(grade_dict):

    attempt_multichoice_response_data = []
    for course_id in grade_dict.keys():
        for _, users in grade_dict[course_id]['attempts'].items():
            for _, quiz in users.items():
                for _, attempt_detail in quiz['details'].items():
                    for question in attempt_detail['questions']:
                        for answer in question['answer']:
                            attempt_multichoice_response_data.append(
                                {
                                    'course_id': course_id,
                                    'user_id':
                                        attempt_detail['attempt']['userid'],
                                    'quiz_id':
                                        attempt_detail['attempt']['quiz'],
                                    'attempt_id':
                                        attempt_detail['attempt']['id'],
                                    'attempt_number':
                                        attempt_detail['attempt']['attempt'],
                                    'answer': answer,
                                    'question_number': question['slot'],
                                }
                            )
    return pd.DataFrame(attempt_multichoice_response_data)


def generate_enrollment_df(users_dict):
    enrollment_data = []
    for course_id in users_dict.keys():
        for user in users_dict[course_id]:
            enrollment_data.append({
                'user_id': user['id'],
                'course_id': course_id,
                'role': user['roles'][0]['shortname']
            })
    return pd.DataFrame(enrollment_data)


def generate_courses_df(users_dict):
    course_data = []
    for course_id in users_dict.keys():
        enrolled = users_dict[course_id][0]['enrolledcourses']
        for course in enrolled:
            if course['id'] == course_id:
                course_data.append({
                    'id': course['id'],
                    'name': course['fullname']
                    })
    return pd.DataFrame(course_data)


def generate_users_df(users_dict):
    user_data = []
    # Use email addresses to de-duplicate users
    seen_users = set()

    for course_id in users_dict.keys():
        for user in users_dict[course_id]:
            user_email = user['email']
            if user_email not in seen_users:
                seen_users.add(user_email)
                user_data.append({
                    "first_name": user['firstname'],
                    "last_name": user['lastname'],
                    "email": user_email,
                    "user_id": user['id'],
                    "uuid": user['uuid'] or uuid4()
                })
    return pd.DataFrame(user_data)


def collect_moodle_dfs(bucket, prefix):
    grades_dict, users_dict = {}, {}
    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator('list_objects')

    grade_data_iterator = paginator.paginate(
        Bucket=bucket,
        Prefix=f"{prefix}/moodle/grades"
    )
    users_data_iterator = paginator.paginate(
        Bucket=bucket,
        Prefix=f"{prefix}/moodle/users"
    )
    for page in grade_data_iterator:
        for data_object in page.get("Contents"):
            object_key = data_object.get("Key")
            course_id = object_key.split("/")[-1].split(".json")[0]
            data = s3_client.get_object(
                Bucket=bucket,
                Key=object_key
            )
            contents = data["Body"].read()
            grades_dict[int(course_id)] = json.loads(contents)

    for page in users_data_iterator:
        for data_object in page.get("Contents"):
            object_key = data_object.get("Key")
            course_id = object_key.split("/")[-1].split(".json")[0]
            data = s3_client.get_object(
                Bucket=bucket,
                Key=object_key
            )
            contents = data["Body"].read()
            users_dict[int(course_id)] = json.loads(contents)

    return {
        'moodle_users': generate_users_df(users_dict),
        'courses': generate_courses_df(users_dict),
        'enrollments': generate_enrollment_df(users_dict),
        'grades': generate_grade_df(grades_dict),
        'quiz_data': generate_quiz_data_df(grades_dict),
        'attempts_summary': generate_attempts_summary_df(grades_dict),
        'attempt_multichoice_response':
        generate_attempt_multichoice_response_df(
            grades_dict
        ),
    }


def collect_content_dfs(bucket, key):
    key_questions = key + "/content/quiz_questions.csv"
    key_question_contents = key + "/content/quiz_question_contents.csv"
    key_multichoice_answers = key + "/content/quiz_multichoice_answers.csv"
    key_ib_input_instances = key + "/content/ib_input_instances.csv"
    key_ib_pset_problems = key + "/content/ib_pset_problems.csv"
    key_course_contents = key + "/content/course_contents.csv"

    s3_client = boto3.client("s3")
    quiz_question_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_questions)
    quiz_question_contents_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_question_contents)
    quiz_multichoice_answers_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_multichoice_answers)
    ib_input_instances_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_ib_input_instances)
    ib_pset_problems_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_ib_pset_problems)
    course_contents_stream = s3_client.get_object(
        Bucket=bucket,
        Key=key_course_contents)

    quiz_question_data = pd.read_csv(
        BytesIO(quiz_question_stream["Body"].read())
    )
    quiz_question_contents_data = pd.read_csv(
        BytesIO(quiz_question_contents_stream["Body"].read())
    )
    quiz_multichoice_answers_data = pd.read_csv(
        BytesIO(quiz_multichoice_answers_stream["Body"].read()),
    )
    ib_input_instances_data = pd.read_csv(
        BytesIO(ib_input_instances_stream["Body"].read()),
    )
    ib_pset_problems_data = pd.read_csv(
        BytesIO(ib_pset_problems_stream["Body"].read()),
    )
    course_contents_data = pd.read_csv(
        BytesIO(course_contents_stream["Body"].read()),
    )

    return {"quiz_questions": quiz_question_data,
            "quiz_question_contents": quiz_question_contents_data,
            "quiz_multichoice_answers": quiz_multichoice_answers_data,
            "ib_input_instances": ib_input_instances_data,
            "ib_pset_problems": ib_pset_problems_data,
            "course_contents": course_contents_data
            }


def compile_models(data_bucket, data_key):
    moodle_dfs = collect_moodle_dfs(data_bucket, data_key)
    content_dfs = collect_content_dfs(data_bucket, data_key)
    all_raw_dfs = moodle_dfs | content_dfs
    return all_raw_dfs


def main():
    parser = argparse.ArgumentParser(description='Upload Resources to S3')
    parser.add_argument('data_bucket', type=str,
                        help='bucket for the moodle grade and user data dirs')
    parser.add_argument('data_prefix', type=str,
                        help='prefix for the moodle grade and user data dirs')
    args = parser.parse_args()

    output_path = os.environ["CSV_OUTPUT_DIR"]

    all_raw_dfs = compile_models(
        args.data_bucket,
        args.data_prefix)

    create_models(output_path, all_raw_dfs)


if __name__ == "__main__":  # pragma: no cover
    main()
