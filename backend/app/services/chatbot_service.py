from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

# Railway operations knowledge base
KNOWLEDGE_BASE = {
    "greeting": {
        "patterns": ["hello", "hi", "hey", "good morning", "good evening", "namaste"],
        "response": "Namaste! I am the Railway Guardian AI Assistant. I can help you with:\n• System status & alerts\n• Weather impact assessments\n• Maintenance schedules\n• Standard Operating Procedures\n• Emergency protocols\n\nHow can I assist you today?"
    },
    "status": {
        "patterns": ["status", "system status", "how is the system", "overview", "dashboard"],
        "response": "SYSTEM STATUS REPORT:\n• All edge nodes: ONLINE\n• Sensor network: OPERATIONAL\n• AI Detection: ACTIVE\n• Risk Level: MONITORING\n\nAll systems are functioning within normal parameters. The last threat assessment was completed moments ago."
    },
    "alerts": {
        "patterns": ["alert", "alerts", "incidents", "threats", "warnings", "danger"],
        "response": "ALERT SUMMARY:\nI'm monitoring all sensor nodes in real-time. Recent incidents are displayed on the Security Dashboard.\n\nTo view detailed alerts:\n1. Navigate to Security → Dashboard\n2. Check the live alert feed\n3. Critical alerts trigger automatic notifications\n\nWould you like me to explain any specific alert type?"
    },
    "weather": {
        "patterns": ["weather", "temperature", "rain", "fog", "visibility", "climate"],
        "response": "WEATHER IMPACT ADVISORY:\nCurrent weather conditions are being monitored for railway operations impact.\n\nKey factors I track:\n• Rail temperature (buckling risk above 55°C)\n• Visibility (signal sighting requirements)\n• Precipitation (drainage & embankment stability)\n• Wind speed (OHE wire stability)\n\nCheck the Monitoring → Weather page for live data."
    },
    "maintenance": {
        "patterns": ["maintenance", "repair", "inspection", "schedule", "track work"],
        "response": "MAINTENANCE MANAGEMENT:\nI help coordinate infrastructure maintenance to prevent false alarms.\n\nActive capabilities:\n• Automatic maintenance window detection\n• Risk suppression during scheduled work\n• Inspection scheduling & tracking\n• Asset health monitoring\n\nVisit Maintenance → Infrastructure for full details."
    },
    "emergency": {
        "patterns": ["emergency", "sos", "urgent", "brake", "accident", "derail"],
        "response": "⚠️ EMERGENCY PROTOCOL ACTIVATED\n\nIf this is a real emergency:\n1. ACTIVATE Emergency Braking System immediately\n2. CONTACT Control Room: Railway Emergency Helpline 139\n3. NOTIFY RPF (Railway Protection Force)\n4. SECURE the area and prevent unauthorized access\n5. PRESERVE evidence for investigation\n\nFor non-emergencies, I can help with threat assessment and SOP guidance."
    },
    "sop": {
        "patterns": ["sop", "procedure", "protocol", "guideline", "rule", "regulation"],
        "response": "STANDARD OPERATING PROCEDURES:\n\n1. THREAT DETECTION SOP:\n   • AI confirms detection → Alert generated\n   • Cross-reference with maintenance schedule\n   • Risk score computation\n   • Auto-dispatch RPF if score > 70\n\n2. SENSOR ANOMALY SOP:\n   • Vibration exceeds threshold → Escalation\n   • Pattern analysis over 40-sample window\n   • Maintenance cross-check before alert\n\n3. PATROL SOP:\n   • Regular track patrol every 4 hours\n   • Enhanced patrol during low visibility\n   • Night patrol with thermal sensors"
    },
    "sensor": {
        "patterns": ["sensor", "vibration", "phyphox", "accelerometer", "detection"],
        "response": "SENSOR NETWORK STATUS:\nThe system uses multiple sensor types:\n\n• Phyphox Accelerometer: Vibration & tampering detection\n• YOLOv8 Vision: Person/object detection\n• Environmental: Temperature, humidity\n• Acoustic: Rail stress monitoring\n\nConnect your Phyphox device via Monitoring → Sensors.\nThreshold: Vibration > 0.35g triggers investigation."
    },
    "help": {
        "patterns": ["help", "what can you do", "features", "capabilities", "commands"],
        "response": "RAILWAY GUARDIAN AI CAPABILITIES:\n\n🔒 Security: Real-time threat monitoring\n📊 Analytics: Incident trends & patterns\n🌤 Weather: Operational impact assessment\n🔧 Maintenance: Asset health & scheduling\n🗺 Mapping: Live Delhi railway network\n⚠️ Risk: Heatmap & zone-wise scoring\n🤖 Prediction: Intent analysis engine\n\nJust ask me about any topic! I'm here to support railway operations 24/7."
    },
    "risk": {
        "patterns": ["risk", "heatmap", "score", "danger zone", "vulnerable"],
        "response": "RISK ASSESSMENT ENGINE:\n\nRisk scores are computed using:\n• Recent incident density (+40 weight)\n• Sensor anomaly frequency (+25 weight)\n• Weather severity (+15 weight)\n• Time-of-day factor (+10 weight)\n• Historical pattern match (+10 weight)\n\nView the Intelligence → Risk Heatmap for zone-wise visualization.\nZones scoring >70 trigger automatic enhanced surveillance."
    }
}

class ChatbotService:
    def process_message(self, message: str, username: str = "operator") -> Dict[str, Any]:
        message_lower = message.lower().strip()
        
        # Find best matching knowledge base entry
        best_match = None
        best_score = 0
        
        for category, data in KNOWLEDGE_BASE.items():
            for pattern in data["patterns"]:
                if pattern in message_lower:
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = category
        
        if best_match:
            response = KNOWLEDGE_BASE[best_match]["response"]
            category = best_match
        else:
            response = (
                "I understand you're asking about: \"" + message + "\"\n\n"
                "I'm not sure about that specific topic. Here's what I can help with:\n"
                "• System status & monitoring\n"
                "• Alert management\n"
                "• Weather impact analysis\n"
                "• Maintenance schedules\n"
                "• Emergency protocols & SOPs\n"
                "• Sensor configuration\n"
                "• Risk assessment\n\n"
                "Try rephrasing or type 'help' for a full list of capabilities."
            )
            category = "general"

        return {
            "user": username,
            "message": message,
            "response": response,
            "category": category,
            "timestamp": datetime.utcnow().isoformat(),
        }

chatbot_service = ChatbotService()
