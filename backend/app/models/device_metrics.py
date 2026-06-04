"""
Device Metrics Model - Network Device Performance Metrics
Stores CPU, RAM, traffic, and other device metrics
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from app import db

class DeviceMetrics(db.Model):
    """
    Device metrics model for storing performance data.
    
    Records CPU, RAM, disk, traffic, and other metrics from
    network devices. Allows historical analysis and trend reporting.
    
    Attributes:
        id: Unique metric identifier
        tenant_id: Tenant this metric belongs to
        device_id: Associated network device
        cpu_percent: CPU usage percentage
        ram_used: RAM used in MB
        ram_total: Total RAM in MB
        disk_used: Disk used in MB
        disk_total: Total disk in MB
        rx_bytes: Bytes received
        tx_bytes: Bytes transmitted
        rx_errors: RX errors
        tx_errors: TX errors
        rx_packets: RX packets
        tx_packets: TX packets
        uptime: Device uptime in seconds
        additional_metrics: JSON field for additional metrics
        recorded_at: When metrics were recorded
        created_date: When metric record was created
        updated_date: When metric record was last updated
    """
    __tablename__ = 'device_metrics'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    tenant_id = Column(BigInteger, ForeignKey('tenants.id'), nullable=False, index=True)
    device_id = Column(BigInteger, ForeignKey('network_devices.id'), nullable=False, index=True)
    
    # CPU and Memory Metrics
    cpu_percent = Column(Numeric(5, 2), nullable=True)  # 0-100
    ram_used = Column(BigInteger, nullable=True)  # MB
    ram_total = Column(BigInteger, nullable=True)  # MB
    
    # Disk Metrics
    disk_used = Column(BigInteger, nullable=True)  # MB
    disk_total = Column(BigInteger, nullable=True)  # MB
    
    # Network Metrics
    rx_bytes = Column(BigInteger, nullable=True)
    tx_bytes = Column(BigInteger, nullable=True)
    rx_errors = Column(BigInteger, nullable=True)
    tx_errors = Column(BigInteger, nullable=True)
    rx_packets = Column(BigInteger, nullable=True)
    tx_packets = Column(BigInteger, nullable=True)
    
    # System Metrics
    uptime = Column(BigInteger, nullable=True)  # Seconds
    
    # Additional Metrics (JSON for flexibility)
    additional_metrics = Column(JSON, nullable=True)
    
    # Recording Timestamp
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<DeviceMetrics(id={self.id}, device_id={self.device_id}, cpu={self.cpu_percent}%)>"
    
    def to_dict(self):
        """Convert device metrics to dictionary representation."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'device_id': self.device_id,
            'cpu_percent': float(self.cpu_percent) if self.cpu_percent else None,
            'ram_used': self.ram_used,
            'ram_total': self.ram_total,
            'disk_used': self.disk_used,
            'disk_total': self.disk_total,
            'rx_bytes': self.rx_bytes,
            'tx_bytes': self.tx_bytes,
            'rx_errors': self.rx_errors,
            'tx_errors': self.tx_errors,
            'rx_packets': self.rx_packets,
            'tx_packets': self.tx_packets,
            'uptime': self.uptime,
            'additional_metrics': self.additional_metrics,
            'recorded_at': self.recorded_at.isoformat(),
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat()
        }
