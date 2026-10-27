module "ingest_pipeline" {
  source               = "../../modules/ingest-pipeline"
  environment          = "dev"
  consumer_timeout     = 30
  consumer_source_file = "${path.module}/../../consumer.py"
  batch_size           = 4
}



output "queue_url" {
  value = module.ingest_pipeline.queue_url
}

output "table_name" {
  value = module.ingest_pipeline.table_name
}

output "pipeline_invoke_url" {
  value = module.ingest_pipeline.invoke_url
}