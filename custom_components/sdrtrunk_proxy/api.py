"""HTTP views for SDRTrunk proxy streaming and metadata."""

from __future__ import annotations

from aiohttp import ClientError, web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_STREAM_URL, DOMAIN
from .coordinator import SDRTrunkCoordinator


class SDRTrunkStreamProxyView(HomeAssistantView):
    """Proxy audio stream from Icecast so Lovelace can use HA-relative URLs."""

    # Keep stream usable for HTML media elements (audio/video) that can fail with
    # HA auth headers in some clients and dashboards.
    requires_auth = False

    def __init__(self, entry: ConfigEntry) -> None:
        self.url = f"/{DOMAIN}/{entry.entry_id}/stream"
        self.extra_urls = [f"/api/{DOMAIN}/{entry.entry_id}/stream"]
        self.name = f"api:{DOMAIN}:stream:{entry.entry_id}"
        self._stream_url = entry.data[CONF_STREAM_URL]

    async def get(self, request: web.Request) -> web.StreamResponse:
        """Proxy the upstream streaming endpoint."""
        session = async_get_clientsession(request.app["hass"])
        try:
            upstream = await session.get(
                self._stream_url,
                headers={
                    "Icy-MetaData": "1",
                    "Accept": "*/*",
                },
            )
        except ClientError as err:
            return web.Response(status=502, text=f"Failed to connect to upstream stream: {err}")

        if upstream.status >= 400:
            text = await upstream.text()
            upstream.close()
            return web.Response(
                status=upstream.status,
                text=text or f"Upstream stream returned HTTP {upstream.status}",
            )

        headers = {"Cache-Control": "no-store"}
        content_type = upstream.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type

        downstream = web.StreamResponse(status=200, reason="OK", headers=headers)
        await downstream.prepare(request)

        try:
            async for chunk in upstream.content.iter_chunked(64 * 1024):
                await downstream.write(chunk)
        except (ClientError, ConnectionError):
            pass
        finally:
            upstream.close()
            await downstream.write_eof()

        return downstream


class SDRTrunkMetadataView(HomeAssistantView):
    """Return normalized talker metadata for the configured stream."""

    requires_auth = True

    def __init__(self, entry: ConfigEntry, coordinator: SDRTrunkCoordinator) -> None:
        self.url = f"/api/{DOMAIN}/{entry.entry_id}/metadata"
        self.name = f"api:{DOMAIN}:metadata:{entry.entry_id}"
        self._coordinator = coordinator

    async def get(self, request: web.Request) -> web.Response:
        """Return current metadata from coordinator cache."""
        data = self._coordinator.data
        payload = {
            "talker": data.talker if data else "idle",
            "talkgroup": data.talkgroup if data else None,
            "source": data.source if data else None,
            "raw": data.raw if data else None,
        }
        return web.json_response(payload)


def async_register_views(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: SDRTrunkCoordinator,
) -> None:
    """Register per-entry API endpoints."""
    hass.http.register_view(SDRTrunkStreamProxyView(entry))
    hass.http.register_view(SDRTrunkMetadataView(entry, coordinator))
