variable "environment" {
  type = string
}

variable "name_prefix" {
  type    = string
  default = "ingest"
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