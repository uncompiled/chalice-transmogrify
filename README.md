# chalice-transmogrify

[![Build Status](https://travis-ci.org/uncompiled/chalice-transmogrify.svg?branch=master)](https://travis-ci.org/uncompiled/chalice-transmogrify)
[![Code Climate](https://codeclimate.com/github/uncompiled/chalice-transmogrify/badges/gpa.svg)](https://codeclimate.com/github/uncompiled/chalice-transmogrify)
[![Issue Count](https://codeclimate.com/github/uncompiled/chalice-transmogrify/badges/issue_count.svg)](https://codeclimate.com/github/uncompiled/chalice-transmogrify)
[![Requirements Status](https://requires.io/github/uncompiled/chalice-transmogrify/requirements.svg?branch=master)](https://requires.io/github/uncompiled/chalice-transmogrify/requirements/?branch=master)

chalice-transmogrify a service that transforms XML/RSS to JSON and is 
designed to run on AWS Lambda.

It's built on the [chalice](https://github.com/awslabs/chalice)
Serverless Microframework for Python.

**Disclaimer: chalice is a developer preview project and not recommended
for production APIs.**

## Getting Started

### Set up your environment

- `git clone https://github.com/uncompiled/chalice-transmogrify.git`
- `cd chalice-transmogrify`
- `mkvirtualenv chalice-transmogrify` (recommended)
- `pip install -r requirements.txt`

### Configure AWS Credentials
 
chalice is specifically designed to work on [AWS Lambda](https://aws.amazon.com/lambda/),
so you will need an AWS account to use it.

If you have previously configured your machine to use boto3
(the AWS SDK for Python) or the AWS CLI, then you can skip this section.

Otherwise, you'll need to [configure your AWS credentials](http://boto3.readthedocs.io/en/latest/guide/configuration.html).

### Deploy to AWS Lambda

- `chalice deploy`

## Endpoints

```
GET /convert
```

PARAMS:

- **url** = urlencoded path to an RSS feed


### Example Request
`/convert?url=http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml`

### Example Response
```
{
    "rss": {
        "@xmlns:dc": "http://purl.org/dc/elements/1.1/",
        "@xmlns:media": "http://search.yahoo.com/mrss/",
        "@xmlns:atom": "http://www.w3.org/2005/Atom",
        "@xmlns:nyt": "http://www.nytimes.com/namespaces/rss/2.0",
        "@version": "2.0",
        "channel": {
            "title": "NYT > Home Page",
            "link": "http://www.nytimes.com/pages/index.html?partner=rss&emc=rss",
            "atom:link": {},
            "description": null,
            "language": "en-us",
            "copyright": "Copyright 2016  The New York Times Company",
            "lastBuildDate": "Tue, 31 May 2016 00:42:36 GMT",
            "image": {
                "title": "NYT > Home Page",
                "url": "https://static01.nyt.com/images/misc/NYT_logo_rss_250x40.png",
                "link": "http://www.nytimes.com/pages/index.html?partner=rss&emc=rss"
            },
            "item": [] // feed items
        }
    }
}
```

## License

The MIT License (MIT)