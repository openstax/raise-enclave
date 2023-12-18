from enclave_mgmt import create_models
from uuid import UUID
import pandas as pd


def test_duplicate_user_uuid():
    """drop_duplicate_users should return an a dataframe without duplicate
    user_uuids when the optional filter flags are applied to compile-models
    """
    enrollments_data = {
        'user_uuid': [UUID("3c2ab175-f9b9-42b5-9857-9fd789914a7c"),
                      UUID("123e4567-e89b-12d3-a456-426655440000")],
        'course_id': [1, 2],
        'role': ['student', 'student']
    }
    users_data = {
        'uuid': [UUID("123e4567-e89b-12d3-a456-426655440000")],
        'first_name': ['Tony'],
        'last_name': ['Soprano'],
        'email': ['tsoprano@gabagool.com']
    }
    enrollments_df = pd.DataFrame(data=enrollments_data)
    users_df = pd.DataFrame(users_data)

    res = create_models.drop_duplicate_users(enrollments_df, users_df)
    expected_data = {
        'uuid': [UUID("123e4567-e89b-12d3-a456-426655440000")],
        'first_name': ['Tony'],
        'last_name': ['Soprano'],
        'email': ['tsoprano@gabagool.com']
    }
    expected_df = pd.DataFrame(expected_data)

    assert res.equals(expected_df)
