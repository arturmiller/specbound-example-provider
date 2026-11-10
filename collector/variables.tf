variable "fixture_state_path" {
  description = "Path to a synthetic local state fixture; never use real state."
  type        = string
  default     = "fixtures/alpha.tfstate"
}
