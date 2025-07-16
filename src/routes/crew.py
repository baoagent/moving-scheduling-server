from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.crew import Crew
from src.models.crew_member import CrewMember

crew_bp = Blueprint('crew', __name__)

@crew_bp.route('/crews', methods=['GET'])
def get_crews():
    try:
        crews = Crew.query.all()
        return jsonify([crew.to_dict() for crew in crews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews/<int:crew_id>', methods=['GET'])
def get_crew(crew_id):
    try:
        crew = Crew.query.get_or_404(crew_id)
        return jsonify(crew.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews', methods=['POST'])
def create_crew():
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        crew = Crew(
            name=data['name'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        # Add crew members if provided
        if 'member_ids' in data:
            for member_id in data['member_ids']:
                member = CrewMember.query.get(member_id)
                if member:
                    crew.members.append(member)
        
        db.session.add(crew)
        db.session.commit()
        
        return jsonify(crew.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews/<int:crew_id>', methods=['PUT'])
def update_crew(crew_id):
    try:
        crew = Crew.query.get_or_404(crew_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        crew.name = data.get('name', crew.name)
        crew.description = data.get('description', crew.description)
        crew.is_active = data.get('is_active', crew.is_active)
        
        # Update crew members if provided
        if 'member_ids' in data:
            crew.members.clear()
            for member_id in data['member_ids']:
                member = CrewMember.query.get(member_id)
                if member:
                    crew.members.append(member)
        
        db.session.commit()
        
        return jsonify(crew.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews/<int:crew_id>', methods=['DELETE'])
def delete_crew(crew_id):
    try:
        crew = Crew.query.get_or_404(crew_id)
        db.session.delete(crew)
        db.session.commit()
        
        return jsonify({'message': 'Crew deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews/<int:crew_id>/members', methods=['POST'])
def add_member_to_crew(crew_id):
    try:
        crew = Crew.query.get_or_404(crew_id)
        data = request.get_json()
        
        if not data or not data.get('member_id'):
            return jsonify({'error': 'Member ID is required'}), 400
        
        member = CrewMember.query.get_or_404(data['member_id'])
        
        if member not in crew.members:
            crew.members.append(member)
            db.session.commit()
        
        return jsonify(crew.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crew_bp.route('/crews/<int:crew_id>/members/<int:member_id>', methods=['DELETE'])
def remove_member_from_crew(crew_id, member_id):
    try:
        crew = Crew.query.get_or_404(crew_id)
        member = CrewMember.query.get_or_404(member_id)
        
        if member in crew.members:
            crew.members.remove(member)
            db.session.commit()
        
        return jsonify(crew.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

