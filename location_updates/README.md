# Location Updates

This folder contains files related to updating APN locations in the database from an Excel spreadsheet.

## Contents

- `update_locations.py` - Python script that reads location data from the Excel file and updates the database
- `EMPLACEMENT le 15.03.2025 (3).xlsx` - Excel file containing APN location data
- `update_summary.md` - Summary of the last update operation
- `README.md` - This file explaining the folder contents

## How to Run

To update APN locations from the Excel file:

1. Make sure the Excel file is up to date
2. Open a terminal in this directory
3. Run the script:

```bash
python update_locations.py
```

The script will:
- Read APNs and locations from the Excel file
- Filter rows where PROCESS="ROB"
- Update matching APNs in the database with their locations
- Log the results to the terminal

## Notes

- The script automatically formats locations to ensure they use the "ARMOIRE X-YY" format
- Only APNs that exist in both the Excel file and the database will be updated
- The script will display a list of APNs that couldn't be found in the database 