from pydantic import BaseModel, Field, IPvAnyAddress
from datetime import datetime

class NetworkEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(..., description="Event timestamp")
    src_ip: IPvAnyAddress = Field(..., description="Source IP address")
    dst_ip: IPvAnyAddress = Field(..., description="Destination IP address")
    src_port: int = Field(..., ge=0, le=65535, description="Source port")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination port")
    protocol: str = Field(..., description="Transport protocol (e.g., TCP, UDP)")
    packets: int = Field(..., ge=0, description="Number of packets")
    bytes: int = Field(..., ge=0, description="Total bytes transferred")
    duration_ms: float = Field(..., ge=0.0, description="Duration in milliseconds")
    vlan: int = Field(..., description="VLAN identifier")
    direction: str = Field(..., description="Traffic direction (e.g., INBOUND, OUTBOUND, INTERNAL)")
    event_version: str = Field(..., description="Version of the event schema")
