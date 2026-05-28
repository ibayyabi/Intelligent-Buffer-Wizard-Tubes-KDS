from pathlib import Path


INDEX_HTML = Path("ui/templates/index.html").read_text()
STYLES_CSS = Path("ui/static/styles.css").read_text()


def test_dashboard_tabs_use_explicit_data_tab_identifiers():
    expected_tabs = ["recipe", "chemistry", "charts", "safety", "recommendations"]

    for tab in expected_tabs:
        assert f'data-tab="{tab}"' in INDEX_HTML
        assert f"switchTab('{tab}')" in INDEX_HTML

    assert "btn.innerText.toLowerCase().includes(tabId)" not in INDEX_HTML
    assert "btn.dataset.tab === tabId" in INDEX_HTML


def test_dashboard_active_tab_has_visible_selected_state():
    assert ".tab-btn.active" in STYLES_CSS
    assert "box-shadow" in STYLES_CSS
    assert "transform: translateY(-1px)" in STYLES_CSS
    assert ".tab-btn.active::after" in STYLES_CSS


def test_video_demo_testcase_document_exists():
    testcase = Path("TESTCASE.md")
    assert testcase.exists()

    content = testcase.read_text()
    assert "# Test Case Video Demonstrasi" in content
    assert "Preparation Protocols" in content
    assert "Indikator tab aktif" in content
