run "default_fixture" {
  command = plan

  assert {
    condition = output.fixture_observation == {
      synthetic   = true
      resource_id = "synthetic-alpha"
      environment = "test"
    }
    error_message = "The default result must come from the alpha fixture."
  }
}

run "alternate_fixture" {
  command = plan

  variables {
    fixture_state_path = "fixtures/beta.tfstate"
  }

  assert {
    condition = output.fixture_observation == {
      synthetic   = true
      resource_id = "synthetic-beta"
      environment = "staging-fixture"
    }
    error_message = "The selected state fixture must determine the result."
  }
}
