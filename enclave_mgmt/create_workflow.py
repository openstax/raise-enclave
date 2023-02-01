import argparse
import jinja2
from pathlib import Path


def create_workflow(prefix, image, command, output_path):

    environment = jinja2.Environment()
    template_path = Path(__file__).parent / 'workflow_template.yaml'

    with open(template_path) as template_file:
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
    parser.add_argument('output_path', type=str, help='Output yaml file path.')

    args = parser.parse_args()

    create_workflow(
        args.prefix,
        args.image,
        args.command,
        args.output_path)


if __name__ == "__main__":  # pragma: no cover
    main()
