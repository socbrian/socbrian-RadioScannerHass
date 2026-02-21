"""The SDRTrunk Proxy integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import async_register_views
from .const import CONF_METADATA_URL, DOMAIN, PLATFORMS, STATIC_PATH
from .coordinator import SDRTrunkCoordinator


def _entry_store(hass: HomeAssistant) -> dict[str, dict]:
    return hass.data.setdefault(DOMAIN, {})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up static files used by the Lovelace card."""
    card_path = Path(__file__).parent
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url_path=STATIC_PATH,
                path=str(card_path),
                cache_headers=False,
            )
        ]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SDRTrunk Proxy from a config entry."""
    coordinator = SDRTrunkCoordinator(hass, entry.data.get(CONF_METADATA_URL), entry.title)
    await coordinator.async_config_entry_first_refresh()

    _entry_store(hass)[entry.entry_id] = {"coordinator": coordinator}
    async_register_views(hass, entry, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload SDRTrunk Proxy config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        _entry_store(hass).pop(entry.entry_id, None)
    return unloaded
