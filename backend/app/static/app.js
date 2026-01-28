async function getJSON(url) {
  const r = await fetch(url, { credentials: "include" });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return await r.json();
}

function setText(id, v) {
  const el = document.getElementById(id);
  if (el) el.textContent = v;
}

function setPill(pillId, textId, ok, msg) {
  const pill = document.getElementById(pillId);
  const txt = document.getElementById(textId);
  if (!pill || !txt) return;
  pill.classList.toggle("ok", ok);
  txt.textContent = msg;
}

function setDeviceState(type, state, battery) {
  const status = document.getElementById(`status-${type}`);
  const bat = document.getElementById(`bat-${type}`);
  const hint = document.getElementById(`hint-${type}`);

  if (bat) bat.textContent = battery ?? "—";

  if (!status || !hint) return;

  status.classList.remove("standby","ok","warn","bad");
  if (state === "ok") { status.classList.add("ok"); status.textContent = "Normal"; hint.textContent = "Receiving telemetry"; }
  else if (state === "warn") { status.classList.add("warn"); status.textContent = "Alert"; hint.textContent = "Issues detected"; }
  else if (state === "bad") { status.classList.add("bad"); status.textContent = "Critical"; hint.textContent = "Immediate attention"; }
  else { status.classList.add("standby"); status.textContent = "Standby"; hint.textContent = "Awaiting telemetry…"; }
}

function renderDeviceList(devices) {
  const el = document.getElementById("deviceList");
  if (!el) return;

  const base = ["VAEL","SNUU","NOOH"];
  const byType = {};
  for (const d of devices) byType[d.device_type || d.type || d.kind] = d;

  el.innerHTML = "";
  for (const t of base) {
    const d = byType[t];
    const online = !!d;
    const dotClass = online ? "ok" : "standby";
    const label = online ? "Online" : "Standby";
    const right = online ? (d.connected ? "Online" : "Seen") : "Standby";
    el.insertAdjacentHTML("beforeend", `
      <div class="device-row">
        <span style="display:flex;align-items:center;gap:10px;">
          <span class="dot ${dotClass}"></span> ${t}
        </span>
        <span class="muted">${right}</span>
      </div>
    `);
  }
}

function renderStream(events) {
  const el = document.getElementById("streamList");
  const meta = document.getElementById("streamMeta");
  if (!el) return;

  if (!events || events.length === 0) {
    el.innerHTML = `<div class="stream-empty">Waiting for first telemetry event…</div>`;
    if (meta) meta.textContent = "No events yet";
    return;
  }

  if (meta) meta.textContent = `${events.length} recent events`;
  el.innerHTML = "";
  for (const e of events.slice(0, 6)) {
    const t = e.device_type || e.type || "DEVICE";
    const id = e.device_id || e.id || "—";
    const ts = e.ts ? new Date(e.ts * 1000).toLocaleTimeString() : "—";
    el.insertAdjacentHTML("beforeend", `
      <div class="device-row">
        <span>${t} <span class="muted">(${id})</span></span>
        <span class="muted">${ts}</span>
      </div>
    `);
  }
}

async function tick() {
  // session line
  try {
    const who = await getJSON("/_whoami");
    const uname = who.session?.user || who.session?.u || "user";
    setText("whoamiLine", `Signed in as ${uname}`);
  } catch {
    setText("whoamiLine", `Session unavailable (are you logged in?)`);
  }

  // hub snapshot (this should always render nicely even if empty)
  try {
    const hub = await getJSON("/api/hub");
    setText("hubId", hub.hub_id || "—");
    setText("lastUpdated", new Date().toLocaleTimeString());

    // devices array shape depends on your store; handle common cases
    const devices = hub.devices || hub.device_list || [];
    const onlineCount = devices.length || 0;
    setText("onlineCount", String(onlineCount));

    // issues
    const issues = hub.issues || [];
    setText("issueCount", `${issues.length || 0} Active Issues`);

    // per-device cards (fallback: standby)
    const base = ["VAEL","SNUU","NOOH"];
    for (const t of base) setDeviceState(t, "standby", null);

    for (const d of devices) {
      const t = d.device_type || d.type;
      if (!t) continue;
      const bat = d.battery_pct ?? d.battery ?? null;

      // simple health heuristic for UI (purely presentational)
      let state = "ok";
      if (d.issues && d.issues.length) state = "warn";
      if (d.low_battery) state = "warn";
      setDeviceState(t, state, bat);
    }

    renderDeviceList(devices);

    // stream: if you expose last_events, show them; otherwise keep empty
    renderStream(hub.last_events || hub.events || []);

    // stats (simple UI numbers; real calc later)
    setText("eps", String(hub.eps || 0));
    setText("dataToday", `${hub.data_mb_today || 0.0} MB`);

    setPill("apiStatusPill", "apiStatusText", true, "Operational");
  } catch (e) {
    setPill("apiStatusPill", "apiStatusText", false, `Hub API error`);
  }
}

tick();
setInterval(tick, 2000);
