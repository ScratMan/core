"""Test the IKEA Idasen Desk sensors."""

from unittest.mock import MagicMock

import pytest

from homeassistant.core import HomeAssistant

from . import init_integration


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_height_sensor(hass: HomeAssistant, mock_desk_api: MagicMock) -> None:
    """Test height sensor."""
    await init_integration(hass)

    entity_id = "sensor.test_height"
    state = hass.states.get(entity_id)
    assert state
    assert state.state == "1"

    mock_desk_api.height = 1.2
    mock_desk_api.trigger_update_callback(None)

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "1.2"
