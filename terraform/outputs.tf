output "function_uri" {
  description = "The URI of the Cloud Function"
  value       = google_cloudfunctions2_function.fitness_agent.service_config[0].uri
}

output "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.fitness_trigger.name
}
