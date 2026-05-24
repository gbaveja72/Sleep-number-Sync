import os
import json
from datetime import datetime, timedelta
import pytz
import gspread
from google.oauth2.service_account import Credentials
import logging
import traceback
from garminconnect import Garmin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EASTERN = pytz.timezone('US/Eastern')

class GarminSync:
    def __init__(self, email: str, password: str, sheet_id: str):
        self.email = email
        self.password = password
        self.sheet_id = sheet_id
        self.client = None
        self.sheets = None
        
    def login_garmin(self) -> bool:
        logger.info("🔐 Connecting to Garmin Connect...")
        try:
            # Pass email/password if available, but login will use the tokenstore if they aren't
            self.client = Garmin(self.email, self.password)
            self.client.login("~/.garminconnect")
            logger.info("✅ Garmin authenticated")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to login to Garmin: {e}")
            return False

    def login_google_sheets(self) -> bool:
        logger.info("🔐 Connecting to Google Sheets...")
        try:
            creds_json = os.getenv("GOOGLE_CREDENTIALS")
            if creds_json:
                creds_dict = json.loads(creds_json)
                credentials = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                if os.path.exists('credentials.json'):
                    credentials = Credentials.from_service_account_file(
                        'credentials.json',
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                else:
                    logger.error("❌ No credentials found (env var or credentials.json)")
                    return False
                    
            self.sheets = gspread.authorize(credentials)
            logger.info("✅ Google Sheets authenticated")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {e}")
            return False

    def ensure_worksheet(self) -> gspread.Worksheet:
        try:
            sheet = self.sheets.open_by_key(self.sheet_id)
            try:
                worksheet = sheet.worksheet("Garmin Data")
            except gspread.exceptions.WorksheetNotFound:
                logger.info("Creating 'Garmin Data' worksheet...")
                worksheet = sheet.add_worksheet(title="Garmin Data", rows="1000", cols="20")
                headers = [
                    "Date", "Steps", "Distance (m)", "Calories", "Active Calories", 
                    "Resting Calories", "Active Time (min)", "Min Heart Rate", "Max Heart Rate", "Resting Heart Rate"
                ]
                worksheet.append_row(headers)
                worksheet.format('A1:J1', {'textFormat': {'bold': True}})
            return worksheet
        except Exception as e:
            logger.error(f"❌ Failed to access worksheet: {e}")
            return None

    def get_existing_dates(self, worksheet: gspread.Worksheet) -> set:
        logger.info("📅 Checking existing dates in Google Sheets...")
        try:
            dates = worksheet.col_values(1)
            if dates and dates[0] == "Date":
                dates = dates[1:]
            logger.info(f"   Found {len(dates)} existing date entries.")
            return set(dates)
        except Exception as e:
            logger.error(f"❌ Failed to read existing dates: {e}")
            return set()

    def fetch_day_data(self, target_date: datetime) -> dict:
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            stats = self.client.get_stats(date_str)
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to fetch Garmin data for {target_date}: {e}")
            return None

    def push_to_sheets(self, worksheet: gspread.Worksheet, date_str: str, stats: dict) -> bool:
        try:
            if not stats:
                return False
                
            steps = stats.get('totalSteps', '')
            distance = stats.get('totalDistanceMeters', '')
            calories = stats.get('totalKilocalories', '')
            active_cals = stats.get('activeKilocalories', '')
            resting_cals = stats.get('bMRKilocalories', '')
            active_seconds = stats.get('highlyActiveSeconds', 0) + stats.get('activeSeconds', 0)
            active_mins = round(active_seconds / 60) if active_seconds else ''
            
            min_hr = stats.get('minHeartRate', '')
            max_hr = stats.get('maxHeartRate', '')
            resting_hr = stats.get('restingHeartRate', '')
            
            row_data = [
                date_str,
                steps,
                distance,
                calories,
                active_cals,
                resting_cals,
                active_mins,
                min_hr,
                max_hr,
                resting_hr
            ]
            
            worksheet.append_row(row_data, value_input_option="USER_ENTERED")
            logger.info(f"✅ Row added: {date_str}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push to sheets: {e}")
            traceback.print_exc()
            return False

    def sync(self) -> bool:
        try:
            if not self.login_garmin():
                return False
            
            if not self.login_google_sheets():
                return False
                
            worksheet = self.ensure_worksheet()
            if not worksheet:
                return False
                
            existing_dates = self.get_existing_dates(worksheet)
            
            logger.info("🔄 Starting Garmin auto-backfill (checking last 30 days)...")
            now = datetime.now(EASTERN)
            
            for i in range(30, -1, -1):
                target_date = now - timedelta(days=i)
                date_str = target_date.strftime("%Y-%m-%d")
                
                if date_str in existing_dates:
                    logger.info(f"⏭️  Skipping {date_str} (already in sheet)")
                    continue
                    
                logger.info(f"📅 Fetching missing data for {date_str}...")
                stats = self.fetch_day_data(target_date)
                if stats:
                    self.push_to_sheets(worksheet, date_str, stats)
            
            logger.info("✨ Garmin Sync completed successfully!\n")
            return True
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")
            traceback.print_exc()
            return False

def main():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    if not sheet_id:
        print("❌ Missing required environment variables:")
        print("   - GOOGLE_SHEETS_ID")
        return False
        
    # Email and password are now optional if ~/.garminconnect exists!
    syncer = GarminSync(email, password, sheet_id)
    success = syncer.sync()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
