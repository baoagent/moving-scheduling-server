from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.crew_member import CrewMember

crew_member_bp = Blueprint('crew_member', __name__)

@crew_member_bp.route('/crew_members', methods=['GET'])
def get_crew_members():
    try:
        crew_members = CrewMember.query.all()
        return jsonify([member.to_dict() for member in crew_members]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crew_member_bp.route('/crew_members/<int:member_id>', methods=['GET'])
def get_crew_member(member_id):
    try:
        member = CrewMember.query.get_or_404(member_id)
        return jsonify(member.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crew_member_bp.route('/crew_members', methods=['POST'])
def create_crew_member():
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        member = CrewMember(
            name=data['name'],
            phone=data.get('phone'),
            email=data.get('email'),
            position=data.get('position'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify(member.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_member_bp.route('/crew_members/<int:member_id>', methods=['PUT'])
def update_crew_member(member_id):
    try:
        member = CrewMember.query.get_or_404(member_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        member.name = data.get('name', member.name)
        member.phone = data.get('phone', member.phone)
        member.email = data.get('email', member.email)
        member.position = data.get('position', member.position)
        member.is_active = data.get('is_active', member.is_active)
        
        db.session.commit()
        
        return jsonify(member.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_member_bp.route('/crew_members/<int:member_id>', methods=['DELETE'])
def delete_crew_member(member_id):
    try:
        member = CrewMember.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': 'Crew member deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

