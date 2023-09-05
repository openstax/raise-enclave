import os
import argparse

from enclave_mgmt.collect_data import collect_data
from enclave_mgmt.create_models import create_models


def main():
    parser = argparse.ArgumentParser(description='Upload Resources to S3')
    parser.add_argument('data_bucket', type=str,
                        help='bucket for the moodle grade and user data dirs')
    parser.add_argument('data_prefix', type=str,
                        help='prefix for the moodle grade and user data dirs')
    parser.add_argument('events_bucket', type=str,
                        help='bucket for the event data dirs')
    parser.add_argument('events_prefix', type=str,
                        help='prefix for the event data dirs')

    args = parser.parse_args()

    output_path = os.environ["CSV_OUTPUT_DIR"]

    all_raw_dfs = collect_data(
        args.data_bucket,
        args.data_prefix,
        args.events_bucket,
        args.events_prefix
        )

    create_models(output_path, all_raw_dfs)


if __name__ == "__main__":  # pragma: no cover
    main()
