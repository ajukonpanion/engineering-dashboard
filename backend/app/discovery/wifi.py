# backend/app/discovery/wifi.py
from __future__ import annotations

import re
import subprocess
import time
from typing import List, Optional, Tuple

from app.device_registry import DiscoveredDevice, DeviceState, registry

PREFIXES = {
    "VAEL": "VAEL-",
    "SNUU": "SNUU-",
    "NOOH": "NOOH-",
}


def _try_nmcli_scan() -> Optional[List[Tuple[str, Optional[int]]]]:
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    networks = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 2:
            continue
        ssid = parts[0].strip()
        sig = parts[1].strip()
        if not ssid:
            continue
        try:
            rssi = int(sig)
        except Exception:
            rssi = None
        networks.append((ssid, rssi))
    return networks


def _try_iw_scan(iface: str = "wlan0") -> Optional[List[Tuple[str, Optional[int]]]]:
    try:
        out = subprocess.check_output(
            ["sudo", "iw", iface, "scan"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    networks = []
    ssid = None
    signal = None

    for line in out.splitlines():
        line = line.strip()
        if line.startswith("SSID:"):
            ssid = line.split("SSID:", 1)[1].strip()
        elif "signal:" in line:
            m = re.search(r"signal:\s*(-?\d+)", line)
            if m:
                signal = int(m.group(1))
        if ssid is not None:
            networks.append((ssid, signal))
            ssid, signal = None, None

    return networks


def scan_and_update_registry() -> List[DiscoveredDevice]:
    networks = _try_nmcli_scan()
    if networks is None:
        networks = _try_iw_scan()

    if networks is None:
        return registry.list()

    now = time.time()

    for ssid, rssi in networks:
        dtype = None
        for t, prefix in PREFIXES.items():
            if ssid.startswith(prefix):
                dtype = t
                break
        if not dtype:
            continue

        device_id = ssid
        registry.upsert(
            DiscoveredDevice(
                device_id=device_id,
                device_type=dtype,
                ssid=ssid,
                rssi=rssi,
                state=DeviceState.DISCOVERED,
                last_seen=now,
            )
        )

    return registry.list()
