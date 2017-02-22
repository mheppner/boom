# Basic Object Obtainment Maître d'

Simple Django application to retrieve remote content (file and git repos) and stream back from BOOM server.  Content may be optionally Base64 encoded by BOOM. Support is also provided for chunking retrieved data to arbitrary max MiBs.

## Installation

```sh
virtualenv --python=`which python2` venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Set your access key and secret token to `~/.aws/credentials` per the [`boto3` configuration](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration) docs. Zappa will create and manage IAM permissions automatically, but you need admin permission for the user you are using. [Custom roles and policies](https://github.com/Miserlou/Zappa#using-custom-aws-iam-roles-and-policies) can be provided and current effort is underway to create a minimal policy for using Zappa.

Change the S3 bucket name in `zappa_settings.json`, as well as that static bucket in `settings.py`. Be sure to allow public access for the static bucket.

## Deployment

First time deployment:

```sh
zappa deploy dev
```

After making changes that do not touch the underlying routes:

```sh
zappa update dev
```

## TODO

- change uploads to go directly to S3
- set up listeners to watch for S3 events
- ...
