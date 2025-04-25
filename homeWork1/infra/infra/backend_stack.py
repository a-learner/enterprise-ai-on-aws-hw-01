from pathlib import Path
from aws_cdk import Stack, RemovalPolicy, Aws, CfnOutput
from constructs import Construct

import os
import cdk_ecr_deployment as ecr_deploy

from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_apprunner as apprunner

_APP_NAME = "ai-cop-aws-backend"

# this will be different for everyone so
# make sure to change it
_SECRET_ID_SUFFIX = "ZMccRw"


class BackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # # Step 1:
        # # We need a ECR Repo
        repo = self._create_ecr_repo()

        # Step 2:
        # Build the docker image
        image = self._create_docker_image()

        target_docker_image = (
            f"{Aws.ACCOUNT_ID}.dkr.ecr.{Aws.REGION}.amazonaws.com/{_APP_NAME}:latest"
        )

        # print(image.image_uri)
        # print(target_docker_image)

        CfnOutput(
            self,
            "Image URL",
            value=f"{image.image_uri}",
            description="Backend application URL",
        )

        # # Step 3:
        # # Push the docker image to ECR
        _ = ecr_deploy.ECRDeployment(
            self,
            "deploy-docker-image",
            src=ecr_deploy.DockerImageName(image.image_uri),
            dest=ecr_deploy.DockerImageName(target_docker_image),
        )

        # Step 4:
        # Create a role that can access ECR
        # app_runner_access_role = self._create_apprunner_access_role()
        # app_runner_instance_role = self._create_apprunner_instance_role()

        # # Step 5:
        # app_runner = self._create_app_runner(
        #     app_runner_access_role,
        #     app_runner_instance_role,
        #     target_docker_image,
        # )

        # CfnOutput(self, "backend-url", value=f"https://{app_runner.attr_service_url}")
        # CfnOutput(self, "backend-image", value=image.image_uri)

    def _create_ecr_repo(self):
        repository = ecr.Repository(
            self,
            "backend-repo",
            repository_name=_APP_NAME,
            image_scan_on_push=True,
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True,
        )

        return repository

    def _create_docker_image(self) -> ecr_assets.DockerImageAsset:
        # TODO: Don't hardcode thisq
        # path_to_docker_dir = "/workspaces/enterprise-ai-on-aws-hw-01/homeWork1"
        path_to_docker_dir = str(Path(os.getcwd()).parent.joinpath("backend"))
        print("path_to_docker_dir: ", path_to_docker_dir)
        asset = ecr_assets.DockerImageAsset(
            self,
            "backend-app-image",
            directory=path_to_docker_dir,
            file="Dockerfile.backend",
            asset_name="backend-app-image",
            platform=ecr_assets.Platform.LINUX_AMD64,
            cache_disabled=True,
        )
        return asset

    def _create_apprunner_access_role(self) -> iam.Role:
        role = iam.Role(
            self,
            "access-role",
            assumed_by=iam.ServicePrincipal("build.apprunner.amazonaws.com"),
            inline_policies={
                "access-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ecr:GetAuthorizationToken",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:GetRepositoryPolicy",
                                "ecr:DescribeRepositories",
                                "ecr:ListImages",
                                "ecr:DescribeImages",
                                "ecr:BatchGetImage",
                                "ecr:GetLifecyclePolicy",
                                "ecr:GetLifecyclePolicyPreview",
                                "ecr:ListTagsForResource",
                                "ecr:DescribeImageScanFindings",
                            ],
                            resources=[
                                f"arn:aws:ecr:{Aws.REGION}:{Aws.ACCOUNT_ID}:repository/{_APP_NAME}"
                            ],
                        ),
                    ]
                )
            },
        )

        return role

    def _create_apprunner_instance_role(self) -> iam.Role:
        role = iam.Role(
            self,
            "instance-role",
            assumed_by=iam.ServicePrincipal("tasks.apprunner.amazonaws.com"),
            inline_policies={
                "instance-policy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "secretsmanager:GetResourcePolicy",
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret",
                                "secretsmanager:ListSecretVersionIds",
                            ],
                            resources=[
                                f"arn:aws:secretsmanager:{Aws.REGION}:{Aws.ACCOUNT_ID}:secret:*"
                            ],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "secretsmanager:ListSecrets",
                            ],
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["ssm:GetParameters"],
                            resources=[
                                f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/*"
                            ],
                        ),
                    ]
                )
            },
        )

        return role

    def _create_app_runner(
        self,
        app_runner_access_role: iam.Role,
        app_runner_instance_role: iam.Role,
        target_docker_image: str,
    ):
        service = apprunner.CfnService(
            self,
            "backend-service",
            service_name="ai-cop-aws-backend",
            instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
                instance_role_arn=app_runner_instance_role.role_arn,
            ),
            source_configuration=apprunner.CfnService.SourceConfigurationProperty(
                authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                    access_role_arn=app_runner_access_role.role_arn,
                ),
                image_repository=apprunner.CfnService.ImageRepositoryProperty(
                    image_identifier=target_docker_image,
                    image_repository_type="ECR",
                    image_configuration=apprunner.CfnService.ImageConfigurationProperty(
                        port="8000",
                        runtime_environment_secrets=[
                            apprunner.CfnService.KeyValuePairProperty(
                                name="A_CONFIG",
                                value=f"arn:aws:ssm:{Aws.REGION}:{Aws.ACCOUNT_ID}:parameter/ai-cop-backend-config",
                            ),
                            apprunner.CfnService.KeyValuePairProperty(
                                name="SECRET_MESSAGE",
                                value=f"arn:aws:secretsmanager:{Aws.REGION}:{Aws.ACCOUNT_ID}:secret:/ai-cop/the-secret-{_SECRET_ID_SUFFIX}",
                            ),
                        ],
                    ),
                ),
                auto_deployments_enabled=True,
            ),
            health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
                path="/health",
                protocol="HTTP",
            ),
        )

        return service
