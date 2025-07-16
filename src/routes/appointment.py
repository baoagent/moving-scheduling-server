from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.appointment import Appointment
from src.models.customer import Customer
from src.models.crew import Crew
from datetime import datetime, date, time

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
def get_appointments():
    try:
        # Support filtering by date range and status
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        query = Appointment.query
        
        if start_date:
            query = query.filter(Appointment.appointment_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Appointment.appointment_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        if status:
            query = query.filter(Appointment.status == status)
        
        appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        return jsonify([appointment.to_dict() for appointment in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/appointments', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['customer_id', 'appointment_date', 'appointment_time', 'origin_address', 'destination_address']):
            return jsonify({'error': 'customer_id, appointment_date, appointment_time, origin_address, and destination_address are required'}), 400
        
        # Validate customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Validate crew exists if provided
        if data.get('crew_id'):
            crew = Crew.query.get(data['crew_id'])
            if not crew:
                return jsonify({'error': 'Crew not found'}), 404
        
        # Parse date and time
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        appointment = Appointment(
            customer_id=data['customer_id'],
            crew_id=data.get('crew_id'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            estimated_duration=data.get('estimated_duration'),
            origin_address=data['origin_address'],
            destination_address=data['destination_address'],
            status=data.get('status', 'scheduled'),
            notes=data.get('notes'),
            estimated_cost=data.get('estimated_cost'),
            actual_cost=data.get('actual_cost')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate customer exists if being updated
        if 'customer_id' in data:
            customer = Customer.query.get(data['customer_id'])
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            appointment.customer_id = data['customer_id']
        
        # Validate crew exists if being updated
        if 'crew_id' in data:
            if data['crew_id']:
                crew = Crew.query.get(data['crew_id'])
                if not crew:
                    return jsonify({'error': 'Crew not found'}), 404
            appointment.crew_id = data['crew_id']
        
        # Update date and time if provided
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        if 'appointment_time' in data:
            appointment.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Update other fields
        appointment.estimated_duration = data.get('estimated_duration', appointment.estimated_duration)
        appointment.origin_address = data.get('origin_address', appointment.origin_address)
        appointment.destination_address = data.get('destination_address', appointment.destination_address)
        appointment.status = data.get('status', appointment.status)
        appointment.notes = data.get('notes', appointment.notes)
        appointment.estimated_cost = data.get('estimated_cost', appointment.estimated_cost)
        appointment.actual_cost = data.get('actual_cost', appointment.actual_cost)
        
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({'message': 'Appointment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
        
        appointment.status = data['status']
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

