#!/usr/bin/env python3
"""
Sleep Number to Google Sheets Sync
Fetches bed status and sleep data, writes to Google Sheets
"""

import asyncio
import os
from datetime import datetime, timedelta
import argparse
import logging
import json
from pytz import timezone

from asyncsleepiq import AsyncSleepIQ, LOGIN_COOKIE
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
import gspread

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EASTERN = timezone('US/Eastern')

class SleepNumberSync:
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, email: str, password: str, sheet_id: str):
        self.email = email
        self.password = password
        self.sheet_id = sheet_id
        self.api = None
        self.sheets = None
        
    async def login_sleep_number(self) -> bool:
        """Authenticate with Sleep Number API"""
        try:
            logger.info("🔐 Connecting to Sleep Number...")
            self.api = AsyncSleepIQ(login_method=LOGIN_COOKIE)
            await self.api.login(self.email, self.password)
            logger.info("✅ Sleep Number authenticated")
            return True
        except Exception as e:
            logger.error(f"❌ Sleep Number login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def login_google_sheets(self) -> bool:
        """Authenticate with Google Sheets"""
        try:
            logger.info("🔐 Connecting to Google Sheets...")
            
            # Try environment variable first (GitHub Actions)
            credentials_json = os.getenv("GOOGLE_CREDENTIALS")
            
            # Fall back to file (local testing)
            if not credentials_json:
                if os.path.exists('credentials.json'):
                    with open('credentials.json', 'r') as f:
                        credentials_json = f.read()
                else:
                    logger.error("❌ No credentials found (env var or credentials.json)")
                    return False
            
            # Parse and authenticate
            creds_dict = json.loads(credentials_json)
            creds = ServiceAccountCredentials.from_service_account_info(
                creds_dict, 
                scopes=self.SCOPES
            )
            self.sheets = gspread.authorize(creds)
            logger.info("✅ Google Sheets authenticated")
            return True
        except Exception as e:
            logger.error(f"❌ Google Sheets auth failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def fetch_bed_data(self, target_date: datetime = None) -> dict:
        """Fetch all bed data including sleep sessions"""
        try:
            logger.info(f"📊 Fetching bed data for {target_date.date() if target_date else 'today'}...")
            
            # Initialize beds
            await self.api.init_beds()
            logger.info("   Initialized beds")
            
            # Fetch current status
            await self.api.fetch_bed_statuses()
            logger.info("   Fetched bed statuses")
            
            # Fetch sleep data (this should get sleep sessions)
            for bed in self.api.beds.values():
                for sleeper in bed.sleepers:
                    if target_date:
                        sleep_data = await sleeper.get_sleep_data(target_date)
                        if sleep_data:
                            sleeper.sleep_data = sleep_data
                    else:
                        await sleeper.fetch_sleep_data()
            logger.info("   Fetched sleep data")
            
            # Get current time in Eastern
            now = datetime.now(EASTERN)
            if target_date:
                date_str = target_date.strftime("%Y-%m-%d")
                time_str = "00:00:00"
            else:
                date_str = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
            
            data = {
                'date': date_str,
                'time': time_str,
                'beds': []
            }
            
            # Process each bed
            for bed_id, bed in self.api.beds.items():
                logger.info(f"📍 Processing bed: {bed.name}")
                
                bed_info = {
                    'bed_id': bed_id,
                    'bed_name': bed.name,
                    'left_sleep_number': '',
                    'left_in_bed': '',
                    'left_sleeper': '',
                    'left_duration': '',
                    'left_session_count': '',
                    'left_heart_rate': '',
                    'left_hrv': '',
                    'left_respiratory_rate': '',
                    'left_sleep_score': '',
                    'left_restful': '',
                    'left_restless': '',
                    'left_out_of_bed': '',
                    'left_fall_asleep_period': '',
                    'left_start_date': '',
                    'left_end_date': '',
                    'right_sleep_number': '',
                    'right_in_bed': '',
                    'right_sleeper': '',
                    'right_duration': '',
                    'right_session_count': '',
                    'right_heart_rate': '',
                    'right_hrv': '',
                    'right_respiratory_rate': '',
                    'right_sleep_score': '',
                    'right_restful': '',
                    'right_restless': '',
                    'right_out_of_bed': '',
                    'right_fall_asleep_period': '',
                    'right_start_date': '',
                    'right_end_date': ''
                }
                
                # Process sleepers
                if hasattr(bed, 'sleepers') and bed.sleepers:
                    for idx, sleeper in enumerate(bed.sleepers):
                        side = 'left' if idx == 0 else 'right'
                        
                        # Basic info (always available)
                        bed_info[f'{side}_sleep_number'] = sleeper.sleep_number or ''
                        bed_info[f'{side}_in_bed'] = "Yes" if sleeper.in_bed else "No"
                        bed_info[f'{side}_sleeper'] = sleeper.name.strip() if sleeper.name else ''
                        
                        # Sleep data (may be empty if not sleeping)
                        if hasattr(sleeper, 'sleep_data') and sleeper.sleep_data:
                            sleep_data = sleeper.sleep_data
                            
                            logger.info(f"   {side.upper()} sleeper data:")
                            logger.info(f"      Raw Dump: {vars(sleep_data)}")
                            logger.info(f"      heart_rate: {sleep_data.heart_rate}")
                            logger.info(f"      hrv: {sleep_data.hrv}")
                            logger.info(f"      respiratory_rate: {sleep_data.respiratory_rate}")
                            logger.info(f"      sleep_score: {sleep_data.sleep_score}")
                            logger.info(f"      restful: {sleep_data.restful}")
                            logger.info(f"      restless: {sleep_data.restless}")
                            
                            # Add metrics if available
                            if getattr(sleep_data, 'duration', None) is not None:
                                bed_info[f'{side}_duration'] = round(sleep_data.duration / 60)
                            if getattr(sleep_data, 'session_count', None) is not None:
                                bed_info[f'{side}_session_count'] = sleep_data.session_count
                            if getattr(sleep_data, 'heart_rate', None) is not None:
                                bed_info[f'{side}_heart_rate'] = sleep_data.heart_rate
                            if getattr(sleep_data, 'hrv', None) is not None:
                                bed_info[f'{side}_hrv'] = sleep_data.hrv
                            if getattr(sleep_data, 'respiratory_rate', None) is not None:
                                bed_info[f'{side}_respiratory_rate'] = sleep_data.respiratory_rate
                            if getattr(sleep_data, 'sleep_score', None) is not None:
                                bed_info[f'{side}_sleep_score'] = sleep_data.sleep_score
                            if getattr(sleep_data, 'restful', None) is not None:
                                bed_info[f'{side}_restful'] = round(sleep_data.restful / 60)
                            if getattr(sleep_data, 'restless', None) is not None:
                                bed_info[f'{side}_restless'] = round(sleep_data.restless / 60)
                            if getattr(sleep_data, 'out_of_bed', None) is not None:
                                bed_info[f'{side}_out_of_bed'] = round(sleep_data.out_of_bed / 60)
                            if getattr(sleep_data, 'fall_asleep_period', None) is not None:
                                bed_info[f'{side}_fall_asleep_period'] = round(sleep_data.fall_asleep_period / 60)
                            if getattr(sleep_data, 'start_date', None) is not None:
                                bed_info[f'{side}_start_date'] = sleep_data.start_date
                            if getattr(sleep_data, 'end_date', None) is not None:
                                bed_info[f'{side}_end_date'] = sleep_data.end_date
                
                data['beds'].append(bed_info)
            
            logger.info(f"✅ Fetched data at {time_str} EDT")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to fetch bed data: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_existing_dates(self) -> set:
        """Read column A of 'Full Sleep Data' and return a set of date strings"""
        logger.info("📅 Checking existing dates in Google Sheets...")
        try:
            sheet = self.sheets.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet("Full Sleep Data")
            dates = worksheet.col_values(1)
            if dates and dates[0] == "Date":
                dates = dates[1:]
            logger.info(f"   Found {len(dates)} existing date entries.")
            return set(dates)
        except gspread.exceptions.WorksheetNotFound:
            logger.info("   Worksheet 'Full Sleep Data' not found, assuming empty.")
            return set()
        except Exception as e:
            logger.error(f"❌ Failed to read existing dates: {e}")
            return set()

    def push_to_sheets(self, data: dict) -> bool:
        """Push data to Google Sheet"""
        try:
            logger.info("📤 Pushing to Google Sheets...")
            sheet = self.sheets.open_by_key(self.sheet_id)
            
            worksheet_name = "Full Sleep Data"
            try:
                worksheet = sheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"⚠️  Creating worksheet '{worksheet_name}'...")
                worksheet = sheet.add_worksheet(
                    title=worksheet_name,
                    rows=2000,
                    cols=33
                )
                
                headers = [
                    "Date",
                    "Time (EDT)",
                    "Left Sleep Number",
                    "Left In Bed",
                    "Left Sleeper",
                    "Left Duration (min)",
                    "Left Sessions",
                    "Left Heart Rate",
                    "Left HRV",
                    "Left Respiratory Rate",
                    "Left Sleep Score",
                    "Left Restful (min)",
                    "Left Restless (min)",
                    "Left Out Of Bed (min)",
                    "Left Fall Asleep (min)",
                    "Left Session Start",
                    "Left Session End",
                    "Right Sleep Number",
                    "Right In Bed",
                    "Right Sleeper",
                    "Right Duration (min)",
                    "Right Sessions",
                    "Right Heart Rate",
                    "Right HRV",
                    "Right Respiratory Rate",
                    "Right Sleep Score",
                    "Right Restful (min)",
                    "Right Restless (min)",
                    "Right Out Of Bed (min)",
                    "Right Fall Asleep (min)",
                    "Right Session Start",
                    "Right Session End",
                    "Notes"
                ]
                worksheet.append_row(headers)
                logger.info("📝 Headers created")
            
            if not data['beds']:
                logger.error("❌ No bed data to push")
                return False
            
            bed = data['beds'][0]
            
            # Check if metrics are populated. If duration is empty for both, skip pushing.
            if bed.get('left_duration', '') == '' and bed.get('right_duration', '') == '':
                logger.warning(f"⚠️  No sleep metrics available for {data['date']} (you may be in bed). Skipping push.")
                return False
            row_data = [
                data['date'],
                data['time'],
                bed['left_sleep_number'],
                bed['left_in_bed'],
                bed['left_sleeper'],
                bed.get('left_duration', ''),
                bed.get('left_session_count', ''),
                bed['left_heart_rate'],
                bed['left_hrv'],
                bed['left_respiratory_rate'],
                bed['left_sleep_score'],
                bed['left_restful'],
                bed['left_restless'],
                bed.get('left_out_of_bed', ''),
                bed.get('left_fall_asleep_period', ''),
                bed.get('left_start_date', ''),
                bed.get('left_end_date', ''),
                bed['right_sleep_number'],
                bed['right_in_bed'],
                bed['right_sleeper'],
                bed.get('right_duration', ''),
                bed.get('right_session_count', ''),
                bed['right_heart_rate'],
                bed['right_hrv'],
                bed['right_respiratory_rate'],
                bed['right_sleep_score'],
                bed['right_restful'],
                bed['right_restless'],
                bed.get('right_out_of_bed', ''),
                bed.get('right_fall_asleep_period', ''),
                bed.get('right_start_date', ''),
                bed.get('right_end_date', ''),
                ""
            ]
            
            worksheet.append_row(row_data, value_input_option="USER_ENTERED")
            logger.info(f"✅ Row added: {data['date']} {data['time']} EDT")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push to sheets: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def sync(self) -> bool:
        """Run complete sync"""
        try:
            if not await self.login_sleep_number():
                return False
            
            if not self.login_google_sheets():
                return False
                
            existing_dates = self.get_existing_dates()
            
            logger.info("🔄 Starting smart auto-backfill (checking last 30 days)...")
            now = datetime.now(EASTERN)
            
            # Check last 30 days (oldest first, ending with today as 0)
            for i in range(30, -1, -1):
                target_date = now - timedelta(days=i)
                date_str = target_date.strftime("%Y-%m-%d")
                
                if date_str in existing_dates:
                    logger.info(f"⏭️  Skipping {date_str} (already in sheet)")
                    continue
                    
                logger.info(f"📅 Fetching missing data for {date_str}...")
                data = await self.fetch_bed_data(target_date)
                if data:
                    self.push_to_sheets(data)
                
                # Small delay to avoid rate limits when backfilling multiple days
                if i > 0:
                    await asyncio.sleep(1)
            
            logger.info("✨ Sync completed successfully!\n")
            return True
        finally:
            if self.api:
                await self.api.close_session()

async def main():
    """Main entry point"""
    email = os.getenv("SLEEP_NUMBER_EMAIL")
    password = os.getenv("SLEEP_NUMBER_PASSWORD")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    if not all([email, password, sheet_id]):
        print("❌ Missing required environment variables:")
        if not email:
            print("   - SLEEP_NUMBER_EMAIL")
        if not password:
            print("   - SLEEP_NUMBER_PASSWORD")
        if not sheet_id:
            print("   - GOOGLE_SHEETS_ID")
        return False
    
    syncer = SleepNumberSync(email, password, sheet_id)
    success = await syncer.sync()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
