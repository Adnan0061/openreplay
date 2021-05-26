from botocore.exceptions import ClientError
from chalicelib.utils.helper import environ

import boto3
import botocore
from botocore.client import Config

client = boto3.client('s3', endpoint_url=environ["S3_HOST"],
                      aws_access_key_id=environ["S3_KEY"],
                      aws_secret_access_key=environ["S3_SECRET"],
                      config=Config(signature_version='s3v4'),
                      region_name='us-east-1')


def exists(bucket, key):
    try:
        boto3.resource('s3', endpoint_url=environ["S3_HOST"],
                       aws_access_key_id=environ["S3_KEY"],
                       aws_secret_access_key=environ["S3_SECRET"],
                       config=Config(signature_version='s3v4'),
                       region_name='us-east-1') \
            .Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            # Something else has gone wrong.
            raise
    return True


def get_presigned_url_for_sharing(bucket, expires_in, key, check_exists=False):
    if check_exists and not exists(bucket, key):
        return None

    return client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket,
            'Key': key
        },
        ExpiresIn=expires_in
    )


def get_presigned_url_for_upload(bucket, expires_in, key):
    return client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket,
            'Key': key
        },
        ExpiresIn=expires_in
    )


def get_file(source_bucket, source_key):
    print("******************************")
    print(f"looking for: {source_key} in {source_bucket}")
    print("******************************")
    try:
        result = client.get_object(
            Bucket=source_bucket,
            Key=source_key
        )
    except ClientError as ex:
        if ex.response['Error']['Code'] == 'NoSuchKey':
            print(f'======> No object found - returning None for {source_bucket}/{source_key}')
            return None
        else:
            raise ex
    return result["Body"].read().decode()