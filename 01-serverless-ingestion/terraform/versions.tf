terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.69.1"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "tfstate-hamzah-48271"
    key = "serverless-ingestion/dev/terraform.tfstate"
    region = "eu-north-1"
    profile = "Touch Grass Later"
    encrypt = true
    use_lockfile = true
  }
}

provider "aws" {
  region  = "eu-north-1"
  profile = "Touch Grass Later"
}