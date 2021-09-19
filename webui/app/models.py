from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    scans = db.relationship('Scan', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(128), index=True, unique=True)
    scan_params = db.Column(db.String(256), index=False, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

