# -*- coding:utf-8 -*-

import os
import json
from decimal import Decimal

import boto3


def main(report, config, output_summary):

    # dynamo
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=config['aws_access_key_id'],
                              aws_secret_access_key=config['aws_secret_access_key'],
                              region_name=config['region'])
    table = dynamodb.Table(config['table'])
    item = {
        "hashkey": report.key,
        "title": report.title,
        "one_host": report.summary.one.host,
        "other_host": report.summary.other.host,
        "same_count": Decimal(report.summary.status.same),
        "different_count": Decimal(report.summary.status.different) + Decimal(report.summary.status.same_without_order),
        "failure_count": Decimal(report.summary.status.failure),
        "start": report.summary.time.start,
        "end": report.summary.time.end,
        "report": json.loads(report.to_json(), parse_float=Decimal)
    }
    table.put_item(Item=item)

    # s3
    s3 = boto3.client('s3',
                      aws_access_key_id=config['aws_access_key_id'],
                      aws_secret_access_key=config['aws_secret_access_key'],
                      region_name=config['region'])

    def upload_s3(which: str):
        dir = f'{output_summary.response_dir}/{report.key}'
        for file in os.listdir(f'{dir}/{which}'):
            s3.upload_file(Bucket=config['bucket'],
                           Key=f'{report.key}/{which}/{file}',
                           Filename=f'{dir}/{which}/{file}')

    upload_s3("one")
    upload_s3("other")

    return report
