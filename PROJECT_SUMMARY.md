# Sleep Number to Google Sheets Sync - Project Summary

## Project Goal
Automatically sync **all available** Sleep Number bed data (including Heart Rate, HRV, Respiratory Rate, Sleep Score, Session Duration, Out of Bed Time, and Fall Asleep Time) to Google Sheets every day at 10 AM and 6 PM EDT.

---

## Current Status

### What Works ✅ (Everything!)
- **Sleep Number API authentication**
- **Google Sheets API authentication** via Service Account
- **Smart Auto-Backfill**: Automatically detects missing dates in the last 30 days and fetches them.
- **"In Bed" Handling**: Safely skips fetching if you are actively in bed (data will be picked up on the next run once the sleep session ends).
- **GitHub Actions Automation**: Deployed and running flawlessly at 10 AM and 6 PM EDT every day.
- **Full Data Extract**: Captures 16 distinct metrics per sleeper.

---

## Architecture

### Components
1. **Sleep Number API** (`asyncsleepiq` library)
   - Authenticates with Sleep Number account.
   - Specifically uses `sleeper.get_sleep_data(date)` to retrieve full session arrays (avoids the bug in older scripts that used the non-existent `api.fetch_sleep_data()`).
   
2. **Google Sheets API** (`gspread` library)
   - Authenticates via service account JSON.
   - Pushes directly to the **"Full Sleep Data"** worksheet tab.
   - Writes using `USER_ENTERED` mode so Google Sheets properly formats dates/times instead of plain text.

3. **GitHub Actions** (Automation)
   - `.github/workflows/sleep-sync-CURRENT.yml`
   - Triggered at 10 AM EDT (`0 14 * * *`) and 6 PM EDT (`0 22 * * *`).

---

## File Structure

```
sleep-number-sync/
├── sleep_sync_CURRENT.py            # Main smart sync script
├── requirements_CURRENT.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── sleep-sync-CURRENT.yml  # GitHub Actions schedule
├── PROJECT_SUMMARY.md               # This reference document
├── IDE_SETUP_GUIDE.md               # IDE setup guide
└── README.md                        # Quick start guide
```

---

## Code Reference: sleep_sync_CURRENT.py

### 1. Auto-Backfill Logic
The script includes a `get_existing_dates()` method. It reads Column A of your `Full Sleep Data` sheet and compares it against the last 30 days. It only queries the Sleep Number API for the days missing from your sheet.

### 2. Time Conversion
Raw data from Sleep Number returns duration in **seconds**. The script automatically divides these by 60 and rounds the numbers before pushing to Google Sheets, resulting in clean **minutes** for `Duration`, `Restful`, `Restless`, `Out of Bed`, and `Fall Asleep Period`.

### 3. Graceful Failure
If the script encounters a day where `duration` is missing (i.e. you are actively in bed or the sleep session did not calculate), the script logs a warning `⚠️ No sleep metrics available` and completely skips pushing that row. This ensures it doesn't pollute your sheet with empty data, and guarantees it will be backfilled during the next run.
