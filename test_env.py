import os
from dotenv import load_dotenv

load_dotenv()
webhook = os.getenv("DISCORD_WEBHOOK_URL")

if webhook:
    print(f"✅ SUCCESS: Webhook found!")
    print(f"🔗 URL starts with: {webhook[:20]}...")
else:
    print("❌ ERROR: DISCORD_WEBHOOK_URL not found in .env file.")