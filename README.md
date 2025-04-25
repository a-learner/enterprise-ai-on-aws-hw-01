# enterprise-ai-on-aws-hw-01
Homework



## Setup credentials in container

```bash
aws configure
```

```bash
# check caller identity
# Security Token Service - sts
aws sts get-caller-identity
```


## Setup for Infra

Creae the virtual environment and activate it

```bash
cd homework1/infra
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
