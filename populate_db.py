import csv
from app import create_app
from models import APN, CP
from extensions import db
import logging # Add logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def populate_database():
    app = create_app()
    
    with app.app_context():
        logging.info("Clearing existing data...")
        db.drop_all()
        db.create_all()
        logging.info("Database cleared and recreated.")
        
        # Populate APN table
        logging.info("Populating APN table...")
        try:
            with open('apn_data.csv', 'r', encoding='utf-8-sig') as f: # Use utf-8-sig
                reader = csv.DictReader(f)
                apn_count = 0
                for i, row in enumerate(reader):
                    try:
                        # Basic validation
                        if not row.get('PIN_id') or not row['PIN_id'].strip():
                            logging.warning(f"Skipping APN row {i+1} due to missing or empty PIN_id: {row}")
                            continue

                        apn = APN(
                            PIN_id=int(row['PIN_id']),
                            DPN=row.get('DPN'), # Use .get for safety
                            Image=row.get('Image'),
                            Ref_Emdep=row.get('Ref_Emdep'),
                            Ref_Ingun=row.get('Ref_Ingun'),
                            Ref_Fenmmital=row.get('Ref_Fenmmital'),
                            Ref_Ptr=row.get('Ref_Ptr'),
                            Type=row.get('Type'),
                            Multi_APN=row.get('Multi_APN')
                        )
                        db.session.add(apn)
                        apn_count += 1
                    except ValueError as e:
                        logging.error(f"ValueError processing APN row {i+1}: {row} - Error: {e}")
                    except KeyError as e:
                        logging.error(f"KeyError processing APN row {i+1}: {row} - Missing key: {e}")
                    except Exception as e:
                        logging.error(f"Unexpected error processing APN row {i+1}: {row} - Error: {e}")
            logging.info(f"Added {apn_count} APN records.")
        except FileNotFoundError:
            logging.error("apn_data.csv not found. Cannot populate APN table.")
        except Exception as e:
            logging.error(f"An error occurred while reading apn_data.csv: {e}")


        # Populate CP table
        logging.info("Populating CP table...")
        try:
            with open('cp_data.csv', 'r', encoding='utf-8-sig') as f: # Use utf-8-sig
                reader = csv.DictReader(f)
                cp_count = 0
                for i, row in enumerate(reader):
                    try:
                        cp_id_val = row.get('CP_ID') # Use .get() for safety
                        if not cp_id_val or not cp_id_val.strip():
                            logging.warning(f"Skipping CP row {i+1} due to missing or empty CP_ID: {row}")
                            continue
                        
                        # Helper function to safely convert to int
                        def safe_int(value):
                            if value and str(value).strip():
                                return int(value)
                            return None

                        cp = CP(
                            CP_ID=int(cp_id_val), # Already checked it exists and is not empty
                            Client_ID_1=row.get('Client_ID_1'), # Use .get for safety
                            PRJ_ID1=row.get('PRJ_ID1'),
                            CP=row.get('CP'),
                            Image=row.get('Image'),
                            OT_rfrence=row.get('OT_rfrence'),
                            PIN1_ID=safe_int(row.get('PIN1_ID')),
                            Qte_1=safe_int(row.get('Qte_1')),
                            PIN2_ID=safe_int(row.get('PIN2_ID')),
                            Qte_2=safe_int(row.get('Qte_2')),
                            PIN3_ID=safe_int(row.get('PIN3_ID')),
                            Qte_3=safe_int(row.get('Qte_3')),
                            PIN4_ID=safe_int(row.get('PIN4_ID')),
                            QTE_4=safe_int(row.get('QTE_4')), # Note: Header has QTE_4
                            TIGE_1_ID=safe_int(row.get('TIGE_1_ID')),
                            Qte_Tige_1=safe_int(row.get('Qte_Tige_1')),
                            TIGE_2_ID=safe_int(row.get('TIGE_2_ID')),
                            Qte_Tige_2=safe_int(row.get('Qte_Tige_2')),
                            RESSORT_1_ID=safe_int(row.get('RESSORT_1_ID')),
                            RESSORT_2_ID=safe_int(row.get('RESSORT_2_ID'))
                        )
                        db.session.add(cp)
                        cp_count += 1
                    except ValueError as e:
                        logging.error(f"ValueError processing CP row {i+1}: {row} - Error: {e}")
                    except KeyError as e: # Should be less likely now with .get()
                        logging.error(f"KeyError processing CP row {i+1}: {row} - Missing key: {e}")
                    except Exception as e:
                        logging.error(f"Unexpected error processing CP row {i+1}: {row} - Error: {e}")
            logging.info(f"Added {cp_count} CP records.")
        except FileNotFoundError:
            logging.error("cp_data.csv not found. Cannot populate CP table.")
        except Exception as e:
            logging.error(f"An error occurred while reading cp_data.csv: {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            logging.info("Database populated successfully!")
        except Exception as e:
            logging.error(f"Error committing changes to the database: {e}")
            db.session.rollback() # Rollback on error

if __name__ == '__main__':
    populate_database() 