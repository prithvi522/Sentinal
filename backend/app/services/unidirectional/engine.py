from __future__ import annotations

import asyncio
import hashlib
import math
import random
import time
import uuid
from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any

from app.db.session import SessionLocal
from app.models.threat_event import ThreatEvent
from app.services.websocket_manager import ConnectionManager


SCENARIOS = {
    "normal": "Normal traffic",
    "ddos": "Volumetric / protocol DDoS",
    "c2": "Botnet C2 beaconing",
    "dga": "DGA / DNS tunneling",
    "port_scan": "Reconnaissance / port scanning",
    "tls_malware": "TLS / QUIC metadata anomaly",
    "exfiltration": "Potential data exfiltration",
    "mixed": "Mixed attack traffic",
}

MITRE = {
    "DDoS": [{"id": "T1498", "name": "Network Denial of Service"}],
    "C2 Beaconing": [{"id": "T1071", "name": "Application Layer Protocol"}],
    "DGA / DNS Tunneling": [{"id": "T1071.004", "name": "DNS"}],
    "Port Scan": [{"id": "T1046", "name": "Network Service Scanning"}],
    "Encrypted Session Anomaly": [{"id": "T1071", "name": "Application Layer Protocol"}],
    "Potential Exfiltration": [{"id": "T1041", "name": "Exfiltration Over C2 Channel"}],
}


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    size = len(value)
    return -sum((count / size) * math.log2(count / size) for count in counts.values())


class PassiveTrafficEngine:
    """Offline telemetry processor. It never opens sockets or transmits packets."""

    def __init__(self) -> None:
        self.mode = "STOPPED"
        self.scenario = "normal"
        self.speed = 1.0
        self.packet_count = 0
        self.flow_count = 0
        self.alert_count = 0
        self.security_score = 98
        self.events: deque[dict[str, Any]] = deque(maxlen=80)
        self.alerts: deque[dict[str, Any]] = deque(maxlen=50)
        self.task: asyncio.Task | None = None
        self.ws = ConnectionManager()

    def overview(self) -> dict[str, Any]:
        protocol_counts = Counter(item["protocol"] for item in self.events)
        total_bytes = sum(item["size"] for item in self.events)
        return {
            "air_gap": {"mode": "PASSIVE", "read_only": True, "ingress_only": True, "return_path": "BLOCKED", "active_probes": 0, "packet_injection": 0, "payload_decryption": "DISABLED", "outbound_network_requests": 0},
            "simulation": {"mode": self.mode, "scenario": self.scenario, "speed": self.speed, "packets_generated": self.packet_count, "flows_analyzed": self.flow_count, "threats_detected": self.alert_count},
            "traffic": {"packets_per_second": len(self.events), "bytes_per_second": total_bytes, "total_packets": self.packet_count, "total_flows": self.flow_count, "protocols": dict(protocol_counts)},
            "security_score": self.security_score,
            "packets": list(self.events)[-24:][::-1],
            "alerts": list(self.alerts)[-20:],
        }

    async def start(self, scenario: str, speed: float = 1.0) -> dict[str, Any]:
        if scenario not in SCENARIOS:
            raise ValueError("Unsupported simulation scenario")
        await self.stop()
        self.scenario, self.speed, self.mode = scenario, max(0.5, min(float(speed), 5.0)), "RUNNING"
        self.task = asyncio.create_task(self._run())
        return self.overview()

    async def pause(self) -> dict[str, Any]:
        self.mode = "PAUSED"
        return self.overview()

    async def stop(self) -> dict[str, Any]:
        self.mode = "STOPPED"
        if self.task and self.task is not asyncio.current_task():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.task = None
        return self.overview()

    def reset(self) -> dict[str, Any]:
        self.packet_count = self.flow_count = self.alert_count = 0
        self.security_score = 98
        self.events.clear()
        self.alerts.clear()
        return self.overview()

    async def _run(self) -> None:
        while self.mode != "STOPPED":
            if self.mode == "RUNNING":
                await self.process_batch()
            await asyncio.sleep(1 / self.speed)

    async def process_batch(self) -> None:
        batch = [self._synthetic_flow() for _ in range(5 if self.scenario == "normal" else 12)]
        for flow in batch:
            self.events.append(flow["packet"])
            self.packet_count += flow["packets"]
            self.flow_count += 1
            alert = self._detect(flow)
            if alert:
                self.alerts.appendleft(alert)
                self.alert_count += 1
                self.security_score = max(15, self.security_score - (8 if alert["severity"] in {"HIGH", "CRITICAL"} else 3))
                self._persist_alert(alert)
                await self.ws.broadcast_json({"channel": "unidirectional_alert", "payload": alert})
        await self.ws.broadcast_json({"channel": "unidirectional_update", "payload": self.overview()})

    def _synthetic_flow(self) -> dict[str, Any]:
        scenario = self.scenario
        if scenario == "mixed":
            scenario = random.choice(["ddos", "c2", "dga", "port_scan", "tls_malware", "exfiltration"])
        source = f"10.10.{random.randint(1, 12)}.{random.randint(2, 240)}"
        destination = f"172.20.{random.randint(1, 6)}.{random.randint(2, 240)}"
        flow: dict[str, Any] = {"scenario": scenario, "source_ip": source, "destination_ip": destination, "protocol": "TCP", "destination_port": 443, "packets": random.randint(4, 18), "bytes": random.randint(800, 12000), "duration": random.uniform(1, 14), "distinct_ports": 1, "fan_out": 1, "interval_cv": 0.8, "domain": "updates.internal", "tls_metadata": False, "upload_ratio": 0.4}
        if scenario == "ddos":
            flow.update(protocol="UDP", packets=random.randint(900, 1800), bytes=random.randint(2_000_000, 7_000_000), duration=random.uniform(0.8, 1.5), fan_out=1)
        elif scenario == "c2":
            flow.update(packets=47, bytes=18800, duration=30.1, interval_cv=0.026, destination_port=443, tls_metadata=True)
        elif scenario == "dga":
            label = "x9q" + "a7" * 12 + "m"
            flow.update(protocol="DNS", destination_port=53, packets=64, bytes=21000, duration=3.2, domain=f"{label}.command.example", dns_rate=20)
        elif scenario == "port_scan":
            flow.update(packets=80, bytes=6400, duration=2.1, distinct_ports=random.randint(18, 44), fan_out=random.randint(12, 38), tcp_syn_ratio=0.94)
        elif scenario == "tls_malware":
            flow.update(protocol="TLS", packets=180, bytes=96000, duration=2.5, interval_cv=0.06, tls_metadata=True, ja3="unrecognized", destination_port=443)
        elif scenario == "exfiltration":
            flow.update(protocol="HTTPS", packets=780, bytes=random.randint(9_000_000, 18_000_000), duration=22, upload_ratio=0.96, destination_port=443)
        packet = {"time": datetime.now(timezone.utc).isoformat(), "source": source, "destination": destination, "protocol": flow["protocol"], "size": flow["bytes"], "risk": "LOW"}
        flow["packet"] = packet
        return flow

    def _detect(self, flow: dict[str, Any]) -> dict[str, Any] | None:
        checks = [
            ("DDoS", flow["packets"] / max(flow["duration"], 0.1) > 500, ["packet rate spike", f"{flow['packets']} packets in {flow['duration']:.1f}s"]),
            ("C2 Beaconing", flow["interval_cv"] < 0.08 and flow["packets"] >= 40, [f"interval coefficient of variation {flow['interval_cv']:.3f}", "repeated destination cadence"]),
            ("DGA / DNS Tunneling", flow["protocol"] == "DNS" and _entropy(flow["domain"].split(".")[0]) > 2.8, [f"domain entropy {_entropy(flow['domain'].split('.')[0]):.2f}", "high DNS query frequency"]),
            ("Port Scan", flow["distinct_ports"] >= 16 or flow["fan_out"] >= 12, [f"{flow['distinct_ports']} destination ports", f"fan-out {flow['fan_out']}"]),
            ("Encrypted Session Anomaly", flow["tls_metadata"] and flow["interval_cv"] < 0.08 and flow["packets"] > 100, ["TLS metadata timing anomaly", "payload decryption was not performed"]),
            ("Potential Exfiltration", flow["upload_ratio"] > 0.9 and flow["bytes"] > 5_000_000, [f"{flow['bytes']} outbound-like bytes", f"upload ratio {flow['upload_ratio']:.2f}"]),
        ]
        for threat, matched, evidence in checks:
            if matched:
                confidence = round(min(97.0, 72 + len(evidence) * 8 + random.random() * 7), 1)
                severity = "CRITICAL" if confidence >= 93 else "HIGH"
                alert = {"alert_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc).isoformat(), "flow_id": hashlib.sha256(f"{flow['source_ip']}{flow['destination_ip']}{time.time_ns()}".encode()).hexdigest()[:16], "threat_class": threat, "severity": severity, "confidence": confidence, "source_ip": flow["source_ip"], "destination_ip": flow["destination_ip"], "protocol": flow["protocol"], "model": "rules-fusion-v1", "evidence": {"indicators": evidence, "packets": flow["packets"], "bytes": flow["bytes"], "duration_seconds": round(flow["duration"], 2)}, "detection_rules": [threat.lower().replace(" ", "_")], "status": "OPEN", "mitre": MITRE.get(threat, []), "latency_ms": {"ingestion": 1, "features": 1, "ml": 0, "fusion": 1, "total": 3}}
                flow["packet"]["risk"] = severity
                return alert
        return None

    def _persist_alert(self, alert: dict[str, Any]) -> None:
        db = SessionLocal()
        try:
            db.add(ThreatEvent(event_type=alert["threat_class"], source_ip=alert["source_ip"], severity=alert["severity"], confidence=alert["confidence"], description="Passive unidirectional traffic detection", event_metadata=alert))
            db.commit()
        finally:
            db.close()


traffic_engine = PassiveTrafficEngine()
