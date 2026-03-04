#!/usr/bin/env python3
"""
Foothill College Math 1C Course Availability Monitor
Checks seat availability for specified CRNs and sends Discord webhook notifications.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://foothill.edu/"
}

def check_foothill():
    url = "https://foothill.edu/schedule/index.html?dept=MATH&Quarter=2026S"
    # Add the headers parameter here
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
# Configuration
TARGET_URL = "https://foothill.edu/schedule/index.html?dept=MATH&Quarter=2026S"
TARGET_CRNS = ["40390", "40039", "40626"]
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')


def send_discord_notification(crn, course_info):
    """Send a Discord webhook notification about available seats."""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️  Discord webhook URL not configured (DISCORD_WEBHOOK_URL env var)")
        return False

    seats_remain = course_info.get('seats_remain', 'Unknown')
    waitlist_remain = course_info.get('waitlist_remain', 'Unknown')
    course_name = course_info.get('course_name', 'Math 1C')
    section = course_info.get('section', '')

    # Create rich embed message
    embed = {
        "title": "🎓 Course Seat Available!",
        "description": f"**{course_name}** (CRN: {crn})",
        "color": 3066993,  # Green color
        "fields": [
            {
                "name": "Available Seats",
                "value": str(seats_remain),
                "inline": True
            },
            {
                "name": "Waitlist Seats",
                "value": str(waitlist_remain),
                "inline": True
            },
            {
                "name": "Section",
                "value": section if section else "N/A",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        },
        "url": TARGET_URL
    }

    payload = {
        "embeds": [embed],
        "content": f"@here A seat is available for **CRN {crn}**!"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Discord notification sent for CRN {crn}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Discord notification: {e}")
        return False


def parse_course_data(soup, crn):
    """
    Parse course availability data for a specific CRN.
    Returns dict with course info or None if not found.
    """
    # Look for the CRN in the HTML - it's typically in a table row
    # Try multiple approaches to find the course data

    # Approach 1: Find by CRN text
    crn_elements = soup.find_all(string=lambda text: text and crn in str(text))

    for crn_elem in crn_elements:
        # Navigate up to find the row containing this CRN
        row = crn_elem.find_parent('tr')
        if not row:
            continue

        # Extract all cells in this row
        cells = row.find_all(['td', 'th'])

        # Try to find seats remain and waitlist data
        # Common patterns: "X seats remain", "Waitlist: Y"
        course_info = {
            'crn': crn,
            'course_name': None,
            'section': None,
            'seats_remain': None,
            'waitlist_remain': None
        }

        for cell in cells:
            cell_text = cell.get_text(strip=True)

            # Look for seat availability patterns
            if 'seat' in cell_text.lower() and 'remain' in cell_text.lower():
                # Extract number from text like "5 seats remain"
                try:
                    seats = ''.join(filter(str.isdigit, cell_text))
                    if seats:
                        course_info['seats_remain'] = int(seats)
                except ValueError:
                    pass

            # Look for waitlist patterns
            if 'waitlist' in cell_text.lower():
                try:
                    # Handle patterns like "Waitlist: 3 seats remain" or "3 waitlist seats"
                    waitlist = ''.join(filter(str.isdigit, cell_text))
                    if waitlist:
                        course_info['waitlist_remain'] = int(waitlist)
                except ValueError:
                    pass

            # Try to get course name (usually contains "MATH")
            if 'MATH' in cell_text and not course_info['course_name']:
                course_info['course_name'] = cell_text

            # Section info (usually a letter or number like "01Y", "02W", etc.)
            if len(cell_text) <= 5 and cell_text.isalnum() and cell_text != crn:
                if not course_info['section']:
                    course_info['section'] = cell_text

        # If we found seat information, return it
        if course_info['seats_remain'] is not None or course_info['waitlist_remain'] is not None:
            return course_info

    # Approach 2: Look for data attributes or specific class names
    # (Foothill may use specific HTML structure)
    for row in soup.find_all('tr'):
        row_text = row.get_text()
        if crn in row_text:
            cells = row.find_all(['td', 'th'])
            # Try to extract structured data
            cell_texts = [cell.get_text(strip=True) for cell in cells]

            course_info = {
                'crn': crn,
                'course_name': 'Math 1C',
                'section': None,
                'seats_remain': None,
                'waitlist_remain': None
            }

            # Look through all cells for numeric values that might be seats
            for i, text in enumerate(cell_texts):
                if text.isdigit():
                    num = int(text)
                    # Heuristic: first number might be seats, second might be waitlist
                    if course_info['seats_remain'] is None:
                        course_info['seats_remain'] = num
                    elif course_info['waitlist_remain'] is None:
                        course_info['waitlist_remain'] = num

            if course_info['seats_remain'] is not None:
                return course_info

    return None


def check_course_availability():
    """Main function to check course availability and send notifications."""
    print(f"🔍 Checking course availability at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Target CRNs: {', '.join(TARGET_CRNS)}")
    print(f"🌐 URL: {TARGET_URL}\n")

    try:
        # Fetch the schedule page
        print("⏳ Fetching schedule page...")
        response = requests.get(TARGET_URL, timeout=30)
        response.raise_for_status()
        print(f"✅ Successfully fetched page (Status: {response.status_code})\n")

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check each CRN
        found_available = False
        for crn in TARGET_CRNS:
            print(f"--- Checking CRN {crn} ---")

            course_data = parse_course_data(soup, crn)

            if course_data is None:
                print(f"⚠️  CRN {crn}: Not found in schedule (may not exist or HTML structure changed)")
                continue

            seats = course_data.get('seats_remain', 0) or 0
            waitlist = course_data.get('waitlist_remain', 0) or 0
            course_name = course_data.get('course_name', 'Math 1C')

            print(f"📊 {course_name}")
            print(f"   Available Seats: {seats}")
            print(f"   Waitlist Seats: {waitlist}")

            # Check if seats are available
            if seats > 0 or waitlist > 0:
                print(f"🎉 SEATS AVAILABLE for CRN {crn}!")
                send_discord_notification(crn, course_data)
                found_available = True
            else:
                print(f"❌ No seats available")

            print()  # Blank line between CRNs

        if not found_available:
            print("📝 Summary: No available seats found for any monitored CRN")
        else:
            print("📝 Summary: Found available seats! Notifications sent.")

        return 0  # Success

    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out while fetching schedule page")
        print("   The Foothill website may be slow or unreachable")
        return 1

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Failed to connect to Foothill website")
        print("   Check your internet connection or the website may be down")
        return 1

    except requests.exceptions.HTTPError as e:
        print(f"❌ ERROR: HTTP error occurred: {e}")
        print(f"   Status code: {response.status_code}")
        return 1

    except Exception as e:
        print(f"❌ ERROR: Unexpected error occurred: {type(e).__name__}")
        print(f"   Details: {str(e)}")
        print("\n   This may indicate the HTML structure has changed.")
        print("   Please check the website manually and update the parser if needed.")
        return 1


if __name__ == "__main__":
    exit_code = check_course_availability()
    sys.exit(exit_code)