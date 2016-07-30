# chalice-transmogrify

[![Build Status](https://travis-ci.org/uncompiled/chalice-transmogrify.svg?branch=master)](https://travis-ci.org/uncompiled/chalice-transmogrify)
[![Code Climate](https://codeclimate.com/github/uncompiled/chalice-transmogrify/badges/gpa.svg)](https://codeclimate.com/github/uncompiled/chalice-transmogrify)
[![Issue Count](https://codeclimate.com/github/uncompiled/chalice-transmogrify/badges/issue_count.svg)](https://codeclimate.com/github/uncompiled/chalice-transmogrify)

chalice-transmogrify a service that transforms XML/RSS to JSON and is 
designed to run on AWS Lambda.

It's built on the [chalice](https://github.com/awslabs/chalice)
Serverless Microframework for Python.

**Disclaimer: chalice is a developer preview project and not recommended
for production APIs.**

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