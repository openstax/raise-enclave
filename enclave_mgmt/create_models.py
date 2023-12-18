import pandas as pd
from enclave_mgmt.models import (
    Assessment, ContentLoads, Course, CourseContents, Grade,
    User, QuizMultichoiceAnswer, QuizQuestion,
    QuizQuestionContents, Enrollment,
    InputInteractiveBlock, ProblemSetProblem,
    IBProblemAttempts, IBInputSubmissions,
    QuizAttempts, QuizAttemptMultichoiceResponses
)

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
MODEL_CONTENT_LOADS = "content_loads.csv"
MODEL_IB_PSET_PROBLEM_ATTEMPTS = "ib_pset_problem_attempts.csv"
MODEL_IB_INPUT_SUBMISSIONS = "ib_input_submissions.csv"


def create_models(output_path, all_raw_dfs, research_filter_df=None):

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
    content_loads_df = content_loads_model(clean_raw_df)
    ib_pset_problem_attempts_df = ib_pset_problem_attempts_model(clean_raw_df)
    ib_input_submissions_df = ib_input_submissions_model(clean_raw_df)

    (
        quiz_attempts_df,
        quiz_attempt_multichoice_responses_df,
    ) = quiz_attempts_and_multichoice_responses_model(
        clean_raw_df, assessments_df, quiz_multichoice_answers_df
    )

    if research_filter_df is not None:
        enrollments_df = filter_dataframes_by_course_id(
            research_filter_df, enrollments_df
        )
        grades_df = filter_dataframes_by_course_id(
            research_filter_df, grades_df
        )
        content_loads_df = filter_dataframes_by_course_id(
            research_filter_df, content_loads_df
        )
        ib_input_submissions_df = filter_dataframes_by_course_id(
            research_filter_df, ib_input_submissions_df
        )
        ib_pset_problem_attempts_df = filter_dataframes_by_course_id(
            research_filter_df, ib_pset_problem_attempts_df
        )
        quiz_attempts_df = filter_dataframes_by_course_id(
            research_filter_df, quiz_attempts_df
        )
        users_df = drop_duplicate_users(enrollments_df, users_df)
        courses_df = pd.merge(
            research_filter_df, courses_df,
            left_on='course_id', right_on='id'
        )
        courses_df = courses_df[
            ['id',
             'name']
        ]
        quiz_attempt_multichoice_responses_df = pd.merge(
            quiz_attempts_df, quiz_attempt_multichoice_responses_df,
            left_on='id', right_on='attempt_id'
        )
        quiz_attempt_multichoice_responses_df = (
            quiz_attempt_multichoice_responses_df[
                ['attempt_id',
                 'question_number',
                 'question_id',
                 'answer_id']
            ])

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
    with open(f"{output_path}/{MODEL_CONTENT_LOADS}", "w") as f:
        content_loads_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_IB_PSET_PROBLEM_ATTEMPTS}", "w") as f:
        ib_pset_problem_attempts_df.to_csv(f, index=False)
    with open(f"{output_path}/{MODEL_IB_INPUT_SUBMISSIONS}", "w") as f:
        ib_input_submissions_df.to_csv(f, index=False)


def scrub_raw_dfs(all_raw_dfs):
    moodle_users_df = all_raw_dfs['moodle_users']

    moodle_users_df['email'] = moodle_users_df['email'].apply(
        lambda col: col.lower())

    grade_df = all_raw_dfs['grades']
    grade_df = grade_df[grade_df['assessment_name'].notnull()]

    all_raw_dfs['moodle_users'] = moodle_users_df
    all_raw_dfs['grades'] = grade_df
    return all_raw_dfs


def multichoice_answer_model(clean_raw_df):
    quiz_multichoice_answer_df = clean_raw_df['quiz_multichoice_answers']
    quiz_multichoice_answer_df.insert(
        0, 'id', quiz_multichoice_answer_df.index
    )
    for item in quiz_multichoice_answer_df.to_dict(orient='records'):
        QuizMultichoiceAnswer.model_validate(item)
    return quiz_multichoice_answer_df


def question_contents_model(clean_raw_df):
    quiz_question_contents_df = clean_raw_df['quiz_question_contents']
    for item in quiz_question_contents_df.to_dict(orient='records'):
        QuizQuestionContents.model_validate(item)
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
        QuizQuestion.model_validate(item)
    return quiz_questions_df


def courses_model(clean_raw_df):
    courses_df = clean_raw_df['courses']

    for item in courses_df.to_dict(orient='records'):
        Course.model_validate(item)

    return courses_df


def enrollments_model(clean_raw_df):
    enrollments_df = clean_raw_df['enrollments']
    users_df = clean_raw_df['moodle_users'][['user_id', 'uuid']]
    enrollments_df = pd.merge(enrollments_df, users_df, on='user_id')
    enrollments_df.rename(columns={'uuid': 'user_uuid'}, inplace=True)
    enrollments_df = enrollments_df[['user_uuid', 'course_id', 'role']]

    for item in enrollments_df.to_dict(orient='records'):
        Enrollment.model_validate(item)

    return enrollments_df


def users_model(clean_raw_df):
    users_df = clean_raw_df['moodle_users']
    users_df = users_df[['uuid', 'first_name', 'last_name', 'email']]

    for item in users_df.to_dict(orient='records'):
        User.model_validate(item)

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
        Assessment.model_validate(item)
    for item in grades_df.to_dict(orient='records'):
        Grade.model_validate(item)
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
        InputInteractiveBlock.model_validate(item)

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
        ProblemSetProblem.model_validate(item)

    return ib_problem_df


def course_contents_model(clean_raw_df):
    course_contents_df = clean_raw_df['course_contents']
    course_contents_df = course_contents_df[
                  ['section',
                   'activity_name',
                   'lesson_page',
                   'content_id',
                   ]]

    for item in course_contents_df.to_dict(orient='records'):
        CourseContents.model_validate(item)

    return course_contents_df


def filter_events(event_df, clean_raw_df):
    enrollments_df = clean_raw_df['enrollments']
    users_df = clean_raw_df['moodle_users'][['user_id', 'uuid']]
    enrollments_df = pd.merge(enrollments_df, users_df, on='user_id')
    enrollments_df.rename(columns={'uuid': 'user_uuid'}, inplace=True)
    filter_df = enrollments_df[['user_uuid', 'course_id']]
    event_df = pd.merge(event_df, filter_df,
                        on=['user_uuid', 'course_id'])
    return event_df


def content_loads_model(clean_raw_df):
    content_loads_df = clean_raw_df['content_loads']
    content_loads_df = content_loads_df[
                    ['user_uuid',
                     'course_id',
                     'impression_id',
                     'timestamp',
                     'content_id',
                     'variant']]

    content_loads_df = filter_events(content_loads_df, clean_raw_df)

    for item in content_loads_df.to_dict(orient='records'):
        ContentLoads.model_validate(item)

    return content_loads_df


def ib_input_submissions_model(clean_raw_df):
    ib_input_submissions_df = clean_raw_df['ib_input_submissions']
    ib_input_submissions_df = ib_input_submissions_df[
                    ['user_uuid',
                     'course_id',
                     'impression_id',
                     'timestamp',
                     'content_id',
                     'input_content_id',
                     'variant',
                     'response']]

    ib_input_submissions_df = filter_events(ib_input_submissions_df,
                                            clean_raw_df)

    for item in ib_input_submissions_df.to_dict(orient='records'):
        IBInputSubmissions.model_validate(item)

    return ib_input_submissions_df


def ib_pset_problem_attempts_model(clean_raw_df):
    ib_pset_problem_attempts_df = clean_raw_df['ib_pset_problem_attempts']
    ib_pset_problem_attempts_df = ib_pset_problem_attempts_df[
                    ['user_uuid',
                     'course_id',
                     'impression_id',
                     'timestamp',
                     'content_id',
                     'pset_content_id',
                     'pset_problem_content_id',
                     'variant',
                     'problem_type',
                     'response',
                     'correct',
                     'attempt',
                     'final_attempt']]

    ib_pset_problem_attempts_df = filter_events(ib_pset_problem_attempts_df,
                                                clean_raw_df)

    for item in ib_pset_problem_attempts_df.to_dict(orient='records'):
        IBProblemAttempts.model_validate(item)

    return ib_pset_problem_attempts_df


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
        QuizAttempts.model_validate(item)

    for item in quiz_attempt_multichoice_responses_df\
            .to_dict(orient='records'):
        QuizAttemptMultichoiceResponses.model_validate(item)
    return quiz_attempts_df, quiz_attempt_multichoice_responses_df


def filter_dataframes_by_course_id(research_filter_df, unfiltered_df):
    filtered_df = pd.merge(
        research_filter_df, unfiltered_df, on='course_id'
    )
    return filtered_df


def drop_duplicate_users(enrollments_df, users_df):
    filtered_users_df = pd.merge(
            enrollments_df['user_uuid'].drop_duplicates(),
            users_df,
            left_on='user_uuid',
            right_on='uuid'
        )

    filtered_users_df = filtered_users_df[
            ['uuid',
             'first_name',
             'last_name',
             'email']
        ]
    return filtered_users_df
