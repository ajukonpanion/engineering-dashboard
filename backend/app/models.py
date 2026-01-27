from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict
from datetime import datetime

DeviceType = Literal["VAEL", "SNUU", "NOOH"]

class BaseTelemetry(BaseModel):
    hub_id: str
    device_id: str
    device_type: DeviceType
    ts: datetime = Field(description="Device timestamp or hub-received timestamp")

    rssi_dbm: Optional[int] = None
    battery_pct: Optional[float] = Field(default=None, ge=0, le=100)
    fw_version: Optional[str] = None

class IMUData(BaseModel):
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float

class MicMetrics(BaseModel):
    # Lightweight metrics only (no audio blobs)
    rms: float
    peak: float
    zcr: Optional[float] = None

class VAELTelemetry(BaseTelemetry):
    device_type: Literal["VAEL"] = "VAEL"
    imu: Optional[IMUData] = None
    mic: Optional[MicMetrics] = None

class SNUUTelemetry(BaseTelemetry):
    device_type: Literal["SNUU"] = "SNUU"
    fsr: Optional[List[float]] = Field(default=None, description="6 channels expected")

class NOOHTelemetry(BaseTelemetry):
    device_type: Literal["NOOH"] = "NOOH"
    imu: Optional[IMUData] = None
    mic: Optional[MicMetrics] = None
    fsr: Optional[List[float]] = Field(default=None, description="4 channels expected")
    # optional events, if device sends them
    fall_event: Optional[bool] = None
    fall_confidence: Optional[float] = Field(default=None, ge=0, le=1)

TelemetryUnion = VAELTelemetry | SNUUTelemetry | NOOHTelemetry

class DeviceStatus(BaseModel):
    hub_id: str
    device_id: str
    device_type: DeviceType
    connected: bool
    last_seen: Optional[datetime] = None
    battery_pct: Optional[float] = None
    rssi_dbm: Optional[int] = None
    fw_version: Optional[str] = None
    issues: List[str] = Field(default_factory=list)

class HubSnapshot(BaseModel):
    hub_id: str
    ts: datetime
    devices: Dict[str, DeviceStatus]
