import argparse
import jinja2


def create_workflow(prefix, image, command,
                    output_path='./enclave_mgmt/workflow.yaml'):

    environment = jinja2.Environment()

    with open('./enclave_mgmt/workflow_template.yaml') as template_file:
        template = environment.from_string(template_file.read())
        with open(f'{output_path}', mode='w') as workflow_file:
            workflow_file.write(template.render(prefix=prefix,
                                                image=image, command=command))


def main():
    parser = argparse.ArgumentParser(description='Target data details')
    parser.add_argument('prefix', type=str,
                        help='Desired location in S3')
    parser.add_argument('image', type=str,
                        help='Researcher docker image')
    parser.add_argument('command', type=str, help='Start command')

    args = parser.parse_args()

    create_workflow(
        args.prefix,
        args.image,
        args.command)


if __name__ == "__main__":  # pragma: no cover
    main()
