data "terraform_remote_state" "example" {
  backend = "local"
  config = {
    path = var.fixture_state_path
  }
}

output "fixture_observation" {
  value = {
    synthetic   = true
    resource_id = data.terraform_remote_state.example.outputs.resource_id
    environment = data.terraform_remote_state.example.outputs.environment
  }
}
