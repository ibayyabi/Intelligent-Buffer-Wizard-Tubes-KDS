from rich.console import Console

from ui.wizard_cli import build_header_panel


def test_header_panel_renders_without_missing_style_error():
    console = Console(record=True, width=100)

    console.print(build_header_panel())

    output = console.export_text()
    assert "Intelligent Buffer Wizard" in output
