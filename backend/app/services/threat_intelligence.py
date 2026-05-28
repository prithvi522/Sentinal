from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelResult:
    ip: str
    malicious: bool
    threat_reputation_score: int
    indicators: list[str]
    asn: str
    country: str
    is_tor: bool
    is_proxy: bool
    is_vpn: bool
    sources: dict

    def as_dict(self) -> dict:
        return {
            "ip": self.ip,
            "malicious": self.malicious,
            "threat_reputation_score": self.threat_reputation_score,
            "indicators": self.indicators,
            "asn": self.asn,
            "country": self.country,
            "is_tor": self.is_tor,
            "is_proxy": self.is_proxy,
            "is_vpn": self.is_vpn,
            "sources": self.sources,
        }


class ThreatIntelligence:
    @staticmethod
    def _threatfox_endpoint() -> str | None:
        value = settings.threatfox_api_key
        if not value:
            return None
        if value.startswith("http://") or value.startswith("https://"):
            return value
        return "https://threatfox-api.abuse.ch/api/v1/"

    @staticmethod
    def _basic_ip_profile(ip: str, user_agent: str | None = None) -> ThreatIntelResult:
        indicators: list[str] = []
        sources: dict[str, dict] = {}
        score = 10

        try:
            parsed = ipaddress.ip_address(ip)
            if parsed.is_private or parsed.is_loopback or parsed.is_reserved:
                score += 25
                indicators.append("internal_or_reserved_ip")
        except ValueError:
            score += 15
            indicators.append("invalid_ip_format")

        fingerprint = f"{ip} {user_agent or ''}".lower()
        is_tor = bool(re.search(r"\btor\b", fingerprint))
        is_proxy = bool(re.search(r"\bproxy\b", fingerprint))
        is_vpn = bool(re.search(r"\bvpn\b|wireguard|openvpn|l2tp", fingerprint))

        if is_tor:
            score += 30
            indicators.append("tor_indicator")
        if is_proxy:
            score += 20
            indicators.append("proxy_indicator")
        if is_vpn:
            score += 15
            indicators.append("vpn_indicator")

        asn = "AS-UNKNOWN"
        country = "Unknown"
        malicious = score >= 50

        return ThreatIntelResult(
            ip=ip,
            malicious=malicious,
            threat_reputation_score=min(100, score),
            indicators=indicators,
            asn=asn,
            country=country,
            is_tor=is_tor,
            is_proxy=is_proxy,
            is_vpn=is_vpn,
            sources=sources,
        )

    @staticmethod
    async def enrich_ip(ip: str, user_agent: str | None = None) -> dict:
        result = ThreatIntelligence._basic_ip_profile(ip, user_agent=user_agent)
        sources = result.sources
        threatfox_endpoint = ThreatIntelligence._threatfox_endpoint()

        async with httpx.AsyncClient(timeout=10.0) as client:
            if settings.virustotal_api_key:
                try:
                    response = await client.get(
                        f"https://www.virustotal.com/api/v3/ip_addresses/{ip}",
                        headers={"x-apikey": settings.virustotal_api_key},
                    )
                    if response.status_code == 200:
                        payload = response.json().get("data", {}).get("attributes", {})
                        sources["virustotal"] = payload
                        result.threat_reputation_score = min(100, max(result.threat_reputation_score, int(payload.get("last_analysis_stats", {}).get("malicious", 0) * 20)))
                        result.malicious = result.malicious or result.threat_reputation_score >= 50
                except Exception as exc:
                    logger.exception("VirusTotal lookup failed for %s: %s", ip, exc)

            if threatfox_endpoint:
                try:
                    response = await client.post(
                        threatfox_endpoint,
                        json={"query": "search_ioc", "search_term": ip},
                        headers={"Content-Type": "application/json"},
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        sources["threatfox"] = payload
                        if isinstance(payload, dict):
                            matches = payload.get("data", []) if isinstance(payload.get("data"), list) else payload.get("data") or []
                            if matches:
                                result.threat_reputation_score = min(100, max(result.threat_reputation_score, 60))
                                result.malicious = True
                                result.indicators.append("threatfox_ioc_match")
                except Exception as exc:
                    logger.exception("ThreatFox lookup failed for %s: %s", indicator if kind != 'ip' else ip, exc)

            if settings.abuseipdb_api_key:
                try:
                    response = await client.get(
                        "https://api.abuseipdb.com/api/v2/check",
                        params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": "true"},
                        headers={"Key": settings.abuseipdb_api_key, "Accept": "application/json"},
                    )
                    if response.status_code == 200:
                        payload = response.json().get("data", {})
                        sources["abuseipdb"] = payload
                        abuse_score = int(float(payload.get("abuseConfidenceScore", 0)))
                        result.threat_reputation_score = max(result.threat_reputation_score, abuse_score)
                        result.malicious = result.malicious or abuse_score >= 50
                except Exception as exc:
                    logger.exception("AbuseIPDB lookup failed for %s: %s", ip, exc)

            if settings.shodan_api_key:
                try:
                    response = await client.get(
                        f"https://api.shodan.io/shodan/host/{ip}",
                        params={"key": settings.shodan_api_key},
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        sources["shodan"] = payload
                        result.asn = payload.get("asn", result.asn)
                        result.country = payload.get("country_name", result.country)
                        result.threat_reputation_score = min(100, result.threat_reputation_score + 10)
                except Exception as exc:
                    logger.exception("Shodan lookup failed for %s: %s", ip, exc)

        return result.as_dict()

    @staticmethod
    async def analyze_indicator(indicator: str, kind: str = "ip", user_agent: str | None = None) -> dict:
        if kind == "ip":
            return await ThreatIntelligence.enrich_ip(indicator, user_agent=user_agent)

        score = 20
        indicators = [f"{kind}_observed"]
        if kind == "domain" and re.search(r"(malware|phish|dump|steal|login|secure|verify|update)", indicator, re.IGNORECASE):
            score += 40
            indicators.append("suspicious_domain_keyword")

        sources = {}
        threatfox_endpoint = ThreatIntelligence._threatfox_endpoint()
        if threatfox_endpoint:
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.post(
                        threatfox_endpoint,
                        json={"query": "search_ioc", "search_term": indicator},
                        headers={"Content-Type": "application/json"},
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        sources["threatfox"] = payload
                        if payload:
                            score = max(score, 65)
                            indicators.append("threatfox_match")
                except Exception:
                    pass

        return {
            "indicator": indicator,
            "kind": kind,
            "malicious": score >= 50,
            "threat_reputation_score": min(100, score),
            "indicators": indicators,
            "asn": "AS-UNKNOWN",
            "country": "Unknown",
            "is_tor": False,
            "is_proxy": False,
            "is_vpn": False,
            "sources": sources,
        }