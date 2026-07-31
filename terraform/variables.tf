variable "project_id" {
  type        = string
  description = "The GCP project ID"
  default     = "fitnessapp-504108"
}

variable "region" {
  type        = string
  description = "The GCP region to deploy resources to"
  default     = "us-central1"
}

variable "smtp_username" {
  type        = string
  description = "The Gmail address to send from"
}

variable "smtp_password" {
  type        = string
  description = "The Gmail App Password (16 characters)"
  sensitive   = true
}
