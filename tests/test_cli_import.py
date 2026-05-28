def test_wizard_cli_import_does_not_start_interactive_prompt():
    import ui.wizard_cli as wizard_cli

    assert wizard_cli.WizardCLI is not None
