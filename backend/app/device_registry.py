from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class DeviceState(str, Enum):
    DISCOVERED = "discovered"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


@dataclass
class DiscoveredDevice:
    device_id: str         # typically SSID or parsed ID
    device_type: str       # VAEL / SNUU / NOOH
    ssid: str
    rssi: Optional[int]
    state: DeviceState
    last_seen: float
    last_error: Optional[str] = None


class DeviceRegistry:
    """
    Separate from HubStore.
    - Registry tracks DISCOVERED/CONNECTED states (before telemetry).
    - HubStore tracks STREAMING/telemetry once ingest happens.
    """
    def __init__(self):
        self._devices: Dict[str, DiscoveredDevice] = {}

    def upsert(self, d: DiscoveredDevice) -> None:
        self._devices[d.device_id] = d

    def list(self) -> List[DiscoveredDevice]:
        # return sorted by strongest signal (if rssi exists)
        def key(x: DiscoveredDevice):
            return (x.rssi if x.rssi is not None else -999)
        return sorted(self._devices.values(), key=key, reverse=True)

    def get(self, device_id: str) -> Optional[DiscoveredDevice]:
        return self._devices.get(device_id)

    def set_state(self, device_id: str, state: DeviceState, err: Optional[str] = None) -> None:
        d = self._devices.get(device_id)
        if not d:
            return
        d.state = state
        d.last_seen = time.time()
        d.last_error = err


registry = DeviceRegistry()
