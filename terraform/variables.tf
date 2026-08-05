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

variable "target_email" {
  type        = string
  description = "The destination email address for the fitness routines"
  sensitive   = true
}

variable "gemini_api_key" {
  description = "The Gemini API Key"
  type        = string
  sensitive   = true
}

variable "time_zone" {
  type        = string
  description = "The timezone for the daily workout schedule"
  default     = "Asia/Dubai"
}
