## For K. Hassan
This a comprehensive summary of your CounterpartSearch project that covers all aspects from interface to database and deployment requirements.

# CounterpartSearch Project Summary

## Project Overview
A Flask-based web application for searching and managing APTIV probe counterparts (CPs) and APTIV Part Numbers (APNs). The application provides a user-friendly interface for maintenance staff to search, view, and manage probe components with their associated images and references.

## Technical Stack
- **Backend**: Python 3.x with Flask 3.0.2
- **Database**: SQLite with SQLAlchemy 2.0.27
- **Frontend**: HTML5, Bootstrap, JavaScript
- **Image Handling**: Native Flask file serving
- **Dependencies**: Listed in requirements.txt:
  ```
  flask==3.0.2
  flask-sqlalchemy==3.1.1
  sqlalchemy==2.0.27
  email-validator==2.1.0.post1
  gunicorn==21.2.0
  psycopg2-binary==2.9.9
  routes==2.5.1
  ```

## Project Structure
```
CounterpartSearch/
├── app.py                 # Main application file
├── routes.py             # Route definitions
├── models.py            # Database models
├── helpers.py           # Helper functions
├── extensions.py        # Flask extensions
├── requirements.txt     # Project dependencies
├── templates/           # HTML templates
│   ├── layout.html     # Base template
│   ├── index.html      # Landing page
│   └── results.html    # Search results
├── static/             # Static assets
│   ├── css/           # CSS files
│   ├── js/            # JavaScript files
│   ├── cp_images/     # CP images
│   ├── cp_sub51_images/ # SUB51 CP images
│   ├── apn_images/    # APN images
│   └── apn_pin_images/ # PIN APN images
└── attached_assets/    # Source images
    ├── CP/            # CP source images
    ├── CP_SUB51/     # SUB51 CP source images
    ├── APN/          # APN source images
    └── CUSTOMER/     # Customer logo images
```

## Database Schema

### CP (Counterpart) Table
```sql
CREATE TABLE CP (
    CP_ID INTEGER PRIMARY KEY,
    Client_ID_1 TEXT,        -- Customer name
    PRJ_ID1 TEXT,           -- Car line
    CP TEXT,                -- CP identifier
    Image TEXT,             -- Image path
    OT_rfrence TEXT,        -- OT reference
    PIN1_ID INTEGER,        -- Foreign key to APN
    Qte_1 INTEGER,          -- Quantity for PIN1
    PIN2_ID INTEGER,        -- Foreign key to APN
    Qte_2 INTEGER,          -- Quantity for PIN2
    PIN3_ID INTEGER,        -- Foreign key to APN
    Qte_3 INTEGER,          -- Quantity for PIN3
    PIN4_ID INTEGER,        -- Foreign key to APN
    QTE_4 INTEGER,          -- Quantity for PIN4
    TIGE_1_ID INTEGER,      -- Foreign key to APN
    Qte_Tige_1 INTEGER,     -- Quantity for TIGE1
    TIGE_2_ID INTEGER,      -- Foreign key to APN
    Qte_Tige_2 INTEGER,     -- Quantity for TIGE2
    RESSORT_1_ID INTEGER,   -- Foreign key to APN
    RESSORT_2_ID INTEGER    -- Foreign key to APN
)
```

### APN (APTIV Part Number) Table
```sql
CREATE TABLE APN (
    PIN_id INTEGER PRIMARY KEY,
    DPN TEXT,              -- Part number
    Image TEXT,            -- Image path
    Ref_Emdep TEXT,       -- Emdep reference
    Ref_Ingun TEXT,       -- Ingun reference
    Ref_Fenmmital TEXT,   -- Fenmmital reference
    Ref_Ptr TEXT,         -- PTR reference
    Type TEXT,            -- APN type
    Multi_APN TEXT        -- Multiple APN reference
)
```

## Key Features

### 1. User Interface
- **Customer Selection**:
  - Displays customer logos from attached_assets/CUSTOMER/
  - Logos positioned at bottom-left with reduced opacity
  - White background with hover effects

- **Car Line Selection**:
  - Dynamically populated based on selected customer
  - Filtered from database based on Client_ID_1

- **Search Interface**:
  - Prefix-based search for CP names
  - Auto-suggestions as user types
  - Respects selected customer and car line

### 2. Image Handling
- **CP Images**:
  - Regular CPs: stored in static/cp_images/
  - SUB51 CPs: stored in static/cp_sub51_images/
  - Source images in attached_assets/CP/ and CP_SUB51/

- **APN Images**:
  - Regular APNs: stored in static/apn_images/
  - PIN APNs: stored in static/apn_pin_images/
  - Source images in attached_assets/APN/

- **Customer Logos**:
  - Stored in attached_assets/CUSTOMER/
  - Supports both JPG and PNG formats

### 3. Search Functionality
- Prefix-based search for CP names
- Filters by customer and car line
- Handles special cases like L/R variants
- Returns multiple matches in card format

### 4. Results Display
- CP details with images
- Associated APN references
- APN images and quantities
- Reference numbers for each APN

## Setup and Deployment

### Prerequisites
1. Python 3.x installed
2. pip package manager
3. Virtual environment (recommended)

### Installation Steps
1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure image directories exist:
   - static/cp_images/
   - static/cp_sub51_images/
   - static/apn_images/
   - static/apn_pin_images/

### Running the Application
```bash
python app.py
```
Access at http://localhost:5000

## Image Requirements
1. CP images:
   - Format: JPG/JPEG
   - Named exactly as in database Image field
   - Placed in appropriate CP or CP_SUB51 folder

2. APN images:
   - Format: PNG/JPG
   - Named exactly as in database Image field
   - Placed in appropriate APN or PIN folder

3. Customer logos:
   - Format: JPG/PNG
   - Named exactly as Client_ID_1 in database
   - Placed in CUSTOMER folder

## Branding
- APTIV logo in navigation bar with red dots
- Footer with signature:
  "AHMED BENMIMOUN - Maintenance Department, APTIV M6"
  "Cité Mohammed VI Tanger Tech (SATT)"
- Copyright notice: "© 2025 APTIV Probes Database"

This summary provides a complete overview of the project's structure, functionality, and requirements. It can be used to understand the project's architecture, deploy it in a new environment, or make modifications to its functionality.
