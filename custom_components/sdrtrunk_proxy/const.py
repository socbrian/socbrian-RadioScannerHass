"""Constants for the SDRTrunk Proxy integration."""

from datetime import timedelta

DOMAIN = "sdrtrunk_proxy"
PLATFORMS = ["sensor"]

CONF_NAME = "name"
CONF_STREAM_URL = "stream_url"
CONF_METADATA_URL = "metadata_url"

DEFAULT_NAME = "SDRTrunk"
UPDATE_INTERVAL = timedelta(seconds=2)
STATIC_PATH = "/api/sdrtrunk_proxy/static"
