from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.customer import Customer

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        return jsonify([customer.to_dict() for customer in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('phone'):
            return jsonify({'error': 'Name and phone are required'}), 400
        
        customer = Customer(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            address=data.get('address')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        customer.name = data.get('name', customer.name)
        customer.phone = data.get('phone', customer.phone)
        customer.email = data.get('email', customer.email)
        customer.address = data.get('address', customer.address)
        
        db.session.commit()
        
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

