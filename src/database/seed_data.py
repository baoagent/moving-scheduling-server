"""
Database seeding functionality for development and testing

This module provides functions to populate the database with sample data
for development, testing, and demonstration purposes.
"""

from datetime import datetime, date, time, timedelta
from src.models.user import db
from src.models.customer import Customer
from src.models.crew_member import CrewMember
from src.models.crew import Crew
from src.models.appointment import Appointment
import logging

logger = logging.getLogger(__name__)

def seed_customers():
    """Seed sample customers for testing"""
    customers_data = [
        {
            'name': 'John Smith',
            'phone': '555-0101',
            'email': 'john.smith@email.com',
            'address': '123 Main St, Anytown, ST 12345'
        },
        {
            'name': 'Sarah Johnson',
            'phone': '555-0102',
            'email': 'sarah.johnson@email.com',
            'address': '456 Oak Ave, Somewhere, ST 12346'
        },
        {
            'name': 'Michael Brown',
            'phone': '555-0103',
            'email': 'michael.brown@email.com',
            'address': '789 Pine Rd, Elsewhere, ST 12347'
        },
        {
            'name': 'Emily Davis',
            'phone': '555-0104',
            'email': 'emily.davis@email.com',
            'address': '321 Elm St, Nowhere, ST 12348'
        },
        {
            'name': 'David Wilson',
            'phone': '555-0105',
            'email': 'david.wilson@email.com',
            'address': '654 Maple Dr, Anywhere, ST 12349'
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        # Check if customer already exists
        existing = Customer.query.filter_by(phone=customer_data['phone']).first()
        if not existing:
            customer = Customer(**customer_data)
            db.session.add(customer)
            created_customers.append(customer)
            logger.info(f"Created customer: {customer_data['name']}")
    
    db.session.commit()
    return created_customers

def seed_crew_members():
    """Seed sample crew members for testing"""
    crew_members_data = [
        {
            'name': 'Mike Rodriguez',
            'phone': '555-1001',
            'email': 'mike.rodriguez@movingco.com',
            'position': 'Team Lead',
            'is_active': True
        },
        {
            'name': 'James Thompson',
            'phone': '555-1002',
            'email': 'james.thompson@movingco.com',
            'position': 'Mover',
            'is_active': True
        },
        {
            'name': 'Carlos Martinez',
            'phone': '555-1003',
            'email': 'carlos.martinez@movingco.com',
            'position': 'Mover',
            'is_active': True
        },
        {
            'name': 'Robert Lee',
            'phone': '555-1004',
            'email': 'robert.lee@movingco.com',
            'position': 'Driver',
            'is_active': True
        },
        {
            'name': 'Anthony Garcia',
            'phone': '555-1005',
            'email': 'anthony.garcia@movingco.com',
            'position': 'Mover',
            'is_active': True
        }
    ]
    
    created_members = []
    for member_data in crew_members_data:
        # Check if crew member already exists
        existing = CrewMember.query.filter_by(phone=member_data['phone']).first()
        if not existing:
            member = CrewMember(**member_data)
            db.session.add(member)
            created_members.append(member)
            logger.info(f"Created crew member: {member_data['name']}")
    
    db.session.commit()
    return created_members

def seed_crews(crew_members):
    """Seed sample crews for testing"""
    if len(crew_members) < 4:
        logger.warning("Not enough crew members to create sample crews")
        return []
    
    crews_data = [
        {
            'name': 'Alpha Team',
            'description': 'Primary moving crew for residential moves',
            'is_active': True
        },
        {
            'name': 'Beta Team',
            'description': 'Secondary crew for commercial and large moves',
            'is_active': True
        }
    ]
    
    created_crews = []
    for i, crew_data in enumerate(crews_data):
        # Check if crew already exists
        existing = Crew.query.filter_by(name=crew_data['name']).first()
        if not existing:
            crew = Crew(**crew_data)
            db.session.add(crew)
            db.session.flush()  # Get the ID
            
            # Assign crew members (2-3 per crew) using the many-to-many relationship
            start_idx = i * 2
            end_idx = min(start_idx + 3, len(crew_members))
            for j in range(start_idx, end_idx):
                if j < len(crew_members):
                    crew.members.append(crew_members[j])
            
            created_crews.append(crew)
            logger.info(f"Created crew: {crew_data['name']}")
    
    db.session.commit()
    return created_crews

def seed_appointments(customers, crews):
    """Seed sample appointments for testing"""
    if not customers or not crews:
        logger.warning("No customers or crews available for creating appointments")
        return []
    
    # Create appointments for the next 30 days
    base_date = date.today()
    appointments_data = []
    
    for i in range(10):  # Create 10 sample appointments
        appointment_date = base_date + timedelta(days=i + 1)
        appointment_time = time(hour=9 + (i % 8), minute=0)  # 9 AM to 4 PM
        
        customer = customers[i % len(customers)]
        crew = crews[i % len(crews)]
        
        appointment_data = {
            'customer_id': customer.id,
            'crew_id': crew.id,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'estimated_duration': 120 + (i % 3) * 60,  # 2-4 hours
            'origin_address': f'{100 + i * 10} Source St, Origin City, ST 1000{i}',
            'destination_address': f'{200 + i * 10} Dest Ave, Destination City, ST 2000{i}',
            'status': ['scheduled', 'confirmed', 'in_progress'][i % 3],
            'notes': f'Sample appointment #{i + 1} - Handle with care',
            'estimated_cost': 300.0 + (i * 50.0)
        }
        appointments_data.append(appointment_data)
    
    created_appointments = []
    for appointment_data in appointments_data:
        appointment = Appointment(**appointment_data)
        db.session.add(appointment)
        created_appointments.append(appointment)
        logger.info(f"Created appointment for {appointment_data['appointment_date']}")
    
    db.session.commit()
    return created_appointments

def seed_all_data():
    """Seed all sample data"""
    try:
        logger.info("Starting database seeding...")
        
        # Seed in order due to dependencies
        customers = seed_customers()
        crew_members = seed_crew_members()
        crews = seed_crews(crew_members)
        appointments = seed_appointments(customers, crews)
        
        logger.info(f"Database seeding completed successfully!")
        logger.info(f"Created: {len(customers)} customers, {len(crew_members)} crew members, "
                   f"{len(crews)} crews, {len(appointments)} appointments")
        
        return {
            'customers': len(customers),
            'crew_members': len(crew_members),
            'crews': len(crews),
            'appointments': len(appointments)
        }
    
    except Exception as e:
        logger.error(f"Error during database seeding: {str(e)}")
        db.session.rollback()
        raise

def clear_all_data():
    """Clear all data from the database (use with caution!)"""
    try:
        logger.warning("Clearing all database data...")
        
        # Delete in reverse order due to foreign key constraints
        Appointment.query.delete()
        Crew.query.delete()
        CrewMember.query.delete()
        Customer.query.delete()
        
        db.session.commit()
        logger.info("All database data cleared successfully")
        
    except Exception as e:
        logger.error(f"Error clearing database data: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    # This allows running the seeding script directly
    from src.main import app
    
    with app.app_context():
        seed_all_data()

