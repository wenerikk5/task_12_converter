from datetime import datetime, timedelta
import uuid

from flask import url_for
import base32_lib as base32

from app import db


class User(db.Model):
    id = db.Column(db.String(8), index=True, unique=True, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    token = db.Column(db.String(36), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    records = db.relationship('Record', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User "{self.name}" ({self.id})>'

    @classmethod
    def generate_id(cls, length: int = 8):
        """Generate unique User ID."""

        new_id = base32.generate(length)
        if db.session.query(cls.query.filter(cls.id == new_id)
                                     .exists()).scalar():
            return cls.generate_id()
        return new_id

    @classmethod
    def get_token(cls, expires_in: int = (24 * 60 * 60)):
        now = datetime.utcnow()

        token = str(uuid.uuid4())
        token_expiration = now + timedelta(seconds=expires_in)
        return token, token_expiration

    @staticmethod
    def check_token(user_id: str, token: str):
        user = User.query.filter_by(id=user_id).first()
        if (
            user is None
            or user.token != token
            or user.token_expiration < datetime.utcnow()
        ):
            return None
        return user

    def update_token(self, prev_token, expires_in: int = (24 * 60 * 60)):
        """
        Update token (valid or expired) based on User ID and
        last token, which presents in DB.
        """
        if prev_token != self.token:
            return None
        now = datetime.utcnow()
        self.token = str(uuid.uuid4())
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token


class Record(db.Model):
    id = db.Column(db.String(36), index=True, unique=True, primary_key=True)
    filename = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(8), db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'<Record "{self.filename}" ({self.id})>'

    def to_dict(self):
        """Form representation dict for Record instance."""

        data = {
            'id': self.id,
            'filename': self.filename,
            'created': self.created.isoformat() + 'Z'
        }
        return data

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        """Form representation dict for list of instances in query."""

        resources = query.paginate(page=page, per_page=per_page,
                                   error_out=False)
        data = {
            'records': [record.to_dict() for record in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data
