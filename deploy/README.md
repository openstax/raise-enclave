# RAISE Enclave deployment

## Overview

The deployment of the Docker image in this repo is automated via [CodePipeline](https://docs.aws.amazon.com/codepipeline). This directory includes all related configuration files with the exception of the AWS infrastructure resource definitions which live with the rest of the K12 IaC code.

RAISE enclaves are run / orchestrated on Kubernetes clusters. This directory includes configuration files for deploying necessary resources in `k8s` environments used for enclaves.

A summary of subdirectories:

* `buildspec/` - [CodeBuild](https://docs.aws.amazon.com/codebuild) buildspec files used in pipeline stages
* `k8s/` - Kubernetes configurations for deployed resources