from typing import Any, Dict

from scapy.all import ICMP, TCP, UDP, Raw, rdpcap

from backend.config.logging_config import get_logger

logger = get_logger(__name__)

class NetworkAnalysisService:
    def __init__(self):
        # We will parse basic anomalies
        self.suspicious_ports = {4444, 3389, 23, 21, 6667}

    def analyze_pcap(self, file_path: str) -> Dict[str, Any]:
        """
        Reads a PCAP file and performs basic heuristic anomaly detection.
        Returns a dictionary of statistics and anomalies.
        """
        logger.info(f"Starting PCAP analysis on {file_path}")
        
        try:
            packets = rdpcap(file_path)
        except Exception as e:
            logger.error(f"Failed to read PCAP: {e}")
            raise ValueError(f"Invalid PCAP file: {e}")

        total_packets = len(packets)
        tcp_count = 0
        udp_count = 0
        icmp_count = 0
        other_count = 0
        
        anomalies = []
        port_hits = set()

        for pkt in packets:
            # Protocol distribution
            if pkt.haslayer(TCP):
                tcp_count += 1
                if pkt[TCP].dport in self.suspicious_ports:
                    port_hits.add(pkt[TCP].dport)
                
                # Check for plaintext credentials in HTTP/FTP/Telnet
                if pkt.haslayer(Raw):
                    try:
                        payload = pkt[Raw].load.decode(errors='ignore').lower()
                        if "password=" in payload or "pass " in payload or "pwd=" in payload:
                            anomalies.append({
                                "type": "plaintext_credentials",
                                "description": "Possible plain-text credentials found in packet payload.",
                                "severity": "high"
                            })
                    except Exception:
                        pass
                        
            elif pkt.haslayer(UDP):
                udp_count += 1
                if pkt[UDP].dport in self.suspicious_ports:
                    port_hits.add(pkt[UDP].dport)
            elif pkt.haslayer(ICMP):
                icmp_count += 1
            else:
                other_count += 1

        # Ping Flood heuristic (very basic)
        if icmp_count > 1000 and (icmp_count / total_packets) > 0.5:
            anomalies.append({
                "type": "ping_flood",
                "description": "High volume of ICMP traffic detected, possible Ping Flood/Sweep.",
                "severity": "medium"
            })
            
        if port_hits:
            anomalies.append({
                "type": "suspicious_ports",
                "description": f"Traffic detected on commonly exploited/suspicious ports: {list(port_hits)}",
                "severity": "high"
            })
            
        # Deduplicate anomaly types
        unique_anomalies = {}
        for a in anomalies:
            unique_anomalies[a["type"]] = a
            
        final_anomalies = list(unique_anomalies.values())

        return {
            "total_packets": total_packets,
            "tcp_count": tcp_count,
            "udp_count": udp_count,
            "icmp_count": icmp_count,
            "other_count": other_count,
            "anomalies_found": len(final_anomalies),
            "anomaly_details": {"anomalies": final_anomalies}
        }

network_service = NetworkAnalysisService()
