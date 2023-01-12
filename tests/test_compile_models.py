import boto3
from botocore.stub import Stubber
from enclave_mgmt import compile_models
from zipfile import ZipFile
import random as rd
import pytest
import io
import json
import os


@pytest.fixture
def local_file_collections():
    def _builder():
        with open("data/users.csv", "r") as f:
            or_users = f.read()
        with open("data/demographics.csv", 'r') as f:
            or_dems = f.read()
        with open("data/users.json", "r") as f:
            moodle_users = json.load(f)
        with open("data/grades.json", 'r') as f:
            moodle_grades = json.load(f)

        return or_users, or_dems, moodle_grades, moodle_users
    return _builder


def test_student_columns(mocker, tmp_path, local_file_collections):
    rd.seed(1)
    os.environ["CSV_OUTPUT_DIR"] = str(tmp_path)

    zip_bucket_name = "sample_bucket"
    zipfile_name = "one_roster.zip"
    zip_key = zip_bucket_name + "/" + zipfile_name

    or_users, or_dems, moodle_grades, moodle_users = local_file_collections()

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
    grade_list = {"Contents": [{"Key": "1"}]}
    user_list = {"Contents": [{"Key": "1"}]}

    stubber_client.add_response(
        "list_objects", grade_list,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Prefix': f"{moodle_key}/grades"
        })

    stubber_client.add_response(
        "list_objects", user_list,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Prefix': f"{moodle_key}/users"
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
            'Key': '1'
        }
    )
    stubber_client.add_response(
        'get_object', users_data_obj,
        expected_params={
            'Bucket': moodle_bucket_name,
            'Key': '1'
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

    with open(tmp_path / "assessments.csv", 'r') as f:
        file = f.read()
        assert file == \
            'name,id\n' +\
            '"Unit 1, Section A Quiz",0\n' +\
            '"Unit 1, Section B Quiz",1\n' +\
            '"Unit 1, Section C Quiz",2\n' +\
            'Unit 1 STAAR Review,3\n' +\
            'Unit 1 Quiz,4\n' +\
            '"Unit 2, Section A Quiz",5\n' +\
            '"Unit 2, Section B Quiz",6\n' +\
            '"Unit 2, Section C Quiz",7\n' +\
            '"Unit 2, Section D Quiz",8\n' +\
            'Unit 2 STAAR Review,9\n' +\
            'Unit 2 Quiz,10\n'

    with open(tmp_path / "users.csv", 'r') as f:
        file = f.read()
        assert file == \
            'uuid,first_name,last_name,email\n' +\
            'cd613e30-d8f1-6adf-91b7-584a2265b1f5,' +\
            'David,Tucci,davidtucci13431@gmail.us\n' +\
            '1e2feb89-414c-343c-1027-c4d1c386bbc4,' +\
            'Deann,James,deannjames121231@gmail.com\n' +\
            '78e51061-7311-d8a3-c2ce-6f447ed4d57b,Don,Castle,' +\
            'doncastle1234123@gmail.com\n' +\
            '35bf992d-c9e9-c616-612e-7696a6cecc1b,James,Stewart,' +\
            'jamesstewart1234121@gmail.com\n' +\
            'e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,Marguerite,Bell,' +\
            'margueritebell53245@gmail.com\n'

    with open(tmp_path / "enrollments.csv", 'r') as f:
        file = f.read()
        assert file == \
            'user_uuid,course_id,role\n' +\
            'cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,student\n' +\
            '1e2feb89-414c-343c-1027-c4d1c386bbc4,1,student\n' +\
            '78e51061-7311-d8a3-c2ce-6f447ed4d57b,1,teacher\n' +\
            '35bf992d-c9e9-c616-612e-7696a6cecc1b,1,student\n' +\
            'e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,student\n'

    with open(tmp_path / "oneroster_demographics.csv", 'r') as f:
        file = f.read()
        assert file == \
            'user_uuid,birth_date,sex,american_indian_or_alaska_native,' +\
            'asian,black_or_african_american,' +\
            'native_hawaiian_or_other_pacific_islander,' +\
            'white,demographic_race_two_or_more_races,' +\
            'hispanic_or_latino_ethnicity\n' +\
            'cd613e30-d8f1-6adf-91b7-584a2265b1f5,2007-11-29,' +\
            'male,false,false,false,false,true,false,false\n' +\
            '1e2feb89-414c-343c-1027-c4d1c386bbc4,2008-03-17,' +\
            'female,false,false,false,false,false,false,true\n' +\
            '35bf992d-c9e9-c616-612e-7696a6cecc1b,2007-12-20,' +\
            'male,false,false,true,false,false,false,false\n' +\
            'e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,2008-01-03,' +\
            'female,true,false,false,false,false,false,false\n'

    with open(tmp_path / "enrollments.csv", 'r') as f:
        file = f.read()
        assert file == \
            'user_uuid,course_id,role\n' +\
            'cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,student\n' +\
            '1e2feb89-414c-343c-1027-c4d1c386bbc4,1,student\n' +\
            '78e51061-7311-d8a3-c2ce-6f447ed4d57b,1,teacher\n' +\
            '35bf992d-c9e9-c616-612e-7696a6cecc1b,1,student\n' +\
            'e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,student\n'

    with open(tmp_path / "grades.csv", 'r') as f:
        file = f.read()
        assert file == \
            'assessment_id,user_uuid,course_id,' +\
            'grade_percentage,time_submitted\n' +\
            '0,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,0.0,1661272078\n' +\
            '1,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,80.0,1661272186\n' +\
            '4,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,75.0,1661272358\n' +\
            '5,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,40.0,1661272507\n' +\
            '6,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,20.0,1661272565\n' +\
            '7,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,20.0,1661272592\n' +\
            '8,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,25.0,1661272614\n' +\
            '9,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,10.0,1661272646\n' +\
            '10,e4b06ce6-0741-c7a8-7ce4-2c8218072e8c,1,50.0,1661272695\n' +\
            '0,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,0.0,1661273642\n' +\
            '1,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,60.0,1661273664\n' +\
            '3,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,20.0,1661273695\n' +\
            '5,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,20.0,1661273762\n' +\
            '6,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,20.0,1661273786\n' +\
            '7,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,20.0,1661273808\n' +\
            '8,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,50.0,1661273828\n' +\
            '9,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,30.0,1661273869\n' +\
            '10,cd613e30-d8f1-6adf-91b7-584a2265b1f5,1,50.0,1661273914\n' +\
            '1,35bf992d-c9e9-c616-612e-7696a6cecc1b,1,60.0,1661273350\n' +\
            '5,35bf992d-c9e9-c616-612e-7696a6cecc1b,1,40.0,1661273377\n' +\
            '6,35bf992d-c9e9-c616-612e-7696a6cecc1b,1,60.0,1661273406\n' +\
            '8,35bf992d-c9e9-c616-612e-7696a6cecc1b,1,50.0,1661273424\n' +\
            '10,35bf992d-c9e9-c616-612e-7696a6cecc1b,1,33.33,1661278562\n' +\
            '2,1e2feb89-414c-343c-1027-c4d1c386bbc4,1,60.0,1661273155\n' +\
            '5,1e2feb89-414c-343c-1027-c4d1c386bbc4,1,0.0,1661273195\n' +\
            '7,1e2feb89-414c-343c-1027-c4d1c386bbc4,1,20.0,1661273227\n'
