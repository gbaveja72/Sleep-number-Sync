#!/usr/bin/env python3
"""
Debug script to dump raw Sleep Number data.
Run this script with your environment variables set to see exactly what SleepIQ returns.
"""

import asyncio
import os
import json
from asyncsleepiq import AsyncSleepIQ, LOGIN_COOKIE

async def main():
    email = os.getenv("SLEEP_NUMBER_EMAIL")
    password = os.getenv("SLEEP_NUMBER_PASSWORD")
    
    if not email or not password:
        print("❌ Missing SLEEP_NUMBER_EMAIL or SLEEP_NUMBER_PASSWORD environment variables.")
        return
        
    print("🔐 Authenticating...")
    api = AsyncSleepIQ(login_method=LOGIN_COOKIE)
    await api.login(email, password)
    
    print("📊 Fetching bed data...")
    await api.init_beds()
    await api.fetch_bed_statuses()
    for bed in api.beds.values():
        for sleeper in bed.sleepers:
            await sleeper.fetch_sleep_data()
    
    for bed_id, bed in api.beds.items():
        print(f"\n================ BED: {bed.name} ================")
        print(f"ID: {bed_id}")
        
        for sleeper in bed.sleepers:
            print(f"\n--- SLEEPER: {sleeper.name} (Side: {sleeper.side}) ---")
            print(f"In Bed: {sleeper.in_bed}")
            print(f"Sleep Number: {sleeper.sleep_number}")
            print(f"Pressure: {sleeper.pressure}")
            
            if hasattr(sleeper, 'sleep_data') and sleeper.sleep_data:
                print(f"\n>>> Sleep Data (vars):")
                sd_dict = vars(sleeper.sleep_data)
                print(json.dumps(sd_dict, indent=2, default=str))
            else:
                print("\n>>> No sleep data available for this sleeper right now.")
                
    await api.close_session()
    print("\n✅ Debug complete.")

if __name__ == "__main__":
    asyncio.run(main())
