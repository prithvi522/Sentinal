"""Generate the SentinelAI OS passive-traffic feature guide PDF."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "SentinelAI_OS_Passive_Traffic_Feature_Guide.pdf"

NAVY = colors.HexColor("#071426")
CYAN = colors.HexColor("#17C7DE")
LIME = colors.HexColor("#A3E635")
INK = colors.HexColor("#152235")
MUTED = colors.HexColor("#52657A")
PALE = colors.HexColor("#EDF7FA")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(CYAN)
    canvas.line(1.6 * cm, 1.35 * cm, 19.4 * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.6 * cm, 0.85 * cm, "SENTINELAI OS  |  SIH26145  |  PASSIVE DEFENCE INTELLIGENCE")
    canvas.drawRightString(19.4 * cm, 0.85 * cm, f"Page {doc.page}")
    canvas.restoreState()


def p(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return [p(f"• {item}", style) for item in items]


def table(rows, widths):
    result = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#BED6DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def build():
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27,
                           leading=32, textColor=NAVY, spaceAfter=10)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=12, leading=17,
                              textColor=MUTED, spaceAfter=18)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18,
                        leading=23, textColor=NAVY, spaceBefore=8, spaceAfter=10)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12,
                        leading=15, textColor=CYAN, spaceBefore=9, spaceAfter=5)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.5, leading=14,
                          textColor=INK, spaceAfter=6)
    small = ParagraphStyle("Small", parent=body, fontSize=8.5, leading=12, textColor=MUTED)
    centered = ParagraphStyle("Centered", parent=body, alignment=TA_CENTER, fontSize=11, leading=15)

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.8 * cm, title="SentinelAI OS Feature Guide")
    story = [Spacer(1, 2.0 * cm), p("SENTINELAI OS", ParagraphStyle("Brand", parent=body, textColor=CYAN, fontName="Helvetica-Bold", fontSize=12, alignment=TA_CENTER)),
             Spacer(1, 0.3 * cm), p("Passive Traffic Intelligence", title),
             p("Feature Guide and Working Capability Overview", ParagraphStyle("CoverSub", parent=subtitle, alignment=TA_CENTER)),
             Spacer(1, 0.5 * cm), p("SIH26145 · Unidirectional Data-Diode Cybersecurity Pipeline", centered),
             Spacer(1, 1.1 * cm),
             table([[p("OPERATING PRINCIPLE", body)], [p("Production traffic is observed through a one-way TAP or data diode. SentinelAI OS transforms passive packet and flow metadata into evidence-backed security intelligence, without probing, decrypting, blocking, or transmitting into the production network.", body)]], [17.8 * cm]),
             Spacer(1, 0.8 * cm), p("Working prototype · Streaming telemetry · Dashboard alerts · Metadata-only analysis", centered), PageBreak()]

    story += [p("1. Solution overview", h1),
              p("SentinelAI OS provides a monitoring-enclave pipeline for critical infrastructure gateways and peering links. It accepts packet captures, live passive interface observations, and normalized NetFlow/IPFIX/sFlow-style records; incrementally extracts metadata features; applies statistical, heuristic, and local anomaly scoring; then streams structured alerts to the SOC dashboard.", body),
              p("Passive security boundary", h2)]
    story += bullets([
        "Read-only ingest: data is received from a capture source, TAP, or one-way diode with no production return path.",
        "No active interaction: no probes, handshakes, packet injection, containment commands, or source/destination callbacks.",
        "No payload decryption: TLS and QUIC-oriented analysis is based solely on observable metadata and fingerprint fields.",
        "Forensic-ready workflow: flow and alert metadata are persisted with timestamps, identifiers, confidence, severity, and evidence.",
    ], body)
    story += [Spacer(1, 0.2 * cm), p("Architecture", h2),
              table([[p("Stage", body), p("Working capability", body)],
                     [p("1. Passive observation", body), p("PCAP upload/parser, Scapy capture on an approved ingest interface, and normalized flow-record API.", body)],
                     [p("2. Streaming pipeline", body), p("Bounded queues and background workers process observations incrementally and broadcast updates through WebSockets.", body)],
                     [p("3. Feature extraction", body), p("Rates, timing, entropy, DNS naming traits, port/host fan-out, byte asymmetry, SYN rate, and encrypted-session metadata.", body)],
                     [p("4. Detection & scoring", body), p("Threat heuristics are fused with statistical and optional local Isolation Forest anomaly scoring.", body)],
                     [p("5. SOC intelligence", body), p("Persisted structured alerts and a live dashboard show severity, confidence, evidence, flows, and pipeline state.", body)]], [4.0 * cm, 13.8 * cm]), PageBreak()]

    story += [p("2. Threat detection capabilities", h1),
              p("The prototype delivers the following detection categories through the same passive processing path used by simulated, replayed, uploaded-PCAP, and flow-record inputs.", body),
              table([[p("Threat class", body), p("Passive indicators used", body), p("Intelligence output", body)],
                     [p("Volumetric / protocol DDoS", body), p("Packets-per-second, bytes-per-second, SYN rate, protocol profile, high-rate flow characteristics.", body), p("SYN flood, UDP amplification, and spoofed-source-flood alerts with measured rates.", body)],
                     [p("Botnet C2 beaconing", body), p("Inter-arrival mean and standard deviation; recurring low-variance flow timing.", body), p("C2 beacon alert with periodicity evidence and confidence score.", body)],
                     [p("DGA and DNS tunnelling", body), p("DNS-label entropy, uncommon character n-grams, digit ratio, query length, and query frequency.", body), p("DGA or DNS tunnel alert showing anomalous domain/query features.", body)],
                     [p("Encrypted-session malware", body), p("JA3/JA3S/JA4-ready fields, TLS version/cipher fields, packet count, timing regularity, and port 443 metadata.", body), p("Encrypted-session anomaly alert; no plaintext inspection or decryption.", body)],
                     [p("Reconnaissance / scanning", body), p("Unique destination ports, unique destination hosts, flow fan-out, and scan velocity.", body), p("Reconnaissance alert with affected-port/host evidence.", body)],
                     [p("Data exfiltration", body), p("Protected-network direction, outbound/inbound byte counts, byte ratio, and high-volume flow behavior.", body), p("Data-exfiltration alert with byte-volume and asymmetry evidence.", body)]], [3.35 * cm, 8.15 * cm, 6.3 * cm]),
              Spacer(1, 0.25 * cm), p("All detections are passive observations. Recommended actions are investigation and evidence preservation—not inline intervention.", small), PageBreak()]

    story += [p("3. Models, features, and scoring", h1),
              p("SentinelAI OS uses a practical ensemble approach suitable for an offline monitoring enclave. Deterministic rules provide immediate coverage while statistical and ML-assisted scoring establish additional anomaly context.", body),
              p("Feature engineering", h2)]
    story += bullets([
        "Flow volume: packet count, byte count, duration, packets/second, and bytes/second.",
        "Timing: mean and standard deviation of inter-arrival time, enabling beacon regularity analysis.",
        "Network behavior: distinct ports and destinations, protocol, TCP SYN rate, and direction.",
        "DNS behavior: query labels, entropy, n-gram rarity, query length, frequency, and record-type metadata.",
        "Encrypted metadata: JA3, JA3S, JA4, TLS version, cipher fields, packet timing, and packet-size/rate context.",
        "Exfiltration behavior: outbound and inbound bytes plus outbound-to-inbound ratio.",
    ], body)
    story += [p("Inference and confidence", h2), p("Rules emit per-threat scores from observed evidence. The fusion stage selects the highest-scoring applicable detection, maps it to LOW/MEDIUM/HIGH/CRITICAL severity, and produces a confidence score. A local Isolation Forest can be fitted after benign observations are collected, providing an additional metadata-only anomaly score without a cloud dependency.", body),
              p("Alert schema", h2), table([[p("Required field", body), p("Provided by SentinelAI OS", body)],
                                               [p("Timestamp", body), p("UTC event timestamp" , body)], [p("Flow identifier", body), p("Stable generated or supplied flow ID", body)], [p("Threat class", body), p("Normalized detection label", body)], [p("Confidence score", body), p("0–1 fused confidence plus risk score/severity", body)], [p("Supporting evidence", body), p("Detection features, rates, entropy, timing, byte ratios, and model/detection method", body)]], [5.0 * cm, 12.8 * cm]), PageBreak()]

    story += [p("4. Dashboard and operational workflow", h1),
              p("The Unidirectional Defense dashboard presents the live passive-traffic operating picture for analysts.", body)]
    story += bullets([
        "Data-diode status panel: read-only state, inbound-only direction, return-path blocked, zero active probes, and decryption disabled.",
        "Live flow stream: source/destination, protocol, byte count, packet rate, and timestamped metadata observations.",
        "Threat investigation queue: threat class, severity, confidence percentage, source/destination, detection method, and supporting evidence.",
        "PCAP analysis: upload a capture and create metadata-only flow and alert results without replaying traffic.",
        "Live passive ingest: select an allow-listed TAP/data-diode receive interface and start bounded passive capture.",
        "Replay and simulation: demonstrate normal traffic and each attack category through the real detector path.",
        "WebSocket updates: dashboard metrics, flows, and alerts update in near real time.",
    ], body)
    story += [p("Input and deployment options", h2), table([[p("Input", body), p("Use", body)],
                [p("PCAP/PCAPNG/CAP", body), p("Offline forensic or replay analysis; only metadata is retained for detection.", body)],
                [p("Live capture NIC", body), p("Passive receive-side interface for a TAP or data diode. Interface allow-listing is supported.", body)],
                [p("Normalized flow API", body), p("Integration point for NetFlow, IPFIX, sFlow, or an enclave-side collector/diode relay.", body)],
                [p("Synthetic/replay feed", body), p("Safe functional demonstrations, analyst training, and controlled scenario validation.", body)]], [4.8 * cm, 13.0 * cm]), PageBreak()]

    story += [p("5. Performance, validation, and deployment", h1),
              p("The pipeline is designed for incremental processing rather than end-of-run reporting. The runtime exposes a local benchmark operation that sends a chosen number of flows through the real passive analysis path and records elapsed time and measured flows per second.", body),
              p("Throughput demonstration", h2),
              table([[p("Metric", body), p("Working implementation", body)],
                     [p("Throughput unit", body), p("Measured flows per second, with packets/second and bytes/second also visible on the dashboard.", body)],
                     [p("Benchmark path", body), p("On-demand benchmark endpoint exercises feature extraction, inference, persistence, and alert output locally.", body)],
                     [p("Latency design", body), p("Bounded ingest queue plus background worker processing and live WebSocket delivery.", body)],
                     [p("Operational protection", body), p("Bounded capture and analysis queues report depth and preserve capture continuity if downstream analysis is degraded.", body)]], [5.0 * cm, 12.8 * cm]),
              p("Validation approach", h2), p("Functional validation uses synthetic scenarios for normal traffic, SYN flood, UDP amplification, spoofed-source flood, C2, DGA, DNS tunnelling, encrypted-session anomaly, port/host scan, and exfiltration. The repository also contains focused unit coverage for the required demo categories. In a deployment, local benchmark results should be recorded for the actual enclave hardware and traffic profile.", body),
              p("Deployment checklist", h2)]
    story += bullets([
        "Place SentinelAI OS in the monitoring enclave only; connect its capture NIC to the receive side of the TAP/data diode.",
        "Configure UNIDIRECTIONAL_ALLOWED_INTERFACES with approved receive-only interfaces.",
        "Configure UNIDIRECTIONAL_PROTECTED_CIDRS to enable direction-aware exfiltration analysis.",
        "Ensure there is no route, management tunnel, packet injection capability, or mitigation integration back into production.",
        "Use PCAP/replay and the benchmark workflow to demonstrate expected detection behavior and measured flows-per-second capacity.",
    ], body)
    story += [Spacer(1, 0.4 * cm), p("Conclusion", h2), p("SentinelAI OS delivers a working passive cybersecurity intelligence prototype for one-directional critical-infrastructure monitoring. It ingests observable traffic metadata, detects and scores the required threat classes in near real time, and provides structured, evidence-backed analyst alerts through a live dashboard—while maintaining the read-only, no-decryption, no-return-path security boundary.", body)]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
