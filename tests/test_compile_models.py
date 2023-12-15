import boto3
from botocore.stub import Stubber
from enclave_mgmt import compile_models
import io
import json
import os
import csv
import pytest


@pytest.fixture
def stubber_setup(local_file_collections):
    (moodle_grades_2, moodle_users_2,
     moodle_grades_3, moodle_users_3,
        quiz_questions, quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems,
        course_contents,
        content_loads,
        ib_pset_problem_attempts,
        ib_input_submissions
     ) = local_file_collections

    s3_client = boto3.client('s3')
    stubber_client = Stubber(s3_client)

    data_bucket_name = "sample_bucket"
    data_key = "data_files"
    event_data_bucket_name = "sample_event_bucket"
    event_data_key = "event_data_files"

    grade_list = {"Contents": [{"Key": "2.json"}, {"Key": "3.json"}]}
    user_list = {"Contents": [{"Key": "2.json"}, {"Key": "3.json"}]}

    grades_data_2 = json.dumps(moodle_grades_2).encode('utf-8')
    grades_data_2_obj = {"Body": io.BytesIO(grades_data_2)}
    users_data_2 = json.dumps(moodle_users_2).encode('utf-8')
    users_data_2_obj = {"Body": io.BytesIO(users_data_2)}

    grades_data_3 = json.dumps(moodle_grades_3).encode('utf-8')
    grades_data_3_obj = {"Body": io.BytesIO(grades_data_3)}
    users_data_3 = json.dumps(moodle_users_3).encode('utf-8')
    users_data_3_obj = {"Body": io.BytesIO(users_data_3)}

    stubber_client.add_response(
        "list_objects", grade_list,
        expected_params={
            'Bucket': data_bucket_name,
            'Prefix': f"{data_key}/moodle/grades"
        })
    stubber_client.add_response(
        'get_object', grades_data_2_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '2.json'
        }
    )
    stubber_client.add_response(
        'get_object', grades_data_3_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '3.json'
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
        'get_object', users_data_2_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '2.json'
        }
    )
    stubber_client.add_response(
        'get_object', users_data_3_obj,
        expected_params={
            'Bucket': data_bucket_name,
            'Key': '3.json'
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

    body = io.BytesIO(content_loads.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': event_data_bucket_name,
            'Key': f"{event_data_key}/content_loaded_v1.json"
            }
        )

    body = io.BytesIO(ib_pset_problem_attempts.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': event_data_bucket_name,
            'Key': f"{event_data_key}/ib_pset_problem_attempted_v1.json"
            }
        )

    body = io.BytesIO(ib_input_submissions.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': event_data_bucket_name,
            'Key': f"{event_data_key}/ib_input_submitted_v1.json"
            }
        )

    return (
        s3_client,
        stubber_client,
        data_bucket_name,
        data_key,
        event_data_bucket_name,
        event_data_key
    )


def compare_results_against_expected_csvs(output_path, expected_csvs):
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
     expected_quiz_attempt_multichoice_responses,
     expected_content_loads,
     expected_ib_pset_problem_attempts,
     expected_ib_input_submissions
     ) = expected_csvs

    with open(output_path / "assessments.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_assignments)
        for i in expected_assignments:
            assert i in results

    with open(output_path / "users.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_users)
        for i in expected_users:
            assert i in results

    with open(output_path / "enrollments.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_enrollments)
        for i in expected_enrollments:
            assert i in results

    with open(output_path / "courses.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_courses)
        for i in expected_courses:
            assert i in results

    with open(output_path / "grades.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_grades)
        for i in expected_grades:
            assert i in results

    with open(output_path / "quiz_questions.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_quiz_questions)
        for i in expected_quiz_questions:
            assert i in results

    with open(output_path / "quiz_question_contents.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_quiz_question_contents)
        for i in expected_quiz_question_contents:
            assert i in results

    with open(output_path / "quiz_multichoice_answers.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_quiz_multichoice_answers)
        for i in expected_quiz_multichoice_answers:
            assert i in results

    with open(output_path / "ib_input_instances.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_ib_input_instances)
        for i in expected_ib_input_instances:
            assert i in results

    with open(output_path / "ib_pset_problems.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_ib_pset_problems)
        for i in expected_ib_pset_problems:
            assert i in results

    with open(output_path / "course_contents.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_course_contents)
        for i in expected_course_contents:
            assert i in results

    with open(output_path / "quiz_attempts.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_quiz_attempts)
        for i in expected_quiz_attempts:
            assert i in results

    with open(
        output_path / "quiz_attempt_multichoice_responses.csv", 'r'
    ) as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_quiz_attempt_multichoice_responses)
        for i in expected_quiz_attempt_multichoice_responses:
            assert i in results

    with open(output_path / "content_loads.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_content_loads)

        for i in expected_content_loads:
            assert i in results

    with open(output_path / "ib_pset_problem_attempts.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_ib_pset_problem_attempts)

        for i in expected_ib_pset_problem_attempts:
            assert i in results

    with open(output_path / "ib_input_submissions.csv", 'r') as f:
        results = list(csv.DictReader(f))
        assert len(results) == len(expected_ib_input_submissions)
        for i in expected_ib_input_submissions:
            assert i in results


def test_compile_models(
    mocker, tmp_path, autogenerated_user_uuid,
    local_expected_csvs, stubber_setup
):
    os.environ["CSV_OUTPUT_DIR"] = str(tmp_path)

    mocker.patch(
        "enclave_mgmt.collect_data.uuid4",
        lambda: autogenerated_user_uuid
    )

    (s3_client, stubber_client,
     data_bucket_name, data_key,
     event_data_bucket_name, event_data_key
     ) = stubber_setup

    stubber_client.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    mocker.patch(
        "sys.argv",
        ["", data_bucket_name, data_key, event_data_bucket_name,
         event_data_key]
    )
    compile_models.main()

    stubber_client.assert_no_pending_responses()

    compare_results_against_expected_csvs(tmp_path, local_expected_csvs)


def test_compile_models_filtered(
    mocker, tmp_path, autogenerated_user_uuid,
    local_expected_filtered_csvs, local_course_filter,
    stubber_setup
):
    os.environ["CSV_OUTPUT_DIR"] = str(tmp_path)

    mocker.patch(
        "enclave_mgmt.collect_data.uuid4",
        lambda: autogenerated_user_uuid
    )

    (s3_client, stubber_client,
     data_bucket_name, data_key,
     event_data_bucket_name, event_data_key
     ) = stubber_setup

    research_filter_bucket = "sample_filter_bucket"
    research_filter_key = "algebra1/ay2023/automation/courses.csv"

    body = io.BytesIO(local_course_filter.encode('utf-8'))
    stubber_client.add_response(
        'get_object', {"Body": body},
        expected_params={
            'Bucket': research_filter_bucket,
            'Key': research_filter_key
        }
    )

    stubber_client.activate()
    mocker.patch('boto3.client', lambda service: s3_client)

    mocker.patch(
        "sys.argv",
        ["", data_bucket_name, data_key, event_data_bucket_name,
         event_data_key, "--research_filter_bucket", research_filter_bucket,
         "--research_filter_prefix", research_filter_key]
    )
    compile_models.main()

    stubber_client.assert_no_pending_responses()

    compare_results_against_expected_csvs(
        tmp_path,
        local_expected_filtered_csvs
    )
