from custom_components.vehicle_service_helper.const import DOMAIN
from custom_components.vehicle_service_helper.services import _get_entry_and_coordinator


class _DummyConfigEntries:
    def __init__(self, entries: dict[str, object]) -> None:
        self._entries = entries

    def async_get_entry(self, entry_id: str):
        return self._entries.get(entry_id)


class _DummyHass:
    def __init__(self, entries: dict[str, object], coordinators: dict[str, object]) -> None:
        self.config_entries = _DummyConfigEntries(entries)
        self.data = {DOMAIN: coordinators}


def test_get_entry_and_coordinator_returns_coordinator() -> None:
    coordinator = object()
    hass = _DummyHass(entries={"abc": object()}, coordinators={"abc": coordinator})
    result = _get_entry_and_coordinator(hass, "abc")
    assert result is coordinator


def test_get_entry_and_coordinator_raises_for_missing_entry() -> None:
    hass = _DummyHass(entries={}, coordinators={})
    try:
        _get_entry_and_coordinator(hass, "missing")
    except ValueError as err:
        assert str(err) == "unknown_entry"
    else:
        raise AssertionError("Expected ValueError for missing entry")


def test_get_entry_and_coordinator_raises_for_unloaded_entry() -> None:
    hass = _DummyHass(entries={"abc": object()}, coordinators={})
    try:
        _get_entry_and_coordinator(hass, "abc")
    except ValueError as err:
        assert str(err) == "entry_not_loaded"
    else:
        raise AssertionError("Expected ValueError for missing coordinator")


def test_get_entry_and_coordinator_raises_when_domain_data_missing() -> None:
    hass = _DummyHass(entries={"abc": object()}, coordinators={})
    hass.data = {}
    try:
        _get_entry_and_coordinator(hass, "abc")
    except ValueError as err:
        assert str(err) == "entry_not_loaded"
    else:
        raise AssertionError("Expected ValueError when integration data is missing")
