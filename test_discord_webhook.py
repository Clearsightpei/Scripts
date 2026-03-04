#!/usr/bin/env python3
"""
Simple script to test Discord webhook configuration.
Run this to verify your webhook URL is working before deploying to GitHub Actions.
"""

import os
import sys
import requests
from datetime import datetime


def test_webhook():
    """Send a test message to Discord webhook."""
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

    if not webhook_url:
        print("❌ ERROR: DISCORD_WEBHOOK_URL environment variable not set")
        print("\nUsage:")
        print("  export DISCORD_WEBHOOK_URL='your_webhook_url'")
        print("  python test_discord_webhook.py")
        return 1

    print("🧪 Testing Discord webhook...")
    print(f"📍 Webhook URL: {webhook_url[:50]}...")

    # Create test embed
    embed = {
        "title": "✅ Webhook Test Successful",
        "description": "Your Discord webhook is configured correctly!",
        "color": 5814783,  # Blue color
        "fields": [
            {
                "name": "Status",
                "value": "Ready to monitor courses",
                "inline": False
            }
        ],
        "footer": {
            "text": f"Test sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }

    payload = {
        "embeds": [embed],
        "content": "🎓 Foothill Course Monitor - Webhook Test"
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()

        print("✅ SUCCESS! Test message sent to Discord")
        print(f"   Response: {response.status_code}")
        print("\n💡 Check your Discord channel for the test message")
        return 0

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if response.status_code == 404:
            print("   The webhook URL may be invalid or deleted")
        elif response.status_code == 401:
            print("   Authentication failed - check your webhook URL")
        else:
            print(f"   Status code: {response.status_code}")
        return 1

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not reach Discord")
        print("   Check your internet connection")
        return 1

    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}")
        print(f"   {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(test_webhook())