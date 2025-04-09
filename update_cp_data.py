import csv
import os
from app import create_app
from models import CP, db
import logging

def update_cp_data():
    app = create_app()
    with app.app_context():
        # Clear existing CP data
        CP.query.delete()
        db.session.commit()
        
        # Read and insert new CP data
        with open('cp_data.csv', 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Convert empty strings to None for foreign keys
                    for key in ['PIN1_ID', 'PIN2_ID', 'PIN3_ID', 'PIN4_ID', 
                              'TIGE_1_ID', 'TIGE_2_ID', 'RESSORT_1_ID', 'RESSORT_2_ID']:
                        if not row[key] or row[key].strip() == '':
                            row[key] = None
                        else:
                            try:
                                row[key] = int(row[key])
                            except ValueError:
                                row[key] = None
                    
                    # Convert empty strings to None for quantities
                    for key in ['Qte_1', 'Qte_2', 'Qte_3', 'QTE_4', 
                              'Qte_Tige_1', 'Qte_Tige_2']:
                        if not row[key] or row[key].strip() == '':
                            row[key] = None
                        else:
                            try:
                                row[key] = int(row[key])
                            except ValueError:
                                row[key] = None
                    
                    # Create new CP record
                    cp = CP(
                        CP_ID=int(row['CP_ID']),
                        Client_ID_1=row['Client_ID_1'],
                        PRJ_ID1=row['PRJ_ID1'],
                        CP=row['CP'],
                        Image=row['Image'],
                        OT_rfrence=row['OT_rfrence'],
                        PIN1_ID=row['PIN1_ID'],
                        Qte_1=row['Qte_1'],
                        PIN2_ID=row['PIN2_ID'],
                        Qte_2=row['Qte_2'],
                        PIN3_ID=row['PIN3_ID'],
                        Qte_3=row['Qte_3'],
                        PIN4_ID=row['PIN4_ID'],
                        QTE_4=row['QTE_4'],
                        TIGE_1_ID=row['TIGE_1_ID'],
                        Qte_Tige_1=row['Qte_Tige_1'],
                        TIGE_2_ID=row['TIGE_2_ID'],
                        Qte_Tige_2=row['Qte_Tige_2'],
                        RESSORT_1_ID=row['RESSORT_1_ID'],
                        RESSORT_2_ID=row['RESSORT_2_ID']
                    )
                    db.session.add(cp)
                except Exception as e:
                    logging.error(f"Error processing row: {str(e)}")
                    logging.error(f"Row data: {row}")
                    continue
            
            try:
                db.session.commit()
                logging.info("Successfully updated CP data")
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error committing changes: {str(e)}")

if __name__ == '__main__':
    update_cp_data() 