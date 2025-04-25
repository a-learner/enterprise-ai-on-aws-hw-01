from pathlib import Path
from aws_cdk import Stack, RemovalPolicy, CfnOutput
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_iam as iam

from constructs import Construct


class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool_name = "cop-ai"
        path_to_functions_dir = (
            Path(__file__).parent.parent.parent / "lambdaFunction" / "function"
        )

        domain_restrict_lambda = _lambda.Function(
            self,
            "ai-cop-hw-01",
            description="This is a lambda function to check the domain for an email Id",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset(str(path_to_functions_dir)),
        )

        # Grant Cognito permission to invoke the Lambda function
        domain_restrict_lambda.add_permission(
            "CognitoInvokeLambda",
            principal=iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            action="lambda:InvokeFunction",
        )

        user_pool = cognito.UserPool(
            self,
            user_pool_name,
            user_pool_name=user_pool_name,
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_digits=False,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False,
            ),
            mfa=cognito.Mfa.OFF,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True),
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            self_sign_up_enabled=True,
            removal_policy=RemovalPolicy.DESTROY,
            lambda_triggers=cognito.UserPoolTriggers(
                pre_sign_up=domain_restrict_lambda
            ),
        )

        user_pool_client = user_pool.add_client(
            "main-client",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        _ = CfnOutput(
            self,
            "user_pool_id",
            value=user_pool.user_pool_id,
            description="The ID of the user pool",
        )

        _ = CfnOutput(
            self,
            "user_pool_client_id",
            value=user_pool_client.user_pool_client_id,
            description="The ID of the user pool client",
        )
