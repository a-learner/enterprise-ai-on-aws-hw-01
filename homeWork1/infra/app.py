#!/usr/bin/env python3
import aws_cdk as cdk

from infra.backend_stack import BackendStack

# from infra.cognito_stack import CognitoStack
# from infra.frontend_stack import FrontendPyStack

app = cdk.App()
BackendStack(app, "AppRunnerStack-3")
# CognitoStack(app, "CognitoStack")

# FrontendPyStack(app, "FrontendStack")


app.synth()
