import boto3
from botocore.stub import Stubber
from enclave_mgmt import compile_models
import io
import json
import os
import csv


def test_compile_models(
    mocker, tmp_path, local_file_collections,
    autogenerated_user_uuid, local_expected_csvs
):
    os.environ["CSV_OUTPUT_DIR"] = str(tmp_path)

    mocker.patch(
        "enclave_mgmt.compile_models.uuid4",
        lambda: autogenerated_user_uuid
    )

    (moodle_grades, moodle_users,
        quiz_questions, quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems,
        course_contents) = local_file_collections

    s3_client = boto3.client('s3')
    stubber_client = Stubber(s3_client)

    data_bucket_name = "sample_bucket"
    data_key = "data_files"
    grade_list = {"Contents": [{"Key": "2"}]}
    user_list = {"Contents": [{"Key": "2"}]}

    grades_data = json.dumps(moodle_grades).encode('utf-8')
    grades_data_obj = {"Body": io.BytesIO(grades_data)}
    users_data = json.dumps(moodle_users).encode('utf-8')
    users_data_obj = {"Body": io.BytesIO(users_data)}

    stubber_client.add_response(
        "list_objects", grade_list,
        expected_params={
            'Bucket': data_bucket_name,
            'Prefix': f"{data_key}/moodle/grades"
        })
    stubber_client.add_response(
        'get_object', grades_data_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '2'
        }
    )
    stubber_client.add_response(
        "list_objects", user_list,
        expected_params={
            'Bucket': data_bucket_name,
            'Prefix': f"{data_key}/moodle/users"
        }
    )
    stubber_client.add_response(
        'get_object', users_data_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '2'
        }
    )

    body = io.BytesIO(quiz_questions.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/quiz_questions.csv"
            }
        )

    body = io.BytesIO(quiz_question_contents.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/quiz_question_contents.csv"
            }
        )

    body = io.BytesIO(quiz_multichoice_answers.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/quiz_multichoice_answers.csv"
            }
        )

    body = io.BytesIO(ib_input_instances.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/ib_input_instances.csv"
            }
        )

    body = io.BytesIO(ib_pset_problems.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/ib_pset_problems.csv"
            }
        )

    body = io.BytesIO(course_contents.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': data_bucket_name,
            'Key': f"{data_key}/content/course_contents.csv"
            }
        )

    stubber_client.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    mocker.patch(
        "sys.argv",
        ["", data_bucket_name, data_key]
    )
    compile_models.main()

    stubber_client.assert_no_pending_responses()

    (expected_assignments,
     expected_users,
     expected_grades,
     expected_enrollments,
     expected_courses,
     expected_quiz_questions,
     expected_quiz_question_contents,
     expected_quiz_multichoice_answers,
     expected_ib_input_instances,
     expected_ib_pset_problems,
     expected_course_contents,
     expected_quiz_attempts,
     expected_quiz_attempt_multichoice_responses) = local_expected_csvs

    with open(tmp_path / "assessments.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_assignments:
            assert i in results

    with open(tmp_path / "users.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_users:
            assert i in results

    with open(tmp_path / "enrollments.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_enrollments:
            assert i in results

    with open(tmp_path / "courses.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_courses:
            assert i in results

    with open(tmp_path / "grades.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_grades:
            assert i in results

    with open(tmp_path / "quiz_questions.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_quiz_questions:
            assert i in results

    with open(tmp_path / "quiz_question_contents.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_quiz_question_contents:
            assert i in results

    with open(tmp_path / "quiz_multichoice_answers.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_quiz_multichoice_answers:
            assert i in results

    with open(tmp_path / "ib_input_instances.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_ib_input_instances:
            assert i in results

    with open(tmp_path / "ib_pset_problems.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_ib_pset_problems:
            assert i in results

    with open(tmp_path / "course_contents.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_course_contents:
            assert i in results

    with open(tmp_path / "quiz_attempts.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_quiz_attempts:
            assert i in results

    with open(tmp_path / "quiz_attempt_multichoice_responses.csv", 'r') as f:
        results = list(csv.DictReader(f))
        for i in expected_quiz_attempt_multichoice_responses:
            assert i in results
