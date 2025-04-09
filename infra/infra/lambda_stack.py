from pathlib import Path
from aws_cdk import Stack, CfnOutput
from constructs import Construct
from aws_cdk import aws_lambda as _lambda


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        path_to_functions_dir = (
            Path(__file__).parent.parent.parent / "lambdaFunction" / "function"
        )

        print(path_to_functions_dir)

        ex1_lambda = _lambda.Function(
            self,
            "ai-cop-hw-01",
            description="This is a lambda function to check the domain for an email Id",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset(str(path_to_functions_dir)),
        )

        # Uncomment the below lines to add the function URL
        fn_url = ex1_lambda.add_function_url(auth_type=_lambda.FunctionUrlAuthType.NONE)
        CfnOutput(self, "ai-cop-hw-01-url", value=fn_url.url)
