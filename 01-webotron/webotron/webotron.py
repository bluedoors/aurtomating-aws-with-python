import boto3
from botocore.exceptions import ClientError
import click

session = boto3.session.Session()
s3 = session.resource('s3')


@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass


@cli.command('list-buckets')
def list_buckets():
    "List all s3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure S3 bucket"
    s3_bucket = None

    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                'LocationConstraint': session.region_name}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e

    policy = """
        {
        "Version":"2012-10-17",
        "Statement":[
        {
        "Sid":"PublicRead",
        "Effect":"Allow",
        "Principal": "*",
        "Action":["s3:GetObject"],
        "Resource":["arn:aws:s3:::%s/*"]
        }
        ]
        }
        """ % s3_bucket.name
    policy = policy.strip()

    bucket_policy = s3_bucket.Policy()
    bucket_policy.put(Policy=policy)
    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={'ErrorDocument': {
        'Key': 'error.html'
    },
        'IndexDocument': {
        'Suffix': 'index.html'
    }})

    return

if __name__ == '__main__':
    cli()
