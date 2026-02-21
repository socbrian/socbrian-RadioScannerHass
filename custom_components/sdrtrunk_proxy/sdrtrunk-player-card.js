class SDRTrunkPlayerCard extends HTMLElement {
  static getStubConfig() {
    return {
      title: "SDRTrunk",
      stream_path: "/sdrtrunk_proxy/YOUR_ENTRY_ID/stream",
      metadata_path: "/api/sdrtrunk_proxy/YOUR_ENTRY_ID/metadata",
      autoplay: false
    };
  }

  setConfig(config) {
    if (!config.stream_path) {
      throw new Error("Set stream_path from the integration entry.");
    }
    const streamCandidates = this._buildStreamCandidates(config.stream_path);
    const inferredMetadataPath = this._inferMetadataPath(config.stream_path);
    this._config = {
      ...config,
      stream_path: streamCandidates[0],
      stream_candidates: streamCandidates,
      metadata_path: config.metadata_path || inferredMetadataPath
    };
    this._render();
    this._setupStreamFallback();
    this._startPolling();
  }

  _buildStreamCandidates(streamPath) {
    const candidates = [streamPath];
    const apiMatch = streamPath.match(/^\/api\/sdrtrunk_proxy\/([^/]+)\/stream$/);
    if (apiMatch) {
      candidates.push(`/sdrtrunk_proxy/${apiMatch[1]}/stream`);
      return candidates;
    }

    const publicMatch = streamPath.match(/^\/sdrtrunk_proxy\/([^/]+)\/stream$/);
    if (publicMatch) {
      candidates.push(`/api/sdrtrunk_proxy/${publicMatch[1]}/stream`);
    }
    return candidates;
  }

  _inferMetadataPath(streamPath) {
    const apiMatch = streamPath.match(/^\/api\/sdrtrunk_proxy\/([^/]+)\/stream$/);
    if (apiMatch) {
      return `/api/sdrtrunk_proxy/${apiMatch[1]}/metadata`;
    }

    const publicMatch = streamPath.match(/^\/sdrtrunk_proxy\/([^/]+)\/stream$/);
    if (publicMatch) {
      return `/api/sdrtrunk_proxy/${publicMatch[1]}/metadata`;
    }

    return null;
  }

  disconnectedCallback() {
    if (this._timer) clearInterval(this._timer);
  }

  _render() {
    this.innerHTML = `
      <ha-card>
        <div style="padding:16px;display:flex;flex-direction:column;gap:8px;">
          <h3 style="margin:0;">${this._config.title || "SDRTrunk"}</h3>
          <audio id="stream" controls playsinline ${this._config.autoplay ? "autoplay" : ""} style="width:100%;" src="${this._config.stream_path}"></audio>
          <div><strong>Talker:</strong> <span id="talker">loading...</span></div>
          <div><strong>Talkgroup:</strong> <span id="talkgroup">-</span></div>
          <div><strong>Source:</strong> <span id="source">-</span></div>
        </div>
      </ha-card>
    `;
  }

  _setupStreamFallback() {
    const audio = this.querySelector("#stream");
    if (!audio) return;

    audio.addEventListener("error", () => {
      const currentIndex = this._config.stream_candidates.indexOf(audio.getAttribute("src"));
      const nextIndex = currentIndex + 1;
      if (nextIndex >= this._config.stream_candidates.length) return;

      const fallbackUrl = this._config.stream_candidates[nextIndex];
      audio.setAttribute("src", fallbackUrl);
      audio.load();
    });
  }

  _startPolling() {
    if (!this._config.metadata_path) {
      this.querySelector("#talker").textContent = "metadata disabled";
      this.querySelector("#talkgroup").textContent = "-";
      this.querySelector("#source").textContent = "-";
      return;
    }

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
