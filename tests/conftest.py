from pathlib import Path
from uuid import UUID
import pytest
import json


@pytest.fixture
def test_data_path():
    return Path(__file__).parent / "data"


@pytest.fixture
def local_file_collections(test_data_path):
    with open(test_data_path / "users.json", "r") as f:
        moodle_users = json.load(f)
    with open(test_data_path / "grades.json", 'r') as f:
        moodle_grades = json.load(f)
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
    return (
        moodle_grades,
        moodle_users,
        quiz_questions,
        quiz_question_contents,
        quiz_multichoice_answers,
        ib_input_instances,
        ib_pset_problems
    )


@pytest.fixture
def local_expected_csvs(test_data_path):
    with open(test_data_path / "expected/assessments.csv", "r") as f:
        assessments = f.readlines()
    with open(test_data_path / "expected/users.csv", 'r') as f:
        users = f.readlines()
    with open(test_data_path / "expected/grades.csv", "r") as f:
        grades = f.readlines()
    with open(test_data_path / "expected/enrollments.csv", 'r') as f:
        enrolments = f.readlines()
    with open(test_data_path / "expected/courses.csv", 'r') as f:
        courses = f.readlines()
    with open(test_data_path / "expected/quiz_questions.csv", 'r') as f:
        quiz_questions = f.readlines()
    with open(
        test_data_path / "expected/quiz_question_contents.csv", 'r'
    ) as f:
        quiz_question_contents = f.readlines()
    with open(
        test_data_path / "expected/quiz_multichoice_answers.csv", 'r'
    ) as f:
        quiz_multichoice_answers = f.readlines()
    with open(test_data_path / "expected/ib_input_instances.csv", 'r') as f:
        ib_input_instances = f.read()
    with open(test_data_path / "expected/ib_pset_problems.csv", 'r') as f:
        ib_pset_problems = f.read()
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
        ib_pset_problems
    )


@pytest.fixture
def autogenerated_user_uuid():
    return UUID("7080c78d-298b-40ba-a68d-55d6a93b00fb")
