from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CHD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ThoiGian = db.Column(db.String(100), nullable=False)
    TenCHD = db.Column(db.String(100), nullable=False)
    TinhCach = db.Column(db.String(100), nullable=False)
    DiemManh = db.Column(db.String(100), nullable=False)
    DiemYeu = db.Column(db.String(100), nullable=False)

