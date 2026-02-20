"""Data coordinator for SDRTrunk metadata."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL


@dataclass(slots=True)
class TalkerMetadata:
    """Normalized talker metadata."""

    talker: str = "idle"
    talkgroup: str | None = None
    source: str | None = None
    raw: dict[str, Any] | None = None


class SDRTrunkCoordinator(DataUpdateCoordinator[TalkerMetadata]):
    """Coordinate SDRTrunk metadata polling."""

    def __init__(self, hass: HomeAssistant, metadata_url: str | None, name: str) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{name} metadata",
            update_interval=UPDATE_INTERVAL,
        )
        self._metadata_url = metadata_url

    async def _async_update_data(self) -> TalkerMetadata:
        """Fetch and normalize metadata from configured endpoint."""
        if not self._metadata_url:
            return TalkerMetadata()

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(self._metadata_url, timeout=10) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Unable to fetch metadata: {err}") from err

        return _normalize_metadata(payload)


def _normalize_metadata(payload: Any) -> TalkerMetadata:
    """Support common metadata formats from SDRTrunk or Icecast status endpoints."""
    if isinstance(payload, list) and payload:
        payload = payload[0]

    if not isinstance(payload, dict):
        return TalkerMetadata(raw={"payload": payload})

    icecast_source = payload.get("icestats", {}).get("source")
    if isinstance(icecast_source, list) and icecast_source:
        icecast_source = icecast_source[0]

    source_data = icecast_source if isinstance(icecast_source, dict) else payload

    talker = (
        source_data.get("talker")
        or source_data.get("alias")
        or source_data.get("title")
        or source_data.get("metadata")
        or "idle"
    )
    talkgroup = (
        source_data.get("talkgroup")
        or source_data.get("tg")
        or source_data.get("genre")
    )
    source = (
        source_data.get("source")
        or source_data.get("radio_id")
        or source_data.get("server_name")
        or source_data.get("server_description")
    )

    return TalkerMetadata(
        talker=str(talker),
        talkgroup=str(talkgroup) if talkgroup else None,
        source=str(source) if source else None,
        raw=payload,
    )
