def test_buffer_catalog_has_expected_minimum_entries(buffer_catalog):
    assert len(buffer_catalog) >= 10
    assert all("name" in item for item in buffer_catalog)


def test_ksp_database_has_expected_minimum_entries(ksp_database):
    assert len(ksp_database) >= 17
    assert all("name" in item and "formula" in item for item in ksp_database)


def test_media_templates_has_expected_minimum_entries(media_templates):
    assert len(media_templates) >= 5
    assert all("name" in item for item in media_templates)


def test_rule_yaml_files_have_rules_list(rule_files):
    assert rule_files
    for file_name, payload in rule_files.items():
        assert isinstance(payload, dict), file_name
        assert "rules" in payload, file_name
        assert isinstance(payload["rules"], list), file_name
        assert payload["rules"], file_name
