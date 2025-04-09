#!/usr/bin/env python3
import aws_cdk as cdk

from infra.lambda_stack import LambdaStack
# from infra.ex2_stack import Example2Stack
# from infra.ex4_stack import Example4Stack

app = cdk.App()

LambdaStack(app, "LambdaStack")
# Example2Stack(app, "Example2Stack")
# Example4Stack(app, "Example4Stack")

app.synth()