import os
import argparse

from enclave_mgmt.data_collection import (
    collect_content_dfs, collect_event_data_dfs, collect_moodle_dfs)
from enclave_mgmt.model_creation import create_models


def compile_models(data_bucket, data_key, events_bucket, events_key):
    moodle_dfs = collect_moodle_dfs(data_bucket, data_key)
    content_dfs = collect_content_dfs(data_bucket, data_key)
    event_data = collect_event_data_dfs(events_bucket, events_key)
    all_raw_dfs = moodle_dfs | content_dfs | event_data
    return all_raw_dfs


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

    all_raw_dfs = compile_models(
        args.data_bucket,
        args.data_prefix,
        args.events_bucket,
        args.events_prefix
        )

    create_models(output_path, all_raw_dfs)


if __name__ == "__main__":  # pragma: no cover
    main()
