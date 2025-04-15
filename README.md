# APN Finder 2.0

## Project Overview
A Flask-based web application for searching and displaying APTIV probe counterparts (CPs) and their associated APTIV Part Numbers (APNs). The application provides a user-friendly interface for maintenance and engineering staff to quickly find CP details, component APNs, and view related images.

## Technical Stack
- **Backend**: Python 3.x with Flask
- **Database**: SQLite (managed via Flask-SQLAlchemy)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Key Python Libraries**: Flask, Flask-SQLAlchemy, SQLAlchemy
- **Dependencies**: See `requirements.txt` for full list.

## Key Features

### 1. CP (Counterpart) Search
- Search for CPs by Customer, Carline, and CP Name (prefix search with suggestions).
- Displays detailed CP information (Customer, Carline, OT Reference, Image).
- Lists all component APNs for the found CP(s), including APN, Type, Quantity, Image, and Reference details.
- *Optimization*: Uses SQLAlchemy's `selectinload` to prevent N+1 database queries when loading related APNs for display.

### 2. APN Database with Integrated Search
- Provides a table view of the entire APN database with integrated search functionality.
- Search by APN, Emdep Reference, Fenmmital Reference, Ingun Reference, or PTR Reference.
- Displays all APN details (PIN ID, APN, Type, Image, References, Multi APN).
- Includes a "Total Qty in DB" column showing the total usage of each APN across all CPs in the database.
- APN image thumbnails are displayed (100px height) and can be clicked to view a larger version in a modal overlay.
- *Optimization*: Total quantities are calculated efficiently using database aggregation.

### 3. Location Tracking
- Track the physical location of APNs in the storage system.
- Visual cabinet representation showing drawer locations.
- Easy-to-use location update interface.

### 4. User Interface
- Clean, modern UI based on Bootstrap 5 (dark theme).
- Streamlined navigation with custom red circle favicon for better brand identity.
- Enhanced "Add" buttons with improved visibility in the CP form.
- Footer with developer credits and location information.

### 5. Database
- Uses SQLite for simple, file-based storage (`instance/probes.db`).
- Data is populated from CSV files in the `database_init` directory using dedicated scripts.
- Database schema includes indexes on frequently searched columns for improved query performance.

## User Management

APN Finder 2.0 now includes a secure user management system with role-based access control:

### User Roles
- **Admin**: Has full access to all features, including user management
- **User**: Has access to search and view data, but cannot add, edit, or delete records

### Managing Users
If you're an administrator, you can:
1. View all users: Navigate to "Manage Users" in the navigation bar
2. Add new users: Click "Add New User" on the user management page
3. Edit users: Change username, employee ID, role, or reset password
4. Delete users: Remove accounts that are no longer needed

### Security Features
- Passwords are securely hashed and never stored in plain text
- Role-based access control prevents unauthorized operations
- Only administrators can add, edit, or delete users
- Safeguards prevent deleting the last admin account

## Project Structure
```
APN-APP/
├── app.py                    # Main Flask application (App Factory)
├── routes.py                 # Route definitions and view logic
├── models.py                 # SQLAlchemy database models (APN, CP)
├── helpers.py                # Helper functions (e.g., get_apn_details)
├── extensions.py             # Flask extension initializations (e.g., SQLAlchemy)
├── requirements.txt          # Python dependencies
├── database_init/            # Database initialization scripts and data
│   ├── __init__.py           # Package initialization
│   ├── populate_db.py        # Script to populate database from CSVs
│   ├── add_first_user.py     # Script to add the first admin user
│   ├── add_location_field.py # Script to add location field to APN table
│   ├── update_admin.py       # Script to update user to admin role
│   ├── update_db_schema.py   # Script to update database schema
│   ├── apn_data.csv          # Source data for APN table
│   └── cp_data.csv           # Source data for CP table
├── scripts/                  # Utility scripts
│   ├── __init__.py           # Package initialization
│   └── generate_favicon.py   # Script to generate favicon
├── templates/                # HTML templates (Jinja2)
│   ├── layout.html           # Base template with navbar/footer
│   ├── index.html            # CP Search form page
│   ├── results.html          # CP Search results page
│   ├── results_apn.html      # APN Search results page (collapsible)
│   ├── apn_database.html     # APN Database with search functionality
│   ├── edit_apn_form.html    # Form for editing APN data
│   └── add_cp_form.html      # Form for adding new CPs
├── static/                   # Static assets (CSS, JS, Images)
│   ├── css/                  # Custom stylesheets
│   ├── js/                   # Custom JavaScript (if any)
│   ├── images/               # UI images (logos, profile pics, favicon)
│   ├── cp_images/            # Served CP images
│   ├── cp_sub51_images/      # Served SUB51 CP images
│   ├── apn_images/           # Served APN images
│   └── apn_pin_images/       # Served PIN APN images
├── attached_assets/          # Non-served assets (e.g., customer logos for display)
│   └── CUSTOMER/             # Customer logos used in UI
├── location_updates/         # Location update related files
├── .gitignore                # Specifies intentionally untracked files
├── .gitattributes            # Git attributes configuration
├── pyproject.toml            # Python project configuration
└── instance/                 # Runtime instance data (gitignore'd)
    └── probes.db             # SQLite database file
```
*Note: Source image folders that might have existed previously (`attached_assets/CP/`, `attached_assets/APN/`, etc.) are assumed to be used for preparing the images served from `static/` folders and are not directly used by the running application.* 

## Recent Updates
- **UI Improvements**: Added a red circle favicon for better visual identity
- **Navigation Simplification**: Removed the separate "Search APN" option and integrated search functionality into the APN Database page
- **Enhanced Forms**: Improved the visibility of action buttons in forms like the "Add" button in the CP form
- **Terminology Consistency**: Updated terminology from "DPN" to "APN" throughout the application

## Setup and Running

### Prerequisites
1. Python 3.x installed.
2. `pip` (Python package installer).
3. Virtual environment tool (`venv`).

### Installation
1.  **Clone the repository (or ensure you are in the project directory):**
    ```bash
    # Example: git clone <repository_url>
    cd APN-APP
    ```
2.  **Create and activate a virtual environment:**
   ```bash
    # Windows
   python -m venv venv
    .\venv\Scripts\activate
    
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
   ```
3.  **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup
*   Before running the app for the first time, or whenever the CSV data files are updated, you **must** populate the database:
    ```bash
    python database_init/populate_db.py
    ```
    *(This script will delete any existing data in `instance/probes.db` and load fresh data from the CSVs)*

### User Authentication Setup
*   Before using the application, create the first admin user:
    ```bash
    python database_init/add_first_user.py
    ```
    When prompted, enter a secure password. The default user will be "Ahmed Benmimoun" with employee ID "2465".
    
    You can also specify a different username and employee ID:
    ```bash
    python database_init/add_first_user.py "New Username" "Employee ID"
    ```

### Running the Application
1.  **Start the Flask development server:**
```bash
python app.py
```
2.  **Access the application:** Open your web browser and go to `http://127.0.0.1:5000` (or the address provided in the terminal output).
3.  **Login:** Use the credentials you set up in the "User Authentication Setup" step.

## Notes
- Ensure all necessary image files corresponding to the entries in the CSV files are present in the correct subdirectories within `static/`. Filenames must match exactly.
- The application runs in debug mode by default, which provides automatic reloading on code changes and a debugger. For production, use a proper WSGI server like Gunicorn.
