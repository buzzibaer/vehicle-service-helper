from custom_components.vehicle_service_helper.const import CONF_LICENSE_PLATE
from custom_components.vehicle_service_helper.diagnostics import (
    TO_REDACT,
    _build_diagnostics_payload,
)


def test_diagnostics_payload_shape() -> None:
    payload = _build_diagnostics_payload(
        entry_data={"vehicle_name": "Car A", "license_plate": "AB-123"},
        option_data={"templates": []},
        coordinator_data={"template_1": {"status": "ok"}},
        devices=[{"id": "dev1", "name": "Car A"}],
    )

    assert payload["entry"]["vehicle_name"] == "Car A"
    assert payload["options"]["templates"] == []
    assert payload["coordinator_data"]["template_1"]["status"] == "ok"
    assert payload["devices"][0]["id"] == "dev1"


def test_diagnostics_redact_set_includes_license_plate() -> None:
    assert CONF_LICENSE_PLATE in TO_REDACT
