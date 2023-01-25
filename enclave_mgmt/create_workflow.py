import argparse
import yaml

def create_workflow(prefix, image, command):

    data = {
  "kind": "Workflow", 
  "spec": {
    "templates": [
      {
        "container": {
          "command": [
            "bash", 
            "-cxe", 
            "mkdir /data/enclave-input\nmkdir /data/enclave-output\ncompile-models raise-data algebra1/ay2022 raise-sftp-home houstonisd-oneroster/RICE_OpenStax_1_1.zip\n"
          ], 
          "image": "361171574891.dkr.ecr.us-east-1.amazonaws.com/raise-enclave", 
          "volumeMounts": [
            {
              "mountPath": "/data", 
              "name": "workdir"
            }
          ], 
          "env": [
            {
              "name": "CSV_OUTPUT_DIR", 
              "value": "/data/enclave-input"
            }
          ]
        }, 
        "name": "setup", 
        "serviceAccountName": "raise-enclave-data"
      },
      {
        "container": {
          "command": command,
          "image": image, 
          "args": [], 
          "volumeMounts": [
            {
              "mountPath": "/data", 
              "name": "workdir"
            }
          ], 
          "env": [
            {
              "name": "DATA_INPUT_DIR", 
              "value": "/data/enclave-input"
            }, 
            {
              "name": "RESULT_OUTPUT_DIR", 
              "value": "/data/enclave-output"
            }
          ]
        }, 
        "name": "analyze", 
        "metadata": {
          "labels": {
            "role": "enclave"
          }
        }
      }, 
      {
        "container": {
          "command": [
            "bash", 
            "-cxe", 
            f"aws s3 cp --recursive /data/enclave-output/ s3://raise-data/enclave-outputs/{prefix}\n"
          ], 
          "image": "361171574891.dkr.ecr.us-east-1.amazonaws.com/raise-enclave", 
          "volumeMounts": [
            {
              "mountPath": "/data", 
              "name": "workdir"
            }
          ], 
          "env": [
            {
              "name": "RESULT_DIR", 
              "value": "/data/enclave-output"
            }
          ]
        }, 
        "name": "postprocess", 
        "serviceAccountName": "raise-enclave-data"
      }, 
      {
        "dag": {
          "tasks": [
            {
              "name": "setup", 
              "template": "setup"
            }, 
            {
              "dependencies": [
                "setup"
              ], 
              "name": "analyze", 
              "template": "analyze"
            }, 
            {
              "dependencies": [
                "analyze"
              ], 
              "name": "postprocess", 
              "template": "postprocess"
            }
          ]
        }, 
        "name": "flow"
      }
    ], 
    "entrypoint": "flow", 
    "volumeClaimTemplates": [
      {
        "spec": {
          "storageClassName": "gp2", 
          "accessModes": [
            "ReadWriteOnce"
          ], 
          "resources": {
            "requests": {
              "storage": "1Gi"
            }
          }
        }, 
        "metadata": {
          "name": "workdir"
        }
      }
    ]
  }, 
  "apiVersion": "argoproj.io/v1alpha1", 
  "metadata": {
    "generateName": "raise-enclave-run-"
  }
}

    with open('data.yaml', 'w') as outfile:
        yaml.dump(data, outfile)


def main():
    parser = argparse.ArgumentParser(description='Target data details')
    parser.add_argument('prefix', type=str,
                        help='desired location in S3')
    parser.add_argument('image', type=str,
                        help='Researcher docker image')
    # parser.add_argument('command', type=str,
    #                     help='bucket for oneroster data')
    parser.add_argument('command',help='list command', nargs='*')

    args = parser.parse_args()


    create_workflow(
        args.prefix,
        args.image,
        args.command)


if __name__ == "__main__":  # pragma: no cover
    main()
