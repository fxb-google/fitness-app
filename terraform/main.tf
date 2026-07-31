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
    "secretmanager.googleapis.com",
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

# Create Secrets
resource "google_secret_manager_secret" "smtp_username" {
  secret_id = "fitness_agent_smtp_username"
  replication {
    auto {}
  }
  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "smtp_username_version" {
  secret      = google_secret_manager_secret.smtp_username.id
  secret_data = var.smtp_username
}

resource "google_secret_manager_secret" "smtp_password" {
  secret_id = "fitness_agent_smtp_password"
  replication {
    auto {}
  }
  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "smtp_password_version" {
  secret      = google_secret_manager_secret.smtp_password.id
  secret_data = var.smtp_password
}

# Grant the default compute service account access to the secrets
data "google_project" "project" {}

resource "google_secret_manager_secret_iam_member" "secret_access_username" {
  secret_id = google_secret_manager_secret.smtp_username.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "secret_access_password" {
  secret_id = google_secret_manager_secret.smtp_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

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

    secret_environment_variables {
      key        = "SMTP_USERNAME"
      project_id = var.project_id
      secret     = google_secret_manager_secret.smtp_username.secret_id
      version    = "latest"
    }

    secret_environment_variables {
      key        = "SMTP_PASSWORD"
      project_id = var.project_id
      secret     = google_secret_manager_secret.smtp_password.secret_id
      version    = "latest"
    }
  }

  depends_on = [
    google_secret_manager_secret_iam_member.secret_access_username,
    google_secret_manager_secret_iam_member.secret_access_password
  ]
}

# Cloud Scheduler service account
resource "google_service_account" "scheduler_sa" {
  account_id   = "fitness-scheduler-sa"
  display_name = "Cloud Scheduler Service Account"
}

resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  location = google_cloudfunctions2_function.fitness_agent.location
  service  = google_cloudfunctions2_function.fitness_agent.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Cloud Scheduler Job (5 days a week at 7 AM)
resource "google_cloud_scheduler_job" "fitness_trigger" {
  name             = "trigger-fitness-agent"
  description      = "Triggers the fitness agent Mon-Fri at 7 AM"
  schedule         = "0 7 * * 1-5"
  time_zone        = "America/New_York" # Feel free to change to your local timezone
  attempt_deadline = "320s"
  region           = var.region
  
  depends_on = [google_project_service.services]

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.fitness_agent.service_config[0].uri
    
    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }
}
