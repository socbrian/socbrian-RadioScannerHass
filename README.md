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
   - `http://YOUR_ICECAST_HOST:8000/p25` (no file extension is also valid)
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
- Proxy stream endpoint (preferred): `/sdrtrunk_proxy/<entry_id>/stream`
- Legacy stream endpoint (still available): `/api/sdrtrunk_proxy/<entry_id>/stream`
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
stream_path: /sdrtrunk_proxy/01JABCDEF23456789XYZ00000/stream
metadata_path: /api/sdrtrunk_proxy/01JABCDEF23456789XYZ00000/metadata
autoplay: false
```

Prefer `/sdrtrunk_proxy/<entry_id>/stream` for `stream_path` if you previously saw 401 errors.

Replace the sample ID with your own entry id.

### 4) Quick troubleshooting

If the card does not appear:

- Hard refresh browser (`Ctrl+F5`) after adding resource.
- Confirm resource URL is exactly `/api/sdrtrunk_proxy/static/sdrtrunk-player-card.js`.
- Confirm card type is exactly `custom:sdrtrunk-player-card`.
- Confirm your `entry_id` is correct in both `stream_path` and `metadata_path`.

If stream loads but does not play:

- Test the HA proxy URL directly in browser first: `/sdrtrunk_proxy/<entry_id>/stream`.
- Check Home Assistant logs for upstream HTTP errors from the stream endpoint.
- Make sure Icecast mountpoint is reachable from Home Assistant host (`http://...:8000/p25` is valid; no `.mp3` required).
- If your stream codec is not MP3, this card now uses the browser's native format detection from proxy response headers.

If you get `401 Unauthorized` on stream:

- Use `/sdrtrunk_proxy/<entry_id>/stream` in your card `stream_path` (non-API route).
- Update to this latest version of the integration; stream proxy endpoint is exposed without HA auth to support HTML audio clients.
- Then hard refresh browser and re-open the dashboard.

If Home Assistant logs `Login attempt or request with invalid authentication from localhost (127.0.0.1)` when starting audio:

- Verify your integration **Stream URL** is your Icecast server (for example `http://192.168.1.10:8000/p25`) and **not** a Home Assistant URL.
- If you don't use metadata, leave Metadata URL blank in the integration.
- Card now auto-derives metadata only for known integration routes; otherwise metadata polling is disabled to avoid bad auth requests.

If you see `Custom element doesn't exist: sdrtrunk-player-card`:

- Your resource is not being loaded. Add resource in **Dashboard → Edit dashboard → ⋮ → Manage resources**.
- Do **not** put `lovelace:` / `resources:` inside a view/card YAML block.
- If you use YAML mode, `lovelace:` must be at the root in `configuration.yaml`, then restart Home Assistant.
- Hard refresh browser after adding/changing resources.

If you use `type: panel` views:

- Use `card:` (single card), not `cards:`.

Example panel view:

```yaml
views:
  - title: Scanner
    path: scanner
    type: panel
    card:
      type: custom:sdrtrunk-player-card
      title: Police Scanner
      stream_path: /sdrtrunk_proxy/<entry_id>/stream
```

`metadata_path` is optional in the card. If omitted, it auto-uses the same path with `/metadata`.

---

## Notes

- Stream endpoint is available on `/sdrtrunk_proxy/<entry_id>/stream` to avoid `/api` auth issues with browser audio.
- Metadata endpoint remains under `/api/.../metadata` and uses Home Assistant auth.
- No local network IP is required in Lovelace card config.
- If your browser blocks autoplay, click play once manually.

## Roadmap ideas

- Options flow for polling interval
- Support authenticated upstream Icecast endpoints
- Auto-generated card config helper
