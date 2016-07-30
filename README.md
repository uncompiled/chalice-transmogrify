# chalice-transmogrify

chalice-transmogrify a service that transforms XML/RSS to JSON and is 
designed to run on AWS Lambda.

It's built on the [chalice](https://github.com/awslabs/chalice)
Serverless Microframework for Python.

# Getting Started

## Set up your environment

- Clone this repo.
- `mkvirtualenv chalice-transmogrify` (recommended)
- `pip install -r requirements.txt`

## Configure AWS Credentials
 
chalice is specifically designed to work on [AWS Lambda](https://aws.amazon.com/lambda/),
so you will need an AWS account to use it.

If you have previously configured your machine to use boto3
(the AWS SDK for Python) or the AWS CLI, then you can skip this section.

Otherwise, you'll need to [configure your AWS credentials](http://boto3.readthedocs.io/en/latest/guide/configuration.html).

## Deploy to AWS Lambda

- `chalice deploy`

# License

The MIT License (MIT)