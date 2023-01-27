from enclave_mgmt import create_workflow
import yaml


def test_compile_workflow():

    create_workflow.create_workflow('prefix_test', 'image_test',
                                    '["python",  "./quiz_analyzer.py"]')
    with open('enclave_mgmt/workflow.yaml') as f:
        dataMap = yaml.safe_load(f)

        assert (['python', './quiz_analyzer.py'] ==
                dataMap['spec']['templates'][1]['container']['command'])

        assert ('image_test' ==
                dataMap['spec']['templates'][1]['container']['image'])

        assert (dataMap['spec']['templates'][2]['container']['command'][2] ==
                'aws s3 cp --recursive /data/enclave-output/ s3://raise-data/\
                    enclave-outputs/prefix_test\n')
