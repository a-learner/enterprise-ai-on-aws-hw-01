from pathlib import Path
import subprocess
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import CfnOutput, RemovalPolicy

from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment

# Remember:
# Stack is a collection of AWS Resources


class FrontendPyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Step 1: Create and deploy the bucket with frontend content
        self.web_bucket = self._create_and_deploy_bucket()

        # Step 2: Create a CloudFront distribution
        self.distribution = self._create_cloud_distribution()

        CfnOutput(
            self,
            "distribution-domain-name",
            value=self.distribution.distribution_domain_name,
            description="The domain name of the CloudFront distribution",
        )

    def _build_frontend(self, front_end: Path) -> None:
        subprocess.run(["npm", "install"], cwd=str(front_end), check=True)
        subprocess.run(["npm", "run", "build"], cwd=str(front_end), check=True)

    def _create_and_deploy_bucket(self):
        # Step 1a: Create an S3 bucket

        # this is to keep the name of bucket unique
        suffix = "hs"

        web_bucket = s3.Bucket(
            self,
            "bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="index.html",
            bucket_name=f"cop-hw1-frontend-{suffix}",
        )

        # Step 1b: Pushing the content of the frontend to the S3 bucket
        # Note - do not hardcode the paths
        frontend_dir_path = Path(
            "/workspaces/enterprise-ai-on-aws-hw-01/homeWork1/frontend"
        )

        self._build_frontend(frontend_dir_path)

        web_bucket_deploy = s3_deployment.BucketDeployment(
            self,
            "deployment",
            sources=[
                s3_deployment.Source.asset(str(frontend_dir_path.joinpath("dist")))
            ],
            destination_bucket=web_bucket,
        )

        return web_bucket

    def _create_cloud_distribution(self):
        distribution = cf.Distribution(
            self,
            "distribution",
            default_root_object="index.html",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3Origin(self.web_bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,  # noqa
            ),
        )

        return distribution
