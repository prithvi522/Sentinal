from collections import Counter

from app.services.threat_intelligence import ThreatIntelligence
from app.services.ai_provider import ai_provider


class ThreatHunter:
    @staticmethod
    async def analyze_logs(logs: list[dict]) -> dict:
        failed_by_ip = Counter()
        user_agent_counter = Counter()
        ip_activity = Counter()
        login_activity = Counter()
        unusual_agents = Counter()

        for log in logs:
            ip = log["source_ip"]
            ip_activity[ip] += 1
            user_agent_counter[log["user_agent"]] += 1
            login_activity[(ip, log["action"].lower())] += 1
            if log["status"].lower() in {"failed", "denied", "invalid"}:
                failed_by_ip[ip] += 1
            if any(keyword in log["user_agent"].lower() for keyword in ["bot", "curl", "python", "headless", "proxy", "vpn", "tor"]):
                unusual_agents[log["user_agent"]] += 1

        alerts = []
        enriched_alerts = []

        for ip, failed_count in failed_by_ip.items():
            if failed_count >= 5:
                alert = {
                    "type": "brute_force",
                    "source_ip": ip,
                    "severity": "high",
                    "confidence": min(0.99, 0.5 + failed_count / 20),
                    "description": f"{failed_count} failed authentication attempts detected.",
                }
                alert["ip_intel"] = await ThreatIntelligence.enrich_ip(ip)
                alerts.append(alert)
                enriched_alerts.append(alert)

        for (ip, action), count in login_activity.items():
            if action in {"login", "auth", "signin"} and count >= 4:
                alert = {
                    "type": "suspicious_login_activity",
                    "source_ip": ip,
                    "severity": "medium" if count < 8 else "high",
                    "confidence": min(0.98, 0.45 + count / 15),
                    "description": f"Suspicious repeated login activity observed for action '{action}' ({count} events).",
                }
                alert["ip_intel"] = await ThreatIntelligence.enrich_ip(ip)
                alerts.append(alert)
                enriched_alerts.append(alert)

        for ip, activity_count in ip_activity.items():
            if activity_count >= 50:
                alert = {
                    "type": "ddos_like_pattern",
                    "source_ip": ip,
                    "severity": "critical",
                    "confidence": min(0.99, 0.6 + activity_count / 200),
                    "description": f"Traffic burst pattern detected with {activity_count} requests.",
                }
                alert["ip_intel"] = await ThreatIntelligence.enrich_ip(ip)
                alerts.append(alert)
                enriched_alerts.append(alert)

            if 20 <= activity_count < 50:
                alert = {
                    "type": "unusual_traffic_behavior",
                    "source_ip": ip,
                    "severity": "medium",
                    "confidence": min(0.96, 0.35 + activity_count / 100),
                    "description": f"Traffic burst pattern detected with {activity_count} requests; behavior deviates from baseline.",
                    "ip_intel": await ThreatIntelligence.enrich_ip(ip),
                }
                alerts.append(alert)
                enriched_alerts.append(alert)

        for ua, count in user_agent_counter.items():
            if "vpn" in ua.lower() or "proxy" in ua.lower():
                alert = {
                    "type": "vpn_or_proxy_usage",
                    "source_ip": "multiple",
                    "severity": "medium",
                    "confidence": min(0.95, 0.4 + count / 100),
                    "description": f"Potential anonymized traffic detected via user-agent '{ua}'.",
                    "ip_intel": {
                        "ip": "multiple",
                        "malicious": False,
                        "threat_reputation_score": 45,
                        "indicators": ["proxy_or_vpn_user_agent"],
                        "asn": "AS-UNKNOWN",
                        "country": "Unknown",
                        "is_tor": False,
                        "is_proxy": True,
                        "is_vpn": True,
                        "sources": {},
                    },
                }
                alerts.append(alert)
                enriched_alerts.append(alert)

        anomaly_summary = {
            "top_failed_ips": [
                {"ip": ip, "failed_attempts": count}
                for ip, count in failed_by_ip.most_common(5)
            ],
            "unusual_user_agents": [
                {"user_agent": ua, "count": count}
                for ua, count in unusual_agents.most_common(5)
            ],
            "suspicious_login_sources": [
                {"ip": ip, "action": action, "count": count}
                for (ip, action), count in login_activity.most_common(10)
                if action in {"login", "auth", "signin"}
            ],
        }

        threat_score = min(100, sum(30 if a["severity"] == "critical" else 20 if a["severity"] == "high" else 10 for a in alerts))

        fallback = {
            "summary": f"Threat hunting completed with {len(alerts)} alerts and threat score {threat_score}/100.",
            "predicted_next_severity": "high" if threat_score >= 55 else "medium" if threat_score >= 25 else "low",
        }

        ai_result = await ai_provider.complete_json(
            system_prompt="You are a SOC threat hunter summarizing network threats.",
            user_prompt=f"Logs count:{len(logs)}\nAlerts:{alerts}\nThreat score:{threat_score}",
            fallback=fallback,
        )

        return {
            "threat_score": threat_score,
            "alerts": alerts,
            "enriched_alerts": enriched_alerts,
            "summary": ai_result.get("summary", fallback["summary"]),
            "predicted_next_severity": ai_result.get("predicted_next_severity", fallback["predicted_next_severity"]),
            "anomaly_summary": anomaly_summary,
        }
