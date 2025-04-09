import csv
from app import create_app
from models import APN, CP
from extensions import db

def populate_database():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Populate APN table
        with open('apn_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                apn = APN(
                    PIN_id=int(row['PIN_id']),
                    DPN=row['DPN'],
                    Image=row['Image'],
                    Ref_Emdep=row['Ref_Emdep'],
                    Ref_Ingun=row['Ref_Ingun'],
                    Ref_Fenmmital=row['Ref_Fenmmital'],
                    Ref_Ptr=row['Ref_Ptr'],
                    Type=row['Type'],
                    Multi_APN=row['Multi_APN']
                )
                db.session.add(apn)
        
        # Populate CP table
        with open('cp_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cp = CP(
                    CP_ID=int(row['CP_ID']),
                    Client_ID_1=row['Client_ID_1'],
                    PRJ_ID1=row['PRJ_ID1'],
                    CP=row['CP'],
                    Image=row['Image'],
                    OT_rfrence=row['OT_rfrence'],
                    PIN1_ID=int(row['PIN1_ID']) if row['PIN1_ID'] else None,
                    Qte_1=int(row['Qte_1']) if row['Qte_1'] else None,
                    PIN2_ID=int(row['PIN2_ID']) if row['PIN2_ID'] else None,
                    Qte_2=int(row['Qte_2']) if row['Qte_2'] else None,
                    PIN3_ID=int(row['PIN3_ID']) if row['PIN3_ID'] else None,
                    Qte_3=int(row['Qte_3']) if row['Qte_3'] else None,
                    PIN4_ID=int(row['PIN4_ID']) if row['PIN4_ID'] else None,
                    QTE_4=int(row['QTE_4']) if row['QTE_4'] else None,
                    TIGE_1_ID=int(row['TIGE_1_ID']) if row['TIGE_1_ID'] else None,
                    Qte_Tige_1=int(row['Qte_Tige_1']) if row['Qte_Tige_1'] else None,
                    TIGE_2_ID=int(row['TIGE_2_ID']) if row['TIGE_2_ID'] else None,
                    Qte_Tige_2=int(row['Qte_Tige_2']) if row['Qte_Tige_2'] else None,
                    RESSORT_1_ID=int(row['RESSORT_1_ID']) if row['RESSORT_1_ID'] else None,
                    RESSORT_2_ID=int(row['RESSORT_2_ID']) if row['RESSORT_2_ID'] else None
                )
                db.session.add(cp)
        
        # Commit all changes
        db.session.commit()
        print("Database populated successfully!")

if __name__ == '__main__':
    populate_database() 