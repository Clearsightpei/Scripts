# Foothill College Course Monitor

Automated monitoring script for Math 1C course availability at Foothill College. Sends Discord notifications when seats become available.

## Features

- ✅ Monitors multiple CRNs simultaneously (40390, 40039, 40626)
- ✅ Checks both regular seats and waitlist seats
- ✅ Discord webhook notifications with rich embeds
- ✅ GitHub Actions compatible (runs every 5-10 minutes)
- ✅ Detailed logging for debugging
- ✅ Graceful error handling

## Setup Instructions

### 1. Create a Discord Webhook

1. Open Discord and go to the channel where you want notifications
2. Click the gear icon (Edit Channel) → Integrations → Webhooks
3. Click "New Webhook" and give it a name (e.g., "Course Monitor")
4. Copy the Webhook URL

### 2. Set Up GitHub Repository

1. Create a new GitHub repository (or use existing)
2. Add these files to your repository:
   - `foothill_course_monitor.py` (the main script)
   - `.github/workflows/course_monitor.yml` (the workflow file)

3. Add your Discord webhook as a secret:
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: (paste your Discord webhook URL)
   - Click "Add secret"

### 3. Create the Workflow Directory

In your repository, create the workflow file at:
```
.github/workflows/course_monitor.yml
```

Use the contents from `.github_workflows_course_monitor.yml` that was generated.

### 4. Customize (Optional)

Edit `foothill_course_monitor.py` to modify:

- **CRNs**: Change `TARGET_CRNS` list to monitor different courses
- **Schedule**: Edit the cron schedule in the workflow file:
  - `*/5 * * * *` = every 5 minutes
  - `*/10 * * * *` = every 10 minutes
  - `0 * * * *` = every hour

### 5. Test the Setup

#### Local Testing (Optional)
```bash
# Install dependencies
pip install requests beautifulsoup4

# Set webhook URL
export DISCORD_WEBHOOK_URL="your_webhook_url_here"

# Run script
python foothill_course_monitor.py
```

#### GitHub Actions Testing
1. Go to your repository → Actions tab
2. Click "Foothill Course Monitor" workflow
3. Click "Run workflow" → "Run workflow"
4. Check the logs to see output

## Understanding the Output

The script logs provide detailed information:

```
🔍 Checking course availability at 2026-03-04 14:30:00
📋 Target CRNs: 40390, 40039, 40626
🌐 URL: https://foothill.edu/schedule/index.html?dept=MATH&Quarter=2026S

⏳ Fetching schedule page...
✅ Successfully fetched page (Status: 200)

--- Checking CRN 40390 ---
📊 Math 1C
   Available Seats: 2
   Waitlist Seats: 0
🎉 SEATS AVAILABLE for CRN 40390!
✅ Discord notification sent for CRN 40390
```

## Troubleshooting

### No notifications are sent
- Verify the Discord webhook URL is correctly set in GitHub secrets
- Check GitHub Actions logs for errors
- Test the webhook manually using a curl command

### Script can't find course data
- The website HTML structure may have changed
- Check if the CRNs are correct for the current quarter
- Visit the URL manually to verify the courses exist

### GitHub Actions quota
- Free GitHub accounts have 2,000 Actions minutes per month
- Running every 10 minutes uses ~4,320 minutes/month (exceeds free tier)
- Consider running during specific hours only:
  ```yaml
  schedule:
    - cron: '*/10 8-17 * * *'  # Every 10 min, 8 AM - 5 PM
  ```

## Modifying for Other Courses

To monitor different courses:

1. Change `TARGET_URL` to the appropriate department and quarter
2. Update `TARGET_CRNS` with the new CRN numbers
3. Update the course name references if needed

Example for a different course:
```python
TARGET_URL = "https://foothill.edu/schedule/index.html?dept=CS&Quarter=2026S"
TARGET_CRNS = ["12345", "67890"]
```

## Important Notes

- ⚠️ Be respectful with scraping frequency (don't exceed every 5 minutes)
- ⚠️ This script is for personal use and educational purposes
- ⚠️ Foothill may change their website structure, requiring updates to the parser
- ⚠️ Always register through official channels when notified

## License

MIT License - Use at your own risk. Not affiliated with Foothill College.