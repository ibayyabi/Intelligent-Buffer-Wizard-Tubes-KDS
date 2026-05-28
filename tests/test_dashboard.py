from fastapi.testclient import TestClient

from ui.dashboard import app


client = TestClient(app)


def test_get_buffers_returns_catalog_data():
    response = client.get("/api/buffers")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 10
    assert any(item["name"] == "Phosphate" for item in payload)


def test_get_templates_returns_template_data():
    response = client.get("/api/templates")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 5


def test_post_formulate_returns_buffer_result():
    response = client.post(
        "/api/formulate",
        json={
            "buffer_name": "Phosphate",
            "target_ph": 7.4,
            "concentration": 0.020,
            "temperature_c": 25.0,
            "added_salts": [{"name": "NaCl", "concentration": 0.150}],
            "environment": "closed",
            "application": "biochemistry",
            "exposure": "dark",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["input_params"]["buffer_name"] == "Phosphate"
    assert payload["real_ph"] == 7.4
    assert payload["ionic_strength"] > 0
    assert payload["species_concentrations"]
    assert "overall_risk_level" in payload
