module "ingest_pipeline" {
  source               = "../../modules/ingest-pipeline"
  environment          = "prod"
  consumer_timeout     = 30
  batch_size           = 5
  consumer_source_file = "${path.module}/../../consumer.py"
}

output "pipeline_invoke_url" {
  value = module.ingest_pipeline.invoke_url
}

output "queue_url" {
  value = module.ingest_pipeline.queue_url
}

output "table_name" {
  value = module.ingest_pipeline.table_name
}