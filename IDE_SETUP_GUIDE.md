# Sleep Number Sync - IDE Setup Guide

## Files You Have

1. **sleep_sync.py** - Main script
2. **requirements.txt** - Python dependencies
3. **sleep-sync.yml** - GitHub Actions workflow (if using GitHub)
4. **credentials.json** - Service account JSON (keep private!)
5. **PROJECT_SUMMARY.md** - Project documentation

---



### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Set Environment Variables

**Mac/Linux:**
```bash
export SLEEP_NUMBER_EMAIL="gbaveja72@gmail.com"
export SLEEP_NUMBER_PASSWORD="your_password_here"
export GOOGLE_SHEETS_ID="1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs"
export GOOGLE_CREDENTIALS='{"type":"service_account",...}'
```

**Windows (PowerShell):**
```powershell
$env:SLEEP_NUMBER_EMAIL = "gbaveja72@gmail.com"
$env:SLEEP_NUMBER_PASSWORD = "your_password_here"
$env:GOOGLE_SHEETS_ID = "1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs"
$env:GOOGLE_CREDENTIALS = '{"type":"service_account",...}'
```

### Step 6: Run Script
```bash
python sleep_sync.py
```

### Step 7: Check Logs
Script outputs to console. Look for:
- ✅ "Sleep Number authenticated"
- ✅ "Google Sheets authenticated"
- ✅ "Fetched bed data"
- ✅ "Row added"

---

## Setup for GitHub Actions (if deploying)

### Step 1: Create GitHub Repository
1. Go to github.com
2. Create new repo: `sleep-number-sync`
3. Clone to your computer

### Step 2: Add Files to Repo
```
sleep-number-sync/
├── sleep_sync.py
├── requirements.txt
└── .github/
    └── workflows/
        └── sleep-sync.yml
```

### Step 3: Create GitHub Secrets
1. Go to repo **Settings**
2. **Secrets and variables** → **Actions**
3. Add these secrets:

| Name | Value |
|------|-------|
| SLEEP_NUMBER_EMAIL | gbaveja72@gmail.com |
| SLEEP_NUMBER_PASSWORD | your_password_here |
| GOOGLE_SHEETS_ID | 1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs |
| GOOGLE_CREDENTIALS | (paste entire JSON file) |

### Step 4: Commit and Push
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 5: Test
- Go to **Actions** tab
- Click "Sleep Number Daily Sync"
- Click "Run workflow"
- Monitor logs

---

## Setup in PyCharm

### Step 1: Open Project
1. File → Open → select folder
2. Mark as sources root

### Step 2: Create Virtual Environment
1. Preferences → Project → Python Interpreter
2. Add Interpreter → Add Local Interpreter
3. Choose base Python 3.11
4. Click "Create"

### Step 3: Install Dependencies
1. Terminal → python -m pip install -r requirements.txt

### Step 4: Configure Run Configuration
1. Run → Edit Configurations
2. Click "+" → Python
3. Script path: `sleep_sync.py`
4. Environment variables:
   ```
   SLEEP_NUMBER_EMAIL=gbaveja72@gmail.com
   SLEEP_NUMBER_PASSWORD=your_password_here
   GOOGLE_SHEETS_ID=1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs
   GOOGLE_CREDENTIALS={"type":"service_account",...}
   ```
5. Click OK

### Step 5: Run
Press Run button or Shift+F10

---

## Debugging Tips

### Enable Debug Mode
Add this at top of sleep_sync.py:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Inspect API Response
Add breakpoints in sleep_sync.py:
```python
# After fetch_bed_data(), add:
print(f"DEBUG - sleeper object: {sleeper}")
print(f"DEBUG - sleep_data object: {sleep_data}")
print(f"DEBUG - heart_rate value: {sleep_data.heart_rate}")
```

### Check Credentials
```python
# In login_google_sheets(), add:
print(f"Credentials dict keys: {creds_dict.keys()}")
print(f"Authorized client: {self.sheets}")
```

---

## Common Issues & Solutions

### "ModuleNotFoundError: No module named 'asyncsleepiq'"
**Solution:** Run `pip install -r requirements.txt`

### "PermissionError: [403]: The caller does not have permission"
**Solution:** Share Google Sheet with service account email from JSON file

### "KeyError: 'type' in credentials"
**Solution:** Check GOOGLE_CREDENTIALS env var is complete JSON (not truncated)

### "No data appearing in Google Sheet"
**Solution:** 
1. Check if sleep session exists in Sleep Number app
2. Verify script ran (check logs)
3. Check Google Sheet has correct ID
4. Verify headers match code

---

## Local Testing Workflow

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Set environment variables (Mac/Linux)
export SLEEP_NUMBER_EMAIL="..."
export SLEEP_NUMBER_PASSWORD="..."
export GOOGLE_SHEETS_ID="..."
export GOOGLE_CREDENTIALS='...'

# 3. Run script
python sleep_sync.py

# 4. Check output
# Look for ✅ or ❌ messages

# 5. Check Google Sheet
# Open and refresh to see new row
```

---

## Next Steps

1. **Test locally first** with credentials.json
2. **Verify Google Sheet updates** with test data
3. **Deploy to GitHub Actions** when working
4. **Monitor logs** for errors
5. **Iterate on sleep data capture** based on what you find

---

## Questions?

Check the logs for specific error messages. Most issues are:
- Missing environment variables
- Wrong Google Sheet ID
- Service account not shared on sheet
- Sleep session not available in Sleep Number API
