import json
import boto3
import pandas as pd
from io import BytesIO
from uuid import uuid4


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


def collect_event_data_dfs(events_bucket, events_key):

    key_content_loads = events_key + "/content_loaded_v1.json"
    key_ib_pset_problem_attempts = \
        events_key + "/ib_pset_problem_attempted_v1.json"
    key_ib_input_submissions = events_key + "/ib_input_submitted_v1.json"

    s3_client = boto3.client("s3")

    content_loads_stream = s3_client.get_object(
        Bucket=events_bucket,
        Key=key_content_loads)
    ib_pset_problem_attempts_stream = s3_client.get_object(
        Bucket=events_bucket,
        Key=key_ib_pset_problem_attempts)
    ib_input_submissions_stream = s3_client.get_object(
        Bucket=events_bucket,
        Key=key_ib_input_submissions)

    content_loads_data = pd.DataFrame(
        json.loads(content_loads_stream["Body"].read())['data']
    )

    # Normalize union type for pset attempt response
    ib_pset_problem_attempts_json = json.loads(
        ib_pset_problem_attempts_stream["Body"].read()
    )['data']
    ib_pset_problem_attempts_normalized = []
    for item in ib_pset_problem_attempts_json:
        item["response"] = \
            item["response"]["string"] or item["response"]["array"]
        ib_pset_problem_attempts_normalized.append(item)
    ib_pset_problem_attempts_data = pd.DataFrame(
        ib_pset_problem_attempts_normalized
    )

    ib_input_submissions_data = pd.DataFrame(
        json.loads(ib_input_submissions_stream["Body"].read())['data']
    )

    return {
        "content_loads": content_loads_data,
        "ib_pset_problem_attempts": ib_pset_problem_attempts_data,
        "ib_input_submissions": ib_input_submissions_data
    }


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
    if len(grade_data) != 0:
        return pd.DataFrame(grade_data)
    else:
        return pd.DataFrame(
            columns=[
                'user_id',
                'grade_percentage',
                'assessment_name',
                'course_id',
                'time_submitted'
            ]
        )


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
    if len(attempt_data) != 0:
        return pd.DataFrame(attempt_data)
    else:
        return pd.DataFrame(
            columns=[
                'course_id',
                'user_id',
                'quiz_id',
                'attempt_id',
                'attempt_number',
                'time_started',
                'time_finished',
                'attempt_grade'
            ]
        )


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
    if len(attempt_multichoice_response_data) != 0:
        return pd.DataFrame(attempt_multichoice_response_data)
    else:
        return pd.DataFrame(
            columns=[
                'course_id',
                'user_id',
                'quiz_id',
                'attempt_id',
                'attempt_number',
                'answer',
                'question_number'
            ]
        )


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
