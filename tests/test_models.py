from enclave_mgmt.models import Grade, IBProblemAttempts
from pydantic import ValidationError
import pytest
from uuid import UUID


def test_invalid_grade():
    data = {
        "assessment_id": 1,
        "user_uuid": UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "course_id": 1,
        "grade_percentage": float('nan'),
        "time_submitted": 1630500000,
    }
    with pytest.raises(ValidationError, match="Grade value is nan"):
        Grade(**data)

    with pytest.raises(ValidationError,
                       match="Grade value -4.0 is out of expected range"):
        data["grade_percentage"] = float(-4)
        Grade(**data)


def test_invalid_response_type():
    data = {
        "user_uuid": UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "course_id": 1,
        "impression_id": UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "timestamp": 1630500000,
        "content_id": UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "pset_content_id": UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "pset_problem_content_id":
            UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
        "variant": "A",
        "problem_type": "multiselect",
        "response": "Option 1",  # Response should be a list
        "correct": True,
        "attempt": 1,
        "final_attempt": True,
    }
    with pytest.raises(ValidationError, match="Response must be a list"):
        IBProblemAttempts(**data)


def test_invalid_response_type_for_non_multiselect():
    data = {
        "user_uuid": UUID("123e4567-e89b-12d3-a456-426655440000"),
        "course_id": 1,
        "impression_id": UUID("123e4567-e89b-12d3-a456-426655440001"),
        "timestamp": 1630500000,
        "content_id": UUID("123e4567-e89b-12d3-a456-426655440002"),
        "pset_content_id": UUID("123e4567-e89b-12d3-a456-426655440003"),
        "pset_problem_content_id":
            UUID("123e4567-e89b-12d3-a456-426655440004"),
        "variant": "A",
        "problem_type": "multiplechoice",
        "response": ["Option 1", "Option 2"],  # Response should be a string
        "correct": True,
        "attempt": 1,
        "final_attempt": True,
    }
    with pytest.raises(ValidationError, match="Response must be a string"):
        IBProblemAttempts(**data)
