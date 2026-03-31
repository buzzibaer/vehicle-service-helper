from pathlib import Path
import json


def test_manifest_exists_and_domain_matches() -> None:
    manifest_path = Path("custom_components/vehicle_service_helper/manifest.json")
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["domain"] == "vehicle_service_helper"
    assert manifest["config_flow"] is True


def test_core_files_exist() -> None:
    required_files = [
        "custom_components/vehicle_service_helper/__init__.py",
        "custom_components/vehicle_service_helper/const.py",
        "custom_components/vehicle_service_helper/config_flow.py",
    ]
    for file_path in required_files:
        assert Path(file_path).exists()
