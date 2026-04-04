import time
import requests
import os
from dotenv import load_dotenv

# Load secret variables from .env
load_dotenv()

# Paste your Discord/Slack Webhook URL in your .env file
WEBHOOK_URL = os.environ.get("ALERT_WEBHOOK_URL", "") 

# Monitor these endpoints
ENDPOINTS = [
    "http://localhost/health",
    "http://localhost/debug-sentry", # Broken for testing
    "http://localhost/metrics"      # To check CPU/RAM
]
INTERVAL = 5 
CPU_THRESHOLD = 90.0 # Alert if CPU > 90%
CONSECUTIVE_REQUIRED = 3 # Alert ONLY if high for 3 checks in a row (Alert Fatigue)

# Tracking state for CPU Threshold
cpu_high_count = 0 

def send_webhook(message):
    if not WEBHOOK_URL:
        return
    payload = {"content": f"🚨 **WATCHTOWER ALERT** 🚨\n{message}"}
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=3)
    except Exception as e:
        print(f"Failed to send webhook: {e}")

def fire_drill():
    print("🕵️ Starting Status Monitor...")
    print(f"Watching: {ENDPOINTS}")
    
    if WEBHOOK_URL:
        print("✅ Webhook found. Sending startup ping to channel...")
        send_webhook("Watchtower is ONLINE and monitoring the fleet. 👁️")
    else:
        print("⚠️ No WEBHOOK_URL found. Alerts will only show in this terminal.")

    print("\n🕵️ Watchtower Monitoring started. (Shift-C to stop)\n")
    
    status_map = {url: True for url in ENDPOINTS}
    global cpu_high_count
    
    while True:
        for url in ENDPOINTS:
            try:
                response = requests.get(url, timeout=3)
                
                # Check for 500 errors (Error Rate Alert)
                if response.status_code >= 500:
                    if status_map[url]:
                        alert(f"HIGH ERROR RATE on {url}! (Status: {response.status_code})")
                        status_map[url] = False
                else:
                    if not status_map[url]:
                        alert(f"RECOVERED: {url} 🏁", is_recovery=True)
                        status_map[url] = True
                
                # SPECIAL CHECK: Read metrics for CPU Threshold
                if "metrics" in url:
                    cpu_use = response.json().get("system", {}).get("cpu_percent", 0)
                    if cpu_use > CPU_THRESHOLD:
                        cpu_high_count += 1
                        if cpu_high_count == CONSECUTIVE_REQUIRED:
                            alert(f"ALERT: SUSTAINED HIGH CPU! ({cpu_use}% for {CONSECUTIVE_REQUIRED * INTERVAL}s)")
                    else:
                        cpu_high_count = 0 # Reset count if it dips
            
            except requests.exceptions.RequestException as e:
                # Service Down Alert
                if status_map[url]:
                    alert(f"SERVICE DOWN: {url} 🚨")
                    status_map[url] = False
        
        time.sleep(INTERVAL)

def alert(message, is_recovery=False):
    timestamp = time.strftime("%H:%M:%S")
    decoration = "✅" if is_recovery else "💥"
    print(f"[{timestamp}] ALERT: {decoration} {message}")
    send_webhook(f"[{timestamp}] {decoration} {message}")

if __name__ == "__main__":
    fire_drill()
