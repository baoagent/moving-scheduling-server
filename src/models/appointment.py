from src.models.user import db
from datetime import datetime

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    crew_id = db.Column(db.Integer, db.ForeignKey('crew.id'), nullable=True)
    
    # Date and time information
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    estimated_duration = db.Column(db.Integer, nullable=True)  # Duration in minutes
    
    # Address information
    origin_address = db.Column(db.Text, nullable=False)
    destination_address = db.Column(db.Text, nullable=False)
    
    # Status and notes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    
    # Pricing information
    estimated_cost = db.Column(db.Float, nullable=True)
    actual_cost = db.Column(db.Float, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Appointment {self.id} - {self.customer.name if self.customer else "No Customer"}>'

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'crew_id': self.crew_id,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'estimated_duration': self.estimated_duration,
            'origin_address': self.origin_address,
            'destination_address': self.destination_address,
            'status': self.status,
            'notes': self.notes,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer': self.customer.to_dict() if self.customer else None,
            'crew': self.crew.to_dict() if self.crew else None
        }

