from flask import Blueprint, request, jsonify
from app import db
from models import Vacancy

vacancy_bp = Blueprint('vacancies', __name__)

@vacancy_bp.route('/', methods=['GET'])
def get_vacancies():
    """Get all vacancies with optional filtering"""
    try:
        # Get query parameters for filtering
        location = request.args.get('location')
        school = request.args.get('school')
        level = request.args.get('level')
        status = request.args.get('status', 'active')
        
        # Build query with filters
        query = Vacancy.query
        
        if location:
            query = query.filter(Vacancy.location.ilike(f'%{location}%'))
        if school:
            query = query.filter(Vacancy.school.ilike(f'%{school}%'))
        if level:
            query = query.filter(Vacancy.level.ilike(f'%{level}%'))
        if status:
            query = query.filter(Vacancy.status == status)
        
        vacancies = query.all()
        return jsonify([vacancy.to_dict() for vacancy in vacancies]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/', methods=['POST'])
def create_vacancy():
    """Create a new vacancy"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        if not data.get('posted_by_id'):
            return jsonify({'error': 'Posted by ID is required'}), 400
        
        vacancy = Vacancy(
            title=data['title'],
            description=data.get('description', ''),
            requirements=data.get('requirements', ''),
            location=data.get('location', ''),
            school=data.get('school', ''),
            level=data.get('level', ''),
            department=data.get('department', ''),
            salary_range=data.get('salary_range', ''),
            employment_type=data.get('employment_type', 'full-time'),
            posted_by_id=data['posted_by_id'],
            status=data.get('status', 'active')
        )
        
        db.session.add(vacancy)
        db.session.commit()
        
        return jsonify({'message': 'Vacancy created successfully', 'vacancy': vacancy.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/<vacancy_id>', methods=['GET'])
def get_vacancy(vacancy_id):
    """Get a specific vacancy by ID"""
    try:
        vacancy = Vacancy.query.get_or_404(vacancy_id)
        return jsonify(vacancy.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/<vacancy_id>', methods=['PUT'])
def update_vacancy(vacancy_id):
    """Update a specific vacancy"""
    try:
        vacancy = Vacancy.query.get_or_404(vacancy_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            vacancy.title = data['title']
        if 'description' in data:
            vacancy.description = data['description']
        if 'requirements' in data:
            vacancy.requirements = data['requirements']
        if 'location' in data:
            vacancy.location = data['location']
        if 'school' in data:
            vacancy.school = data['school']
        if 'level' in data:
            vacancy.level = data['level']
        if 'department' in data:
            vacancy.department = data['department']
        if 'salary_range' in data:
            vacancy.salary_range = data['salary_range']
        if 'employment_type' in data:
            vacancy.employment_type = data['employment_type']
        if 'status' in data:
            vacancy.status = data['status']
        
        db.session.commit()
        
        return jsonify({'message': 'Vacancy updated successfully', 'vacancy': vacancy.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/<vacancy_id>', methods=['DELETE'])
def delete_vacancy(vacancy_id):
    """Delete a specific vacancy"""
    try:
        vacancy = Vacancy.query.get_or_404(vacancy_id)
        db.session.delete(vacancy)
        db.session.commit()
        
        return jsonify({'message': 'Vacancy deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/locations', methods=['GET'])
def get_locations():
    """Get all unique locations from vacancies"""
    try:
        locations = db.session.query(Vacancy.location).distinct().filter(
            Vacancy.location.isnot(None), 
            Vacancy.location != '',
            Vacancy.status == 'active'
        ).all()
        
        # Extract location strings from tuples and filter out None/empty
        location_list = [loc[0] for loc in locations if loc[0]]
        
        return jsonify({
            'locations': sorted(location_list),
            'count': len(location_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/schools', methods=['GET'])
def get_schools():
    """Get all unique schools from vacancies"""
    try:
        schools = db.session.query(Vacancy.school).distinct().filter(
            Vacancy.school.isnot(None), 
            Vacancy.school != '',
            Vacancy.status == 'active'
        ).all()
        
        # Extract school strings from tuples and filter out None/empty
        school_list = [school[0] for school in schools if school[0]]
        
        return jsonify({
            'schools': sorted(school_list),
            'count': len(school_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vacancy_bp.route('/levels', methods=['GET'])
def get_levels():
    """Get all unique levels from vacancies"""
    try:
        levels = db.session.query(Vacancy.level).distinct().filter(
            Vacancy.level.isnot(None), 
            Vacancy.level != '',
            Vacancy.status == 'active'
        ).all()
        
        # Extract level strings from tuples and filter out None/empty
        level_list = [level[0] for level in levels if level[0]]
        
        return jsonify({
            'levels': sorted(level_list),
            'count': len(level_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500