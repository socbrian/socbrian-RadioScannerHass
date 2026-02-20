class SDRTrunkPlayerCard extends HTMLElement {
  static getStubConfig() {
    return {
      title: "SDRTrunk",
      stream_path: "/api/sdrtrunk_proxy/YOUR_ENTRY_ID/stream",
      metadata_path: "/api/sdrtrunk_proxy/YOUR_ENTRY_ID/metadata",
      autoplay: false
    };
  }

  setConfig(config) {
    if (!config.stream_path) {
      throw new Error("Set stream_path from the integration entry.");
    }
    this._config = {
      ...config,
      metadata_path: config.metadata_path || config.stream_path.replace(/\/stream$/, "/metadata")
    };
    this._render();
    this._startPolling();
  }

  disconnectedCallback() {
    if (this._timer) clearInterval(this._timer);
  }

  _render() {
    this.innerHTML = `
      <ha-card>
        <div style="padding:16px;display:flex;flex-direction:column;gap:8px;">
          <h3 style="margin:0;">${this._config.title || "SDRTrunk"}</h3>
          <audio controls ${this._config.autoplay ? "autoplay" : ""} style="width:100%;">
            <source src="${this._config.stream_path}" type="audio/mpeg" />
          </audio>
          <div><strong>Talker:</strong> <span id="talker">loading...</span></div>
          <div><strong>Talkgroup:</strong> <span id="talkgroup">-</span></div>
          <div><strong>Source:</strong> <span id="source">-</span></div>
        </div>
      </ha-card>
    `;
  }

  _startPolling() {
    this._updateMetadata();
    if (this._timer) clearInterval(this._timer);
    this._timer = setInterval(() => this._updateMetadata(), 2000);
  }

  async _updateMetadata() {
    try {
      const response = await fetch(this._config.metadata_path, { credentials: "same-origin" });
      if (!response.ok) return;
      const data = await response.json();
      this.querySelector("#talker").textContent = data.talker || "idle";
      this.querySelector("#talkgroup").textContent = data.talkgroup || "-";
      this.querySelector("#source").textContent = data.source || "-";
    } catch (_err) {
      this.querySelector("#talker").textContent = "unavailable";
    }
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("sdrtrunk-player-card", SDRTrunkPlayerCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "sdrtrunk-player-card",
  name: "SDRTrunk Player Card",
  description: "Play proxied SDRTrunk audio and show active talker metadata."
});
