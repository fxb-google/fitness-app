terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "storage.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# Bucket for Cloud Function source code
resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-gcf-source"
  location                    = var.region
  uniform_bucket_level_access = true
  depends_on                  = [google_project_service.services]
}

# Zip the source code
data "archive_file" "source_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/function-source.zip"
}

resource "google_storage_bucket_object" "object" {
  name   = "source-${data.archive_file.source_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.source_zip.output_path
}

data "google_project" "project" {}

# Cloud Function (2nd Gen)
resource "google_cloudfunctions2_function" "fitness_agent" {
  name        = "fitness-agent-function"
  location    = var.region
  description = "Fitness Agent Cloud Function"

  build_config {
    runtime     = "python311"
    entry_point = "generate_and_send_routine"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 120
    
    environment_variables = {
      SMTP_USERNAME = var.smtp_username
      SMTP_PASSWORD = var.smtp_password
      TARGET_EMAIL  = var.target_email
    }
  }
}

# Cloud Scheduler Job (5 days a week at 7 AM)
resource "google_cloud_scheduler_job" "fitness_trigger" {
  name             = "trigger-fitness-agent"
  description      = "Triggers the fitness agent Mon-Sat at 7 AM"
  schedule         = "0 7 * * 1-6"
  time_zone        = "America/New_York"
  attempt_deadline = "320s"
  region           = var.region
  
  depends_on = [google_project_service.services]

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.fitness_agent.service_config[0].uri
    
    oidc_token {
      service_account_email = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
    }
  }
}
