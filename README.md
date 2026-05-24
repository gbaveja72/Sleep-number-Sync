# Sleep Number to Google Sheets Sync - Complete Package

## 📦 Package Contents

This folder contains everything you need to sync Sleep Number bed data to Google Sheets.

### Files Included

| File | Purpose |
|------|---------|
| `sleep_sync.py` | **Main script** - Fetches Sleep Number data and writes to Sheets |
| `requirements.txt` | Python dependencies - Install with `pip install -r requirements.txt` |
| `sleep-sync.yml` | GitHub Actions workflow - Copy to `.github/workflows/sleep-sync.yml` for automation |
| `credentials.json` | Service account JSON - **Keep private, don't commit** |
| `PROJECT_SUMMARY.md` | Project overview and architecture documentation |
| `IDE_SETUP_GUIDE.md` | Step-by-step setup for VS Code, PyCharm, etc. |
| `.gitignore` | Git configuration - Prevents committing credentials |
| `README.md` | This file |

---

## 🚀 Quick Start (5 minutes)

### Option 1: Run Locally (Mac/Linux/Windows)

```bash
# 1. Create folder
mkdir sleep-number-sync
cd sleep-number-sync

# 2. Add these files
# - sleep_sync.py
# - requirements.txt
# - credentials.json (from Google Cloud)

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables
export SLEEP_NUMBER_EMAIL="gbaveja72@gmail.com"
export SLEEP_NUMBER_PASSWORD="your_password_here"
export GOOGLE_SHEETS_ID="1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs"
export GOOGLE_CREDENTIALS='{"type":"service_account",...}'

# 6. Run
python sleep_sync.py
```

### Option 2: Deploy to GitHub Actions (Automatic Daily)

```bash
# 1. Create GitHub repo: sleep-number-sync
# 2. Add files:
#    - sleep_sync.py
#    - requirements.txt
#    - .github/workflows/sleep-sync.yml
#    - .gitignore

# 3. Add GitHub Secrets (Settings → Secrets):
#    - SLEEP_NUMBER_EMAIL
#    - SLEEP_NUMBER_PASSWORD
#    - GOOGLE_SHEETS_ID
#    - GOOGLE_CREDENTIALS

# 4. Commit and push
git add .
git commit -m "Sleep Number sync"
git push

# 5. Runs automatically at 11 AM and 6 PM EDT
```

---

## ✅ What It Does

1. **Authenticates** with Sleep Number API
2. **Fetches** bed status, sleep data, metrics
3. **Extracts** Heart Rate, HRV, Respiratory Rate, Sleep Score
4. **Writes** to Google Sheet with timestamp
5. **Runs automatically** at 11 AM (night sleep) and 6 PM (naps)

---

## 📊 Google Sheet Columns

The script writes these columns to your Google Sheet:

```
Date | Time (EDT) | Left Sleep # | Left In Bed | Left Sleeper |
Left Heart Rate | Left HRV | Left Respiratory Rate | Left Sleep Score | Left Restful | Left Restless |
Right Sleep # | Right In Bed | Right Sleeper |
Right Heart Rate | Right HRV | Right Respiratory Rate | Right Sleep Score | Right Restful | Right Restless | Notes
```

---

## 🔑 Required Credentials

### 1. Sleep Number Account
- Email: `gbaveja72@gmail.com`
- Password: `your_password_here`

### 2. Google Service Account JSON
- Create at: console.cloud.google.com
- Contains: Project ID, private key, client email, etc.
- Share your Google Sheet with the client email

### 3. Google Sheet ID
- Your sheet: `1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs`

---

## 📝 Setup Instructions

### Local Development (VS Code)

See **IDE_SETUP_GUIDE.md** for detailed steps

### GitHub Actions (Automatic)

1. **Create repo** on github.com
2. **Add files** to repo
3. **Add secrets** to Settings → Secrets
4. **Commit and push**
5. **Check Actions tab** for logs

---

## 🐛 Debugging

### Common Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"PermissionError [403]"**
- Share Google Sheet with service account email from JSON

**"No data in sheet"**
- Check if sleep session exists in Sleep Number app
- Verify script ran (check logs)
- Refresh Google Sheet

### Enable Debug Logs

Change in `sleep_sync.py`:
```python
level=logging.DEBUG  # Instead of INFO
```

---

## 📅 Schedule

**Local:** Run manually with `python sleep_sync.py`

**GitHub Actions:** Automatic at:
- 🌅 **11 AM EDT** (3 PM UTC) - for night sleep (11 PM - 6 AM)
- 🌤️ **6 PM EDT** (10 PM UTC) - for naps before 6 PM

---

## 🔒 Security

- **Never commit** credentials.json
- **Never share** JSON file
- **Use GitHub Secrets** for sensitive data (email, password, credentials JSON)
- **.gitignore** is configured to prevent accidental commits

---

## 📚 Documentation

- **PROJECT_SUMMARY.md** - Architecture and current status
- **IDE_SETUP_GUIDE.md** - Step-by-step setup for different IDEs
- **README.md** - This file

---

## 🚧 Current Status

### ✅ Working
- Sleep Number API authentication
- Google Sheets API authentication
- Basic bed data capture (in bed status, sleep number preference)
- Writing rows to Google Sheet
- GitHub Actions automation

### ⚠️ Known Limitations
- Heart Rate, HRV, Respiratory Rate may not always populate (depends on Sleep Number API availability)
- No historical backfill (30-day data)
- Single bed per script (can be extended)

---

## 🔗 Dependencies

```
asyncsleepiq           # Sleep Number API client
google-auth-oauthlib   # Google OAuth
google-api-python-client # Google Sheets API
gspread                # Google Sheets library
pytz                   # Timezone handling
```

All installed via: `pip install -r requirements.txt`

---

## 📞 Next Steps

1. **Test locally** first
2. **Verify data** in Google Sheet
3. **Deploy to GitHub** for automation
4. **Monitor logs** for any errors
5. **Iterate** based on what you find

---

## 📝 Notes

- Times are in **EDT** (Eastern Daylight Time)
- Adjust cron times in `sleep-sync.yml` for different timezone
- Sleep metrics only available when sleep session is complete
- Script logs all actions for debugging

---

## ✨ Good Luck!

This package is ready to use. Move it to your IDE and follow the setup guide!

Questions? Check the logs and documentation files.
