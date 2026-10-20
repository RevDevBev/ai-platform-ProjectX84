module "ingest_pipeline" {
  source             = "../../modules/ingest-pipeline"
  environment        = "dev"
  consumer_timeout   = 30
  lambda_source_file = "${path.module}/../../lambda_function.py"
}



output "queue_url" {
  value = module.ingest_pipeline.queue_url
}

output "table_name" {
  value = module.ingest_pipeline.table_name
}