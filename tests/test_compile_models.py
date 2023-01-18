import boto3
from botocore.stub import Stubber
from enclave_mgmt import compile_models
from zipfile import ZipFile
import io
import json
import os


def test_compile_models(
    mocker, tmp_path, local_file_collections,
    autogenerated_user_uuid, local_expected_csvs
):
    os.environ["CSV_OUTPUT_DIR"] = str(tmp_path)

    mocker.patch(
        "enclave_mgmt.compile_models.uuid4",
        lambda: autogenerated_user_uuid
    )

    zip_bucket_name = "sample_bucket"
    zipfile_name = "one_roster.zip"
    zip_key = zip_bucket_name + "/" + zipfile_name

    (or_users, or_dems, moodle_grades, moodle_users,
        quiz_questions, quiz_question_contents,
        quiz_multichoice_answers) = local_file_collections

    zip_data = io.BytesIO()
    with ZipFile(zip_data, 'w') as f:
        f.writestr("users.csv", or_users)
        f.writestr('demographics.csv', or_dems)
    zip_data.seek(0)

    s3_client = boto3.client('s3')
    stubber_client = Stubber(s3_client)
    stubber_client.add_response(
        'get_object', {"Body": zip_data},
        expected_params={
            'Bucket': zip_bucket_name,
            'Key': zip_key
            }
        )

    moodle_bucket_name = "sample_bucket"
    moodle_key = "moodle_files"
    grade_list = {"Contents": [{"Key": "2"}]}
    user_list = {"Contents": [{"Key": "2"}]}
    stubber_client.add_response(
        "list_objects", grade_list,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Prefix': f"{moodle_key}/moodle/grades"
        })
    stubber_client.add_response(
        "list_objects", user_list,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Prefix': f"{moodle_key}/moodle/users"
        }
    )

    grades_data = json.dumps(moodle_grades).encode('utf-8')
    grades_data_obj = {"Body": io.BytesIO(grades_data)}
    users_data = json.dumps(moodle_users).encode('utf-8')
    users_data_obj = {"Body": io.BytesIO(users_data)}
    stubber_client.add_response(
        'get_object', grades_data_obj,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': '2'
        }
    )
    stubber_client.add_response(
        'get_object', users_data_obj,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': '2'
        }
    )

    body = io.BytesIO(quiz_questions.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': f"{moodle_key}/contents/quiz_questions.csv"
            }
        )

    body = io.BytesIO(quiz_question_contents.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': f"{moodle_key}/contents/quiz_question_contents.csv"
            }
        )

    body = io.BytesIO(quiz_multichoice_answers.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': f"{moodle_key}/contents/quiz_multichoice_answers.csv"
            }
        )

    stubber_client.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    mocker.patch(
        "sys.argv",
        ["", moodle_bucket_name, moodle_key, zip_bucket_name, zip_key]
    )
    compile_models.main()

    stubber_client.assert_no_pending_responses()

    (expected_assignments,
     expected_users,
     expected_grades,
     expected_enrollments,
     expected_or_demographics,
     expected_courses,
     expected_quiz_questions,
     expected_quiz_question_contents,
     expected_quiz_multichoice_answers) = local_expected_csvs

    with open(tmp_path / "assessments.csv", 'r') as f:
        results = f.readlines()
        for i in expected_assignments:
            assert i in results

    with open(tmp_path / "users.csv", 'r') as f:
        results = f.readlines()
        for i in expected_users:
            assert i in results

    with open(tmp_path / "enrollments.csv", 'r') as f:
        results = f.readlines()
        for i in expected_enrollments:
            assert i in results

    with open(tmp_path / "oneroster_demographics.csv", 'r') as f:
        results = f.readlines()
        for i in expected_or_demographics:
            assert i in results

    with open(tmp_path / "courses.csv", 'r') as f:
        results = f.readlines()
        for i in expected_courses:
            assert i in results

    with open(tmp_path / "grades.csv", 'r') as f:
        results = f.readlines()
        for i in expected_grades:
            assert i in results

    with open(tmp_path / "quiz_questions.csv", 'r') as f:
        results = f.readlines()
        for i in expected_quiz_questions:
            assert i in results

    with open(tmp_path / "quiz_question_contents.csv", 'r') as f:
        results = f.readlines()
        for i in expected_quiz_question_contents:
            assert i in results

    with open(tmp_path / "quiz_multichoice_answers.csv", 'r') as f:
        results = f.readlines()
        for i in expected_quiz_multichoice_answers:
            assert i in results
