# SDRTrunk Proxy Player for Home Assistant

A HACS-installable custom integration that lets Home Assistant:

- Proxy your SDRTrunk/Icecast audio stream through Home Assistant (`/api/...`) so dashboards never need direct local IPs.
- Poll metadata (talker/talkgroup/source) from SDRTrunk-compatible JSON endpoints.
- Expose an `Active Talker` sensor entity.
- Provide a lightweight Lovelace custom card to play audio and show who is talking.

## What this solves

If you already stream SDRTrunk audio to Icecast, this integration lets you consume that stream inside Home Assistant without hardcoding `http://192.168.x.x:...` URLs in Lovelace. Use Home Assistant relative paths only.

---

## Install with HACS

1. In HACS, add this repository as a **Custom Repository**.
2. Category: **Integration**.
3. Install **SDRTrunk Proxy Player**.
4. Restart Home Assistant.

---

## Integrate with SDRTrunk

You need two upstream URLs that Home Assistant will consume server-side:

1. **Stream URL** (from Icecast mountpoint), example:
   - `http://YOUR_ICECAST_HOST:8000/scanner.mp3`
2. **Metadata JSON URL** (any JSON endpoint exposing current talker info), examples:
   - Icecast status endpoint: `http://YOUR_ICECAST_HOST:8000/status-json.xsl`
   - A custom SDRTrunk metadata exporter endpoint if you run one.

> Tip: if your metadata format differs, this integration still stores the raw payload in sensor attributes.

---

## Configure Home Assistant

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **SDRTrunk Proxy Player**.
3. Fill in:
   - **Name**
   - **Icecast stream URL**
   - **Metadata JSON URL**

After setup, the integration creates:

- Sensor: `<Name> Active Talker`
- Proxy stream endpoint: `/api/sdrtrunk_proxy/<entry_id>/stream`
- Proxy metadata endpoint: `/api/sdrtrunk_proxy/<entry_id>/metadata`

---

## Lovelace setup

### 1) Add card resource

Add this resource in Dashboard resources:

- URL: `/api/sdrtrunk_proxy/static/sdrtrunk-player-card.js`
- Type: `module`

### 2) Add card

Use the integration-provided proxy paths:

```yaml
type: custom:sdrtrunk-player-card
title: Police Scanner
stream_path: /api/sdrtrunk_proxy/<entry_id>/stream
metadata_path: /api/sdrtrunk_proxy/<entry_id>/metadata
autoplay: false
```

Replace `<entry_id>` with your config entry ID (from `.storage/core.config_entries` or browser URL while editing the integration entry).

---

## Notes

- Audio is authenticated via Home Assistant session because endpoints are under `/api`.
- No local network IP is required in Lovelace card config.
- If your browser blocks autoplay, click play once manually.

## Roadmap ideas

- Options flow for polling interval
- Support authenticated upstream Icecast endpoints
- Auto-generated card config helper
