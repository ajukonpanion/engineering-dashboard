from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Deque, Any, Optional, List
from collections import deque
from datetime import datetime, timedelta

from .models import TelemetryUnion, DeviceStatus, HubSnapshot

@dataclass
class RingBuffer:
    maxlen: int
    items: Deque[dict] = field(default_factory=deque)

    def push(self, x: dict) -> None:
        if self.items.maxlen != self.maxlen:
            self.items = deque(self.items, maxlen=self.maxlen)
        self.items.append(x)

    def to_list(self) -> List[dict]:
        return list(self.items)

class HubStore:
    """
    Purely event-driven: nothing appears unless a device sends telemetry.
    """
    def __init__(self, hub_id: str, max_samples: int):
        self.hub_id = hub_id
        self.max_samples = max_samples

        # status by device_id
        self.status: Dict[str, DeviceStatus] = {}

        # ring buffers by device_id
        self.telemetry: Dict[str, RingBuffer] = {}

        # last raw event for websocket fanout
        self.last_event: Optional[dict] = None

    def upsert_telemetry(self, evt: TelemetryUnion) -> None:
        # status init
        if evt.device_id not in self.status:
            self.status[evt.device_id] = DeviceStatus(
                hub_id=evt.hub_id,
                device_id=evt.device_id,
                device_type=evt.device_type,
                connected=True,
                last_seen=evt.ts,
                battery_pct=evt.battery_pct,
                rssi_dbm=evt.rssi_dbm,
                fw_version=evt.fw_version,
                issues=[]
            )
        else:
            s = self.status[evt.device_id]
            s.connected = True
            s.last_seen = evt.ts
            if evt.battery_pct is not None:
                s.battery_pct = evt.battery_pct
            if evt.rssi_dbm is not None:
                s.rssi_dbm = evt.rssi_dbm
            if evt.fw_version is not None:
                s.fw_version = evt.fw_version

        # validate channel counts (no fake data; only flag issues)
        issues = []
        if evt.device_type == "SNUU":
            if evt.fsr is None:
                issues.append("No FSR payload received.")
            elif len(evt.fsr) != 6:
                issues.append(f"Expected 6 FSR channels, got {len(evt.fsr)}.")
        if evt.device_type == "NOOH":
            if evt.fsr is not None and len(evt.fsr) != 4:
                issues.append(f"Expected 4 FSR channels, got {len(evt.fsr)}.")

        if evt.battery_pct is not None and evt.battery_pct < 15:
            issues.append("Low battery (<15%).")

        # overwrite issues each update (keeps it current)
        self.status[evt.device_id].issues = issues

        # buffer init
        if evt.device_id not in self.telemetry:
            self.telemetry[evt.device_id] = RingBuffer(maxlen=self.max_samples)
        self.telemetry[evt.device_id].push(evt.model_dump())

        self.last_event = evt.model_dump()

    def mark_stale_devices(self, stale_after_s: int = 15) -> None:
        now = datetime.utcnow()
        for s in self.status.values():
            if s.last_seen is None:
                s.connected = False
                continue
            if now - s.last_seen.replace(tzinfo=None) > timedelta(seconds=stale_after_s):
                s.connected = False
                if "Device stale/disconnected." not in s.issues:
                    s.issues = list(dict.fromkeys(s.issues + ["Device stale/disconnected."]))

    def snapshot(self) -> HubSnapshot:
        return HubSnapshot(
            hub_id=self.hub_id,
            ts=datetime.utcnow(),
            devices={k: v for k, v in self.status.items()}
        )

    def get_device_series(self, device_id: str) -> List[dict]:
        rb = self.telemetry.get(device_id)
        return rb.to_list() if rb else []
