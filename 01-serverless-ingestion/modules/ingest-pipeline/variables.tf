variable "environment" {
  type = string
}

variable "name_prefix" {
  type    = string
  default = "ingest"
}

variable "consumer_timeout" {
  description = "Timeout in seconds for the consumer Lambda (built in Hour3)"
  type = number
  default = 30
}

variable "max_receive_count" {
  description = "Failed attempts before a message goes to the DLQ"
  type = number
  default = 3
}

variable "lambda_source_file" {
  type = string
}

variable "runtime" {
  type    = string
  default = "python3.13"
}

variable "timeout" {
  type    = number
  default = 10
}