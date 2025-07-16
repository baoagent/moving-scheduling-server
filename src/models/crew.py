from src.models.user import db

# Association table for many-to-many relationship between Crew and CrewMember
crew_members_association = db.Table('crew_members_association',
    db.Column('crew_id', db.Integer, db.ForeignKey('crew.id'), primary_key=True),
    db.Column('crew_member_id', db.Integer, db.ForeignKey('crew_member.id'), primary_key=True)
)

class Crew(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Many-to-many relationship with CrewMember
    members = db.relationship('CrewMember', secondary=crew_members_association, lazy='subquery',
                             backref=db.backref('crews', lazy=True))
    
    # Relationship with appointments
    appointments = db.relationship('Appointment', backref='crew', lazy=True)

    def __repr__(self):
        return f'<Crew {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'members': [member.to_dict() for member in self.members]
        }

