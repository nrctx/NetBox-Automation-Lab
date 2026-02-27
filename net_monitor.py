import os
import time
import requests
from pynetbox import api
from icmplib import ping
from dotenv import load_dotenv

# 1. LOAD CONFIGURATION
load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL")
# Default to 60 seconds if not specified in .env
CHECK_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", 60))

# 2. INITIALIZE API
nb = api(url=NETBOX_URL, token=NETBOX_TOKEN)

def send_to_discord(message):
    """Sends a formatted notification to the Discord channel."""
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Discord Error: {e}")

def update_netbox_status(device, new_status):
    """Updates the device status in the NetBox database."""
    try:
        device.status = new_status
        device.save()
        print(f"🔄 NetBox: {device.name} status updated to {new_status.upper()}")
    except Exception as e:
        print(f"❌ NetBox Update Error for {device.name}: {e}")

def run_monitor():
    """Main logic to check device health and handle state changes."""
    # Filter for devices that are either 'active' or 'offline'
    devices = nb.dcim.devices.filter(status=['active', 'offline'])

    for device in devices:
        if not device.primary_ip:
            continue # Skip devices with no IP assigned

        # Clean the IP (remove /32, etc.)
        ip_address = device.primary_ip.address.split('/')[0]
        
        # Perform the ping
        host = ping(ip_address, count=2, interval=0.2)
        
        # --- LOGIC: DEVICE IS DOWN ---
        if not host.is_alive:
            if device.status.value == 'active':
                print(f"⚠️ {device.name} ({ip_address}) is DOWN!")
                send_to_discord(f"🚨 **ALERT**: `{device.name}` ({ip_address}) is unreachable!")
                update_netbox_status(device, 'offline')
            else:
                print(f"ℹ️ {device.name} is still offline (No new alert sent).")

        # --- LOGIC: DEVICE IS UP ---
        elif host.is_alive:
            if device.status.value == 'offline':
                print(f"🎉 {device.name} ({ip_address}) has RECOVERED!")
                send_to_discord(f"✅ **RECOVERY**: `{device.name}` ({ip_address}) is back online!")
                update_netbox_status(device, 'active')
            else:
                # Device is active and ping is successful
                pass 

if __name__ == "__main__":
    print("🚀 Monitoring System Started...")
    print(f"Settings: Checking NetBox every {CHECK_INTERVAL}s")
    print("Press Ctrl+C to exit safely.")
    print("-" * 40)

    while True:
        try:
            run_monitor()
            
            # Local Heartbeat Log
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"💓 [HEARTBEAT] {timestamp} - Scan complete. All systems nominal.")
            
        except KeyboardInterrupt:
            print("\nShutting down monitor. Goodbye!")
            break
        except Exception as e:
            print(f"❌ [CRITICAL ERROR] {e}")
        
        time.sleep(CHECK_INTERVAL)