from src.models.user import db

class CrewMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    position = db.Column(db.String(50), nullable=True)  # e.g., "Driver", "Helper", "Team Lead"
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<CrewMember {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'position': self.position,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

