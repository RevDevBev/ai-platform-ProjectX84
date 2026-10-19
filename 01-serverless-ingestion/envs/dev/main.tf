module "ingest_api" {
  source             = "../../modules/ingest-api"
  environment        = "dev"
  lambda_source_file = "${path.module}/../../lambda_function.py"
}

output "invoke_url" {
  value = module.ingest_api.invoke_url
}