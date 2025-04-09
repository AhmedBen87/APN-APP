import os
import csv
import logging
from app import app, db
from models import CP, APN

# Set up logging
logging.basicConfig(level=logging.INFO)

def clean_csv_value(value):
    """Clean CSV values by removing quotes and handling empty strings."""
    if value is None:
        return None

    value = str(value).strip()

    # Remove surrounding quotes and newlines
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        value = value[1:-1].strip()

    # Handle empty strings and NA values
    if value == '' or value.lower() in ['na', 'n/a']:
        return None

    return value

def insert_cp_data():
    """Insert CP data from CSV file into the database."""
    # First, delete all existing CP records
    CP.query.delete()
    db.session.commit()

    csv_path = 'cp_data.csv'

    total_rows = 0
    inserted_rows = 0
    error_rows = 0

    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                total_rows += 1

                try:
                    # Helper function to safely convert to integer
                    def safe_int(val):
                        val = clean_csv_value(val)
                        return int(val) if val and val.isdigit() else None

                    cp = CP(
                        CP_ID=int(row['CP_ID']),
                        Client_ID_1=clean_csv_value(row['Client_ID_1']),
                        PRJ_ID1=clean_csv_value(row['PRJ_ID1']),
                        CP=clean_csv_value(row['CP']),
                        Image=clean_csv_value(row['Image']),
                        OT_rfrence=clean_csv_value(row['OT_rfrence']),
                        PIN1_ID=safe_int(row['PIN1_ID']),
                        Qte_1=safe_int(row['Qte_1']),
                        PIN2_ID=safe_int(row['PIN2_ID']),
                        Qte_2=safe_int(row['Qte_2']),
                        PIN3_ID=safe_int(row['PIN3_ID']),
                        Qte_3=safe_int(row['Qte_3']),
                        PIN4_ID=safe_int(row['PIN4_ID']),
                        QTE_4=safe_int(row['QTE_4']),
                        TIGE_1_ID=safe_int(row['TIGE_1_ID']),
                        Qte_Tige_1=safe_int(row['Qte_Tige_1']),
                        TIGE_2_ID=safe_int(row['TIGE_2_ID']),
                        Qte_Tige_2=safe_int(row['Qte_Tige_2']),
                        RESSORT_1_ID=safe_int(row['RESSORT_1_ID']),
                        RESSORT_2_ID=safe_int(row['RESSORT_2_ID'])
                    )

                    db.session.add(cp)
                    inserted_rows += 1

                    # Commit every 10 records
                    if inserted_rows % 10 == 0:
                        db.session.commit()
                        logging.info(f"Inserted {inserted_rows} records so far")

                except Exception as e:
                    error_rows += 1
                    logging.error(f"Error inserting CP_ID {row['CP_ID']}: {str(e)}")
                    db.session.rollback()

            # Commit any remaining records
            db.session.commit()

        logging.info(f"""
        Data import completed:
        Total rows processed: {total_rows}
        Successfully inserted: {inserted_rows}
        Failed rows: {error_rows}
        """)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

# Create a CSV file from the provided data
def create_csv_from_data(data_path, output_path='cp_data.csv'):
    """Create a CSV file from the provided data file."""
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = f.read()

        with open(output_path, 'w', encoding='utf-8', newline='') as csv_out:
            csv_out.write(data)

        logging.info(f"CSV file created at {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error creating CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        # Path to the provided data file
        data_path = 'attached_assets/Pasted-CP-ID-Client-ID-1-PRJ-ID1-CP-Image-OT-rfrence-PIN1-ID-Qte-1-PIN2-ID-Qte-2-PIN3-ID-Qte-3-PIN4-ID-QTE--1743756864980.txt'

        # Create CSV file from the provided data
        if create_csv_from_data(data_path):
            # Insert data into the database
            insert_cp_data()
        else:
            logging.error("Failed to create CSV file. Data import aborted.")