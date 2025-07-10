# scripts/monitor_system.py
"""
System monitoring script for Knowledge Representation Engine
Monitors health, performance, and alerts on issues
"""

import asyncio
import psutil
import requests
import time
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import sqlite3

class SystemMonitor:
    """System monitoring and alerting"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        self.config = self.load_config(config_file)
        self.alerts_sent = {}
        self.metrics_history = []
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "check_interval": 60,
            "app_url": "http://localhost:8000",
            "thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "response_time": 5.0,
                "error_rate": 0.1
            },
            "alerts": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_addresses": []
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                }
            },
            "retention_days": 7
        }
        
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "app_health": self.check_app_health(),
            "database_health": self.check_database_health()
        }
        
        return metrics
    
    def check_app_health(self) -> Dict[str, Any]:
        """Check application health"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.config['app_url']}/health",
                timeout=10
            )
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response_time,
                "status_code": response.status_code,
                "details": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time": None,
                "status_code": None,
                "error": str(e)
            }
    
    def check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            db_path = Path("data/knowledge_repr.db")
            if not db_path.exists():
                return {"status": "unhealthy", "error": "Database file not found"}
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conversation_count = cursor.fetchone()[0]
                
                # Check database size
                db_size = db_path.stat().st_size / (1024 * 1024)  # MB
                
                return {
                    "status": "healthy",
                    "conversation_count": conversation_count,
                    "database_size_mb": round(db_size, 2)
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def evaluate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate metrics against thresholds and generate alerts"""
        alerts = []
        thresholds = self.config["thresholds"]
        
        # CPU usage alert
        if metrics["cpu_usage"] > thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"High CPU usage: {metrics['cpu_usage']:.1f}%",
                "value": metrics["cpu_usage"],
                "threshold": thresholds["cpu_usage"]
            })
        
        # Memory usage alert
        if metrics["memory_usage"] > thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"High memory usage: {metrics['memory_usage']:.1f}%",
                "value": metrics["memory_usage"],
                "threshold": thresholds["memory_usage"]
            })
        
        # Disk usage alert
        if metrics["disk_usage"] > thresholds["disk_usage"]:
            alerts.append({
                "type": "disk_high",
                "severity": "critical",
                "message": f"High disk usage: {metrics['disk_usage']:.1f}%",
                "value": metrics["disk_usage"],
                "threshold": thresholds["disk_usage"]
            })
        
        # Application health alert
        app_health = metrics["app_health"]
        if app_health["status"] != "healthy":
            alerts.append({
                "type": "app_unhealthy",
                "severity": "critical",
                "message": f"Application unhealthy: {app_health.get('error', 'Unknown error')}",
                "details": app_health
            })
        elif app_health["response_time"] and app_health["response_time"] > thresholds["response_time"]:
            alerts.append({
                "type": "slow_response",
                "severity": "warning",
                "message": f"Slow response time: {app_health['response_time']:.2f}s",
                "value": app_health["response_time"],
                "threshold": thresholds["response_time"]
            })
        
        # Database health alert
        db_health = metrics["database_health"]
        if db_health["status"] != "healthy":
            alerts.append({
                "type": "database_unhealthy",
                "severity": "critical",
                "message": f"Database unhealthy: {db_health.get('error', 'Unknown error')}",
                "details": db_health
            })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send alerts via configured channels"""
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['severity']}"
            
            # Avoid spamming - only send if not sent in last hour
            if alert_key in self.alerts_sent:
                if datetime.now() - self.alerts_sent[alert_key] < timedelta(hours=1):
                    continue
            
            self.alerts_sent[alert_key] = datetime.now()
            
            # Send email alert
            if self.config["alerts"]["email"]["enabled"]:
                self.send_email_alert(alert)
            
            # Send Slack alert
            if self.config["alerts"]["slack"]["enabled"]:
                self.send_slack_alert(alert)
            
            print(f"🚨 ALERT: {alert['message']}")
    
    def send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert"""
        try:
            email_config = self.config["alerts"]["email"]
            
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['to_addresses'])
            msg['Subject'] = f"🚨 Knowledge Repr Alert: {alert['type']}"
            
            body = f"""
Alert Details:
- Type: {alert['type']}
- Severity: {alert['severity']}
- Message: {alert['message']}
- Timestamp: {datetime.now().isoformat()}

{json.dumps(alert, indent=2)}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['username'], email_config['to_addresses'], text)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, alert: Dict[str, Any]):
        """Send Slack alert"""
        try:
            webhook_url = self.config["alerts"]["slack"]["webhook_url"]
            
            severity_emoji = {
                "info": "ℹ️",
                "warning": "⚠️",
                "critical": "🚨"
            }
            
            payload = {
                "text": f"{severity_emoji.get(alert['severity'], '🔔')} *{alert['type']}*: {alert['message']}",
                "attachments": [
                    {
                        "color": "danger" if alert['severity'] == 'critical' else "warning",
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert['severity'],
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.now().isoformat(),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics for historical analysis"""
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        cutoff_time = datetime.now() - timedelta(days=self.config["retention_days"])
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # Optionally store in database
        try:
            db_path = Path("data/knowledge_repr.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS system_metrics (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            cpu_usage REAL,
                            memory_usage REAL,
                            disk_usage REAL,
                            app_response_time REAL,
                            metrics_json TEXT
                        )
                    """)
                    
                    app_health = metrics.get("app_health", {})
                    cursor.execute("""
                        INSERT INTO system_metrics 
                        (cpu_usage, memory_usage, disk_usage, app_response_time, metrics_json)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        metrics["cpu_usage"],
                        metrics["memory_usage"],
                        metrics["disk_usage"],
                        app_health.get("response_time"),
                        json.dumps(metrics)
                    ))
                    
                    conn.commit()
        except Exception as e:
            print(f"Failed to store metrics in database: {e}")
    
    async def run_monitoring_loop(self):
        """Main monitoring loop"""
        print("🔍 Starting system monitoring...")
        
        while True:
            try:
                # Check system health
                metrics = self.check_system_health()
                
                # Store metrics
                self.store_metrics(metrics)
                
                # Evaluate alerts
                alerts = self.evaluate_alerts(metrics)
                
                # Send alerts if any
                if alerts:
                    self.send_alerts(alerts)
                else:
                    print(f"✅ System healthy at {metrics['timestamp']}")
                
                # Wait for next check
                await asyncio.sleep(self.config["check_interval"])
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

def run_monitor():
    """Run the monitoring system"""
    monitor = SystemMonitor()
    asyncio.run(monitor.run_monitoring_loop())

