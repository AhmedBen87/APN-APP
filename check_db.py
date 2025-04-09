from app import create_app
from models import CP, db

def check_database():
    app = create_app()
    with app.app_context():
        cp_count = CP.query.count()
        print(f"Total number of CP records in database: {cp_count}")
        
        # Print a few sample records
        print("\nSample records:")
        for cp in CP.query.limit(5):
            print(f"CP_ID: {cp.CP_ID}, Client: {cp.Client_ID_1}, CP: {cp.CP}")

if __name__ == '__main__':
    check_database() 