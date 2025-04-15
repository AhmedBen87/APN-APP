from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class APN(db.Model):
    """APTIV Part Number model"""
    __tablename__ = 'APN'
    
    PIN_id = db.Column(db.Integer, primary_key=True)
    DPN = db.Column(db.Text, index=True)
    Image = db.Column(db.Text)
    Ref_Emdep = db.Column(db.Text)
    Ref_Ingun = db.Column(db.Text)
    Ref_Fenmmital = db.Column(db.Text)
    Ref_Ptr = db.Column(db.Text)
    Type = db.Column(db.Text, index=True)
    Multi_APN = db.Column(db.Text)
    Location = db.Column(db.Text)  # Format: "ARMOIRE C-07", will store cabinet location
    
    def __repr__(self):
        return f"<APN(PIN_id={self.PIN_id}, DPN={self.DPN}, Type={self.Type})>"

class CP(db.Model):
    """Counterpart model"""
    __tablename__ = 'CP'
    
    CP_ID = db.Column(db.Integer, primary_key=True)
    Client_ID_1 = db.Column(db.Text, index=True)
    PRJ_ID1 = db.Column(db.Text, index=True)
    CP = db.Column(db.Text, index=True)
    Image = db.Column(db.Text)
    OT_rfrence = db.Column(db.Text)
    
    # APN Foreign Keys and Quantities
    PIN1_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    Qte_1 = db.Column(db.Integer)
    PIN2_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    Qte_2 = db.Column(db.Integer)
    PIN3_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    Qte_3 = db.Column(db.Integer)
    PIN4_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    QTE_4 = db.Column(db.Integer)
    TIGE_1_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    Qte_Tige_1 = db.Column(db.Integer)
    TIGE_2_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    Qte_Tige_2 = db.Column(db.Integer)
    RESSORT_1_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    RESSORT_2_ID = db.Column(db.Integer, db.ForeignKey('APN.PIN_id'), index=True)
    
    # Relationships with APN
    apn1 = db.relationship('APN', foreign_keys=[PIN1_ID])
    apn2 = db.relationship('APN', foreign_keys=[PIN2_ID])
    apn3 = db.relationship('APN', foreign_keys=[PIN3_ID])
    apn4 = db.relationship('APN', foreign_keys=[PIN4_ID])
    apn5 = db.relationship('APN', foreign_keys=[TIGE_1_ID])
    apn6 = db.relationship('APN', foreign_keys=[TIGE_2_ID])
    apn7 = db.relationship('APN', foreign_keys=[RESSORT_1_ID])
    apn8 = db.relationship('APN', foreign_keys=[RESSORT_2_ID])
    
    def __repr__(self):
        return f"<CP(CP_ID={self.CP_ID}, Client={self.Client_ID_1}, CP={self.CP})>"

class User(db.Model, UserMixin):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
        
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
