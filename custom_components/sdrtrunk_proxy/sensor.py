"""Sensor platform for SDRTrunk Proxy."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SDRTrunkCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for a config entry."""
    coordinator: SDRTrunkCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SDRTrunkTalkerSensor(entry, coordinator)])


class SDRTrunkTalkerSensor(CoordinatorEntity[SDRTrunkCoordinator], SensorEntity):
    """Represents the currently active talker."""

    _attr_icon = "mdi:radio-handheld"

    def __init__(self, entry: ConfigEntry, coordinator: SDRTrunkCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Active Talker"
        self._attr_unique_id = f"{entry.entry_id}_active_talker"

    @property
    def native_value(self) -> str:
        data = self.coordinator.data
        return data.talker if data else "idle"

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        data = self.coordinator.data
        if not data:
            return {}

        return {
            "talkgroup": data.talkgroup,
            "source": data.source,
            "raw": data.raw,
        }
