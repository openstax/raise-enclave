from enclave_mgmt import collect_data


def test_generate_grade_df_nodata():
    """generate_grade_df should return an empty dataframe when there no courses
    have students entrolled yet
    """
    grade_dict = {
        1: {
            'usergrades': []
        }
    }

    res = collect_data.generate_grade_df(grade_dict)
    expected_columns = [
        'user_id',
        'grade_percentage',
        'assessment_name',
        'course_id',
        'time_submitted'
    ]

    assert all(column in res.columns for column in expected_columns)


def test_generate_attempts_summary_df_nodata():
    """generate_attempts_summary_df should return an empty dataframe when no
    quiz attempts have been made yet
    """
    grade_dict = {
        1: {
            'attempts': {}
        }
    }

    res = collect_data.generate_attempts_summary_df(grade_dict)
    expected_columns = [
        'course_id',
        'user_id',
        'quiz_id',
        'attempt_id',
        'attempt_number',
        'time_started',
        'time_finished',
        'attempt_grade'
    ]

    assert all(column in res.columns for column in expected_columns)


def test_generate_attempt_multichoice_response_df_nodata():
    """generate_attempt_multichoice_response_df should return an empty
    dataframe when no quiz attempts have been made yet
    """

    grade_dict = {
        1: {
            'attempts': {}
        }
    }

    res = collect_data.generate_attempt_multichoice_response_df(grade_dict)
    expected_columns = [
        'course_id',
        'user_id',
        'quiz_id',
        'attempt_id',
        'attempt_number',
        'answer',
        'question_number'
    ]

    assert all(column in res.columns for column in expected_columns)
