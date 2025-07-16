#!/usr/bin/env python3
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing imports...")
    from src.models.user import db
    print("✓ user model imported")
    
    from src.models.customer import Customer
    print("✓ customer model imported")
    
    from src.models.crew_member import CrewMember
    print("✓ crew_member model imported")
    
    from src.models.crew import Crew
    print("✓ crew model imported")
    
    from src.models.appointment import Appointment
    print("✓ appointment model imported")
    
    from src.routes.customer import customer_bp
    print("✓ customer routes imported")
    
    from src.routes.crew_member import crew_member_bp
    print("✓ crew_member routes imported")
    
    from src.routes.crew import crew_bp
    print("✓ crew routes imported")
    
    from src.routes.appointment import appointment_bp
    print("✓ appointment routes imported")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()

