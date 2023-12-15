from pathlib import Path
from uuid import UUID
import pytest
import json
import csv


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data"


@pytest.fixture
def local_file_collections(test_data_path):
    with open(test_data_path / "users_2.json", "r") as f:
        moodle_users_2 = json.load(f)
    with open(test_data_path / "grades_2.json", 'r') as f:
        moodle_grades_2 = json.load(f)
    with open(test_data_path / "users_3.json", "r") as f:
        moodle_users_3 = json.load(f)
    with open(test_data_path / "grades_3.json", 'r') as f:
        moodle_grades_3 = json.load(f)
    with open(test_data_path / "quiz_questions.csv", 'r') as f:
        quiz_questions = f.read()
    with open(test_data_path / "quiz_question_contents.csv", 'r') as f:
        quiz_question_contents = f.read()
    with open(test_data_path / "quiz_multichoice_answers.csv", 'r') as f:
        quiz_multichoice_answers = f.read()
    with open(test_data_path / "ib_input_instances.csv", 'r') as f:
        ib_input_instances = f.read()
    with open(test_data_path / "ib_pset_problems.csv", 'r') as f:
        ib_pset_problems = f.read()
    with open(test_data_path / "course_contents.csv", 'r') as f:
        course_contents = f.read()
    with open(test_data_path / "content_loaded_v1.json", 'r') as f:
        content_loads = f.read()
    with open(test_data_path / "ib_pset_problem_attempted_v1.json", 'r') as f:
        ib_pset_problem_attempts = f.read()
    with open(test_data_path / "ib_input_submitted_v1.json", 'r') as f:
        ib_input_submissions = f.read()

    return (
        moodle_grades_2,
        moodle_users_2,
        moodle_grades_3,
        moodle_users_3,
        quiz_questions,
        quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems,
        course_contents,
        content_loads,
        ib_pset_problem_attempts,
        ib_input_submissions
    )


@pytest.fixture
def local_expected_csvs(test_data_path):
    with open(test_data_path / "expected/assessments.csv", "r") as f:
        assessments = list(csv.DictReader(f))
    with open(test_data_path / "expected/users.csv", 'r') as f:
        users = list(csv.DictReader(f))
    with open(test_data_path / "expected/grades.csv", "r") as f:
        grades = list(csv.DictReader(f))
    with open(test_data_path / "expected/enrollments.csv", 'r') as f:
        enrolments = list(csv.DictReader(f))
    with open(test_data_path / "expected/courses.csv", 'r') as f:
        courses = list(csv.DictReader(f))
    with open(test_data_path / "expected/quiz_questions.csv", 'r') as f:
        quiz_questions = list(csv.DictReader(f))
    with open(
        test_data_path / "expected/quiz_question_contents.csv", 'r'
    ) as f:
        quiz_question_contents = list(csv.DictReader(f))
    with open(
        test_data_path / "expected/quiz_multichoice_answers.csv", 'r'
    ) as f:
        quiz_multichoice_answers = list(csv.DictReader(f))
    with open(test_data_path / "expected/ib_input_instances.csv", 'r') as f:
        ib_input_instances = list(csv.DictReader(f))
    with open(test_data_path / "expected/ib_pset_problems.csv", 'r') as f:
        ib_pset_problems = list(csv.DictReader(f))
    with open(test_data_path / "expected/course_contents.csv", 'r') as f:
        course_contents = list(csv.DictReader(f))
    with open(test_data_path / "expected/quiz_attempts.csv", 'r') as f:
        quiz_attempts = list(csv.DictReader(f))
    with open(test_data_path /
              "expected/quiz_attempt_multichoice_responses.csv", 'r') as f:
        quiz_attempt_multichoice_responses = list(csv.DictReader(f))
    with open(test_data_path / "expected/content_loads.csv", 'r') as f:
        content_loads = list(csv.DictReader(f))
    with open(test_data_path / "expected/ib_pset_problem_attempts.csv", 'r')\
            as f:
        ib_pset_problem_attempts = list(csv.DictReader(f))
    with open(test_data_path / "expected/ib_input_submissions.csv", 'r') as f:
        ib_input_submissions = list(csv.DictReader(f))
    return (
        assessments,
        users,
        grades,
        enrolments,
        courses,
        quiz_questions,
        quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems,
        course_contents,
        quiz_attempts,
        quiz_attempt_multichoice_responses,
        content_loads,
        ib_pset_problem_attempts,
        ib_input_submissions
    )


@pytest.fixture
def local_expected_filtered_csvs(test_data_path):
    with open(test_data_path / "expected_filtered/assessments.csv", "r") as f:
        assessments = list(csv.DictReader(f))
    with open(test_data_path / "expected_filtered/users.csv", 'r') as f:
        users = list(csv.DictReader(f))
    with open(test_data_path / "expected_filtered/grades.csv", "r") as f:
        grades = list(csv.DictReader(f))
    with open(test_data_path / "expected_filtered/enrollments.csv", 'r') as f:
        enrolments = list(csv.DictReader(f))
    with open(test_data_path / "expected_filtered/courses.csv", 'r') as f:
        courses = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/quiz_questions.csv", 'r'
    ) as f:
        quiz_questions = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/quiz_question_contents.csv", 'r'
    ) as f:
        quiz_question_contents = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/quiz_multichoice_answers.csv", 'r'
    ) as f:
        quiz_multichoice_answers = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/ib_input_instances.csv", 'r'
    ) as f:
        ib_input_instances = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/ib_pset_problems.csv", 'r'
    ) as f:
        ib_pset_problems = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/course_contents.csv", 'r'
    ) as f:
        course_contents = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/quiz_attempts.csv", 'r'
    ) as f:
        quiz_attempts = list(csv.DictReader(f))
    with open(
        test_data_path /
        "expected_filtered/quiz_attempt_multichoice_responses.csv", 'r'
    ) as f:
        quiz_attempt_multichoice_responses = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/content_loads.csv", 'r'
    ) as f:
        content_loads = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/ib_pset_problem_attempts.csv", 'r'
    ) as f:
        ib_pset_problem_attempts = list(csv.DictReader(f))
    with open(
        test_data_path / "expected_filtered/ib_input_submissions.csv", 'r'
    ) as f:
        ib_input_submissions = list(csv.DictReader(f))
    return (
        assessments,
        users,
        grades,
        enrolments,
        courses,
        quiz_questions,
        quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems,
        course_contents,
        quiz_attempts,
        quiz_attempt_multichoice_responses,
        content_loads,
        ib_pset_problem_attempts,
        ib_input_submissions
    )


@pytest.fixture
def autogenerated_user_uuid():
    return UUID("7080c78d-298b-40ba-a68d-55d6a93b00fb")


@pytest.fixture
def local_course_filter(test_data_path):
    with open(test_data_path / "courses.csv", "r") as f:
        courses = f.read()
    return courses
