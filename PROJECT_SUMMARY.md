# Sleep Number to Google Sheets Sync - Project Summary

## Project Goal
Automatically sync Sleep Number bed data (including Heart Rate, HRV, Respiratory Rate, Sleep Score) to Google Sheets every day at 11 AM and 6 PM EDT.

---

## Current Status

### What Works ✅
- Sleep Number API authentication
- Google Sheets API authentication with service account
- Real-time bed status (in bed, sleep number preference)
- Basic row writing to Google Sheet

### What Needs Investigation ❌
- Historical sleep data retrieval (30 days backfill)
- Fetching Heart Rate, HRV, Respiratory Rate, Sleep Score from sleep sessions
- Multiple sleep sessions per day (night sleep + naps)
- Proper date/time formatting in Google Sheet

---

## Architecture

### Components
1. **Sleep Number API** (asyncsleepiq library)
   - Authenticates with Sleep Number account
   - Fetches bed status and sleep data
   
2. **Google Sheets API** (gspread library)
   - Authenticates via service account JSON
   - Writes data rows to spreadsheet

3. **GitHub Actions** (Automation)
   - Runs Python script automatically
   - Schedule: 11 AM EDT (night sleep) + 6 PM EDT (naps)
   - Uses environment variables for credentials

---

## Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Google Service Account
1. Go to console.cloud.google.com
2. Create service account (name: sleep-number-sync)
3. Create JSON key
4. Share your Google Sheet with the service account email
5. Save JSON as `credentials.json` (for local testing)

### Step 3: Set Environment Variables
```bash
export SLEEP_NUMBER_EMAIL="gbaveja72@gmail.com"
export SLEEP_NUMBER_PASSWORD="Sikhnet12!"
export GOOGLE_SHEETS_ID="1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs"
export GOOGLE_CREDENTIALS='{"type":"service_account",...}'  # Paste JSON contents
```

### Step 4: Test Locally
```bash
python sleep_sync.py
```

### Step 5: Deploy to GitHub Actions
1. Create GitHub repo: `sleep-number-sync`
2. Add files: `sleep_sync.py`, `requirements.txt`, `.github/workflows/sleep-sync.yml`
3. Add repository secrets (Settings → Secrets):
   - SLEEP_NUMBER_EMAIL
   - SLEEP_NUMBER_PASSWORD
   - GOOGLE_SHEETS_ID
   - GOOGLE_CREDENTIALS (paste entire JSON)

---

## File Structure

```
sleep-number-sync/
├── sleep_sync.py                    # Main sync script
├── requirements.txt                 # Python dependencies
├── credentials.json                 # Service account JSON (local only)
├── .github/
│   └── workflows/
│       └── sleep-sync.yml          # GitHub Actions workflow
└── README.md                        # This file
```

---

## Current Code

### sleep_sync.py
- **Status:** Partially working
- **Issues:** 
  - Not fetching historical sleep data properly
  - May not capture Heart Rate, HRV, Respiratory Rate in all cases
  - Timezone handling needs verification

### requirements.txt
- asyncsleepiq
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- gspread
- pytz

### sleep-sync.yml (GitHub Actions)
- Runs at 11 AM UTC (3 PM UTC = 11 AM EDT)
- Runs at 6 PM UTC (10 PM UTC = 6 PM EDT)
- Uses environment variables from GitHub secrets

---

## Known Limitations

1. **Historical Data:** Sleep Number API may not support fetching arbitrary date ranges
2. **Sleep Metrics:** Heart Rate, HRV, etc. only available when sleep session is complete
3. **Timezone:** Script uses EDT; adjust for other timezones
4. **Rate Limits:** Sleep Number API has rate limits (not documented)

---

## Next Steps for Debugging

1. **Enable verbose logging** in sleep_sync.py to see what data is being returned
2. **Check asyncsleepiq library documentation** for available methods beyond fetch_sleep_data()
3. **Test API directly** using Python interactive shell to inspect returned objects
4. **Verify sleep sessions exist** in Sleep Number app before running sync
5. **Check Google Sheet** for proper permissions and data format

---

## Useful Commands

```bash
# Test locally
python sleep_sync.py

# Run with backfill flag (if implemented)
BACKFILL=true python sleep_sync.py

# Check logs
tail -f ~/sleep_sync.log

# Verify environment variables
echo $SLEEP_NUMBER_EMAIL
echo $GOOGLE_SHEETS_ID
```

---

## Contact/Support

Current issues:
- Sleep metrics not populating in Google Sheet
- Unclear if asyncsleepiq supports historical data fetching with date parameters
- Need to inspect actual API response to understand data structure

Recommendation: Use Python IDE (VS Code, PyCharm) to:
1. Step through code with debugger
2. Inspect asyncsleepiq returned objects
3. Log all API responses to understand structure
4. Verify sleep_data object contains expected metrics
