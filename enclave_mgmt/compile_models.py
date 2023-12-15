import os
import argparse
import boto3
import pandas as pd
from io import BytesIO

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
    parser.add_argument('--research_filter_bucket', type=str,
                        help='CHANGE ME')
    parser.add_argument('--research_filter_prefix', type=str,
                        help='CHANGE ME')

    args = parser.parse_args()

    output_path = os.environ["CSV_OUTPUT_DIR"]

    all_raw_dfs = collect_data(
        args.data_bucket,
        args.data_prefix,
        args.events_bucket,
        args.events_prefix
        )

    research_filter_bucket = args.research_filter_bucket
    research_filter_key = args.research_filter_prefix
    if research_filter_bucket and research_filter_key:
        s3_client = boto3.client("s3")
        courses_stream = s3_client.get_object(
            Bucket=research_filter_bucket,
            Key=research_filter_key)
        courses_data_df = pd.read_csv(
            BytesIO(courses_stream["Body"].read()),
            keep_default_na=False
        )
        research_course_df = courses_data_df.loc[courses_data_df[
            'research_participation'] == 1]
        research_course_df = research_course_df[[
            'id'
        ]]
        research_course_df.rename(columns={'id': 'course_id'}, inplace=True)
        create_models(output_path, all_raw_dfs, research_course_df)
    else:
        create_models(output_path, all_raw_dfs)


if __name__ == "__main__":  # pragma: no cover
    main()
