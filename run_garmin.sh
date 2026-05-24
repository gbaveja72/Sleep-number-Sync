#!/bin/bash

# Navigate to the correct directory
cd "/Users/gbaveja/Documents/Files/Anti Gravity/Sleep Number"

# Export the Google Sheet ID
export GOOGLE_SHEETS_ID="1yWvLH6sm4iDyOTxeZsXJuuMALYAFGnPiBdlrsH9M1zs"

# Run the garmin sync using the virtual environment python
./venv/bin/python garmin_sync.py

# Log completion
echo "Garmin sync ran at $(date)" >> garmin_sync.log
