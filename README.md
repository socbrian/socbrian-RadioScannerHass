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

You need at least one upstream URL:

1. **Stream URL** (from Icecast mountpoint), example:
   - `http://YOUR_ICECAST_HOST:8000/scanner.mp3`
2. **Metadata JSON URL** (**optional**, for who-is-talking data), examples:
   - Icecast status endpoint: `http://YOUR_ICECAST_HOST:8000/status-json.xsl`
   - A custom SDRTrunk metadata exporter endpoint if you run one.

If you don't have metadata yet, leave Metadata URL blank. Audio proxy still works, but talker fields will stay `idle`/empty.

### Where can metadata JSON come from?

Icecast only provides JSON if `status-json.xsl` is enabled and reachable. Some installs disable it.

If your Icecast doesn't expose JSON, common options are:

1. Use an SDRTrunk sidecar script/service that listens to SDRTrunk events and publishes a tiny JSON endpoint (talker, talkgroup, source).
2. Publish metadata to MQTT from SDRTrunk, then expose it through Home Assistant as a REST endpoint/template sensor.
3. Use any existing scanner backend endpoint that returns JSON and map fields via the integration's normalization logic.

Minimum JSON this integration can use is:

```json
{
  "talker": "Unit 123",
  "talkgroup": "Dispatch",
  "source": "County P25"
}
```

---

## Configure Home Assistant

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **SDRTrunk Proxy Player**.
3. Fill in:
   - **Name**
   - **Icecast stream URL**
   - **Metadata JSON URL** (optional)

After setup, the integration creates:

- Sensor: `<Name> Active Talker`
- Proxy stream endpoint: `/api/sdrtrunk_proxy/<entry_id>/stream`
- Proxy metadata endpoint: `/api/sdrtrunk_proxy/<entry_id>/metadata`

---

## Lovelace setup

If this is your first custom card, do these steps in order.

### 1) Add the card JavaScript resource (UI method)

1. Open your dashboard.
2. Click the **⋮** menu (top-right) → **Edit dashboard**.
3. Click the **⋮** menu again → **Manage resources**.
4. Click **Add resource**.
5. Enter:
   - **URL**: `/api/sdrtrunk_proxy/static/sdrtrunk-player-card.js`
   - **Resource type**: `JavaScript Module` (or `module`)
6. Click **Create** / **Save**.

If you use YAML mode dashboards, add this under `lovelace: resources:` in `configuration.yaml`:

```yaml
lovelace:
  resources:
    - url: /api/sdrtrunk_proxy/static/sdrtrunk-player-card.js
      type: module
```

### 2) Get your integration `entry_id`

You need this once to build your proxy paths.

Options:

1. **UI URL method (easiest):**
   - Go to **Settings → Devices & Services → SDRTrunk Proxy Player → Configure**.
   - Look at the browser URL; copy the long ID in the path (the config entry id).
2. **Storage file method:**
   - Open `.storage/core.config_entries`.
   - Find the `"domain": "sdrtrunk_proxy"` block and copy `"entry_id"`.

Example entry id:

`01JABCDEF23456789XYZ00000`

### 3) Add the card

1. Open dashboard → **Edit dashboard** → **Add card**.
2. Choose **Manual** card.
3. Paste:

```yaml
type: custom:sdrtrunk-player-card
title: Police Scanner
stream_path: /api/sdrtrunk_proxy/01JABCDEF23456789XYZ00000/stream
metadata_path: /api/sdrtrunk_proxy/01JABCDEF23456789XYZ00000/metadata
autoplay: false
```

Replace the sample ID with your own entry id.

### 4) Quick troubleshooting

If the card does not appear:

- Hard refresh browser (`Ctrl+F5`) after adding resource.
- Confirm resource URL is exactly `/api/sdrtrunk_proxy/static/sdrtrunk-player-card.js`.
- Confirm card type is exactly `custom:sdrtrunk-player-card`.
- Confirm your `entry_id` is correct in both `stream_path` and `metadata_path`.

---

## Notes

- Audio is authenticated via Home Assistant session because endpoints are under `/api`.
- No local network IP is required in Lovelace card config.
- If your browser blocks autoplay, click play once manually.

## Roadmap ideas

- Options flow for polling interval
- Support authenticated upstream Icecast endpoints
- Auto-generated card config helper
