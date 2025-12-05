from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from app import db
from models import File, Resume, User
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
import base64
import mimetypes
import docx2txt
from datetime import datetime
file_bp = Blueprint('files', __name__)

# Configuration
UPLOAD_FOLDER = './uploads/files'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size doesn't exceed limit"""
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    return file_length <= MAX_FILE_SIZE

def get_file_size(file):
    """Get file size in bytes"""
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    return file_length


# 1. FILE UPLOAD
@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload a new file
    ---
    tags:
      - Files
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: File to upload (PDF or DOCX only, max 10MB)
      - name: category
        in: formData
        type: string
        required: false
        description: File category (e.g., resume, document, contract)
      - name: description
        in: formData
        type: string
        required: false
        description: File description
      - name: is_public
        in: formData
        type: boolean
        required: false
        description: Make file publicly accessible
    responses:
      201:
        description: File uploaded successfully
      400:
        description: Invalid file or missing required fields
      413:
        description: File size exceeds limit
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX files are allowed'}), 400
        
        # Validate file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024 * 1024)}MB limit'}), 413
        
        # Get form data
        category = request.form.get('category', 'document')
        description = request.form.get('description', '')
        is_public = request.form.get('is_public', 'false').lower() == 'true'
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get MIME type
        mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        
        # Create database record
        new_file = File(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            mime_type=mime_type,
            uploaded_by_id=current_user_id,
            category=category,
            description=description,
            is_public=is_public
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'data': new_file.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        # Clean up file if database insert fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500


# 2. GET FILE DOWNLOAD
@file_bp.route('/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """
    Download a file
    ---
    tags:
      - Files
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: ID of the file to download
    responses:
      200:
        description: File downloaded successfully
      403:
        description: Access denied
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Get file from database
        file_record = File.query.get_or_404(file_id)
        
        # Check access permissions
        # Users can access their own files or public files
        # Admins can access all files
        is_admin = current_user.role and current_user.role.name == 'admin'
        is_hr = current_user.role and current_user.role.name == 'hr'
        is_owner = file_record.uploaded_by_id == current_user_id
        is_public = file_record.is_public
        
        if not (is_admin or is_owner or is_public or is_hr):
            return jsonify({'error': 'Access denied. You do not have permission to download this file'}), 403
        
        # Check if file exists on disk
        if not os.path.exists(file_record.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        # Send file
        return send_file(
            file_record.file_path,
            as_attachment=True,
            download_name=file_record.original_filename,
            mimetype=file_record.mime_type
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 3. DELETE FILE
@file_bp.route('/delete/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """
    Delete a file
    ---
    tags:
      - Files
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: ID of the file to delete
    responses:
      200:
        description: File deleted successfully
      403:
        description: Access denied
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Get file from database
        file_record = File.query.get_or_404(file_id)
        
        # Check permissions - only owner or admin can delete
        is_admin = current_user.role and current_user.role.name == 'admin'
        is_owner = file_record.uploaded_by_id == current_user_id
        
        if not (is_admin or is_owner):
            return jsonify({'error': 'Access denied. You do not have permission to delete this file'}), 403
        
        # Delete file from disk
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        
        # Delete from database
        db.session.delete(file_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 4. PREVIEW FILE
@file_bp.route('/<file_id>/preview', methods=['GET'])
@jwt_required()
def preview_file(file_id):
    """
    Preview file content
    ---
    tags:
      - Files
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: ID of the file to preview
    responses:
      200:
        description: File preview generated successfully
      403:
        description: Access denied
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Get file from database
        file_record = File.query.get_or_404(file_id)
        
        # Check access permissions
        is_Admin = current_user.role and current_user.role.name == 'admin'
        is_hr = current_user.role and current_user.role.name == 'hr'
        is_owner = file_record.uploaded_by_id == current_user_id
        is_public = file_record.is_public
        
        if not (is_hr or is_owner or is_public):
            return jsonify({'error': 'Access denied. You do not have permission to preview this file'}), 403
        
        # Check if file exists on disk
        if not os.path.exists(file_record.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        preview_data = {
            'file_id': file_record.id,
            'filename': file_record.original_filename,
            'file_type': file_record.file_type,
            'file_size': file_record.file_size,
            'category': file_record.category,
            'description': file_record.description,
            'uploaded_at': file_record.uploaded_at.isoformat() if file_record.uploaded_at else None,
            'uploaded_by': file_record.uploaded_by.name if file_record.uploaded_by else None
        }
        
        # Generate preview based on file type
        if file_record.file_type == 'docx':
            try:
                # Extract text from DOCX
                text_content = docx2txt.process(file_record.file_path)
                preview_data['preview_type'] = 'text'
                preview_data['content'] = text_content[:5000]  # Limit to first 5000 characters
                preview_data['full_length'] = len(text_content)
            except Exception as e:
                preview_data['preview_type'] = 'metadata'
                preview_data['error'] = f'Could not extract text: {str(e)}'
        
        elif file_record.file_type == 'pdf':
            # For PDF, return metadata only (you can enhance this with PyPDF2 if needed)
            preview_data['preview_type'] = 'metadata'
            preview_data['message'] = 'PDF preview not available. Please download to view.'
        
        else:
            # For other files, just return metadata
            preview_data['preview_type'] = 'metadata'
        
        return jsonify(preview_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 5. GET ALL FILES (with filtering)
@file_bp.route('/', methods=['GET'])
@jwt_required()
def get_files():
    """
    Get all accessible files with optional filtering
    ---
    tags:
      - Files
    parameters:
      - name: category
        in: query
        type: string
        required: false
        description: Filter by category
      - name: file_type
        in: query
        type: string
        required: false
        description: Filter by file type (pdf, docx)
      - name: page
        in: query
        type: integer
        required: false
        description: Page number (default 1)
      - name: limit
        in: query
        type: integer
        required: false
        description: Items per page (default 10)
    responses:
      200:
        description: Files retrieved successfully
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Get query parameters
        category = request.args.get('category')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Build query based on user role
        is_admin = current_user.role and current_user.role.name == 'admin'
        
        if is_admin:
            # Admin can see all files
            query = File.query
        else:
            # Users can see their own files and public files
            query = File.query.filter(
                db.or_(
                    File.uploaded_by_id == current_user_id,
                    File.is_public == True
                )
            )
        
        # Apply filters
        if category:
            query = query.filter(File.category == category)
        
        # Get total count
        total_count = query.count()
        
        # Pagination
        files = query.order_by(File.uploaded_at.desc()).offset(
            (page - 1) * limit
        ).limit(limit).all()
        
        return jsonify({
            'data': [file.to_dict() for file in files],
            'pagination': {
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_count': total_count,
                'per_page': limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

### get resume file 
@file_bp.route('/resume', methods=['GET'])
@jwt_required()
def get_resume():
    try:
        current_user_id = get_jwt_identity()
        # Return all resumes for the current user (previously returned only the first)
        resumes = Resume.query.filter_by(owner_id=current_user_id).order_by(Resume.uploaded_at.desc()).all()
        return jsonify([r.to_dict() for r in resumes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 6. GET SINGLE FILE INFO
@file_bp.route('/<file_id>', methods=['GET'])
@jwt_required()
def get_file_info(file_id):
    """
    Get information about a specific file
    ---
    tags:
      - Files
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: ID of the file
    responses:
      200:
        description: File information retrieved successfully
      403:
        description: Access denied
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        # Get file from database
        file_record = File.query.get_or_404(file_id)
        
        # Check access permissions
        is_admin = current_user.role and current_user.role.name == 'hr'
        is_owner = file_record.uploaded_by_id == current_user_id
        is_public = file_record.is_public
        
        if not (is_admin or is_owner or is_public):
            return jsonify({'error': 'Access denied. You do not have permission to view this file'}), 403
        
        return jsonify(file_record.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 7. UPDATE FILE METADATA
@file_bp.route('/<file_id>', methods=['PUT'])
@jwt_required()
def update_file_metadata(file_id):
    """
    Update file metadata (category, description, is_public)
    ---
    tags:
      - Files
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: ID of the file
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            category:
              type: string
            description:
              type: string
            is_public:
              type: boolean
    responses:
      200:
        description: File metadata updated successfully
      403:
        description: Access denied
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        # Get file from database
        file_record = File.query.get_or_404(file_id)
        
        # Check permissions - only owner or admin can update
        is_admin = current_user.role and current_user.role.name == 'admin'
        is_owner = file_record.uploaded_by_id == current_user_id
        
        if not (is_admin or is_owner):
            return jsonify({'error': 'Access denied. You do not have permission to update this file'}), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'category' in data:
            file_record.category = data['category']
        
        if 'description' in data:
            file_record.description = data['description']
        
        if 'is_public' in data:
            file_record.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File metadata updated successfully',
            'data': file_record.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 8. GET FILE STATISTICS
@file_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_file_statistics():
    """
    Get file upload statistics
    ---
    tags:
      - Files
    responses:
      200:
        description: Statistics retrieved successfully
      500:
        description: Server error
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get_or_404(current_user_id)
        
        is_admin = current_user.role and current_user.role.name == 'admin'
        
        if is_admin:
            # Admin sees all files stats
            total_files = File.query.count()
            total_size = db.session.query(db.func.sum(File.file_size)).scalar() or 0
            files_by_type = db.session.query(
                File.file_type, 
                db.func.count(File.id),
                db.func.sum(File.file_size)
            ).group_by(File.file_type).all()
            files_by_category = db.session.query(
                File.category,
                db.func.count(File.id)
            ).group_by(File.category).all()
        else:
            # User sees only their files stats
            total_files = File.query.filter_by(uploaded_by_id=current_user_id).count()
            total_size = db.session.query(db.func.sum(File.file_size)).filter(
                File.uploaded_by_id == current_user_id
            ).scalar() or 0
            files_by_type = db.session.query(
                File.file_type,
                db.func.count(File.id),
                db.func.sum(File.file_size)
            ).filter(File.uploaded_by_id == current_user_id).group_by(File.file_type).all()
            files_by_category = db.session.query(
                File.category,
                db.func.count(File.id)
            ).filter(File.uploaded_by_id == current_user_id).group_by(File.category).all()
        
        return jsonify({
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files_by_type': {
                file_type: {
                    'count': count,
                    'total_size_mb': round((size or 0) / (1024 * 1024), 2)
                }
                for file_type, count, size in files_by_type
            },
            'files_by_category': {
                category: count
                for category, count in files_by_category
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@file_bp.route('/upload/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    """
    Upload resume file and create Resume record in one step
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type - only PDF and DOCX for resumes
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX files are allowed'}), 400
        
        # Validate file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024 * 1024)}MB limit'}), 413
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Get MIME type
        mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        
        # Create File record
        new_file = File(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            mime_type=mime_type,
            uploaded_by_id=current_user_id,
            category='resume',
            description='User resume',
            is_public=False
        )
        
        db.session.add(new_file)
        db.session.flush()
        
        # Delete existing resume if any


        # if existing_resume:
        #     # --- FIX STARTS HERE ---
        #     # 1. Clean up the OLD underlying file (Physical file + File DB Record)
        #     # We don't delete the Resume record itself, just the old file associated with it
        #     if existing_resume.file_id:
        #         old_file = File.query.get(existing_resume.file_id)
        #         if old_file:
        #             # Remove from disk
        #             if os.path.exists(old_file.file_path):
        #                 try:
        #                     os.remove(old_file.file_path)
        #                 except OSError:
        #                     pass # File might be already gone
        #             # Remove file record from DB
        #             db.session.delete(old_file)
            
        #     # 2. Update the EXISTING resume record with new file details
        #     # This preserves the Resume ID, keeping the 'Application' foreign key valid
        #     existing_resume.file_url = file_path
        #     existing_resume.uploaded_at = datetime.utcnow()
        #     existing_resume.filename = unique_filename
        #     existing_resume.file_id = new_file.id
        #     existing_resume.file_size = file_size
        #     # Reset parsed data on new upload if desired
        #     existing_resume.parsed_data = None 
            
        #     resume_record = existing_resume
        #     # --- FIX ENDS HERE ---
        # else:
        #     # Create NEW Resume record if none exists
        resume_record = Resume(
            owner_id=current_user_id,
            file_url=file_path,
            uploaded_at=datetime.utcnow(),
            parsed_data=None,
            filename=unique_filename,
            file_id=new_file.id,
            file_size=file_size
        )
        db.session.add(resume_record)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully',
            'file': new_file.to_dict(),
            'resume': resume_record.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        # Clean up file if database insert fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500


# DOWNLOAD FILE
@file_bp.route('/preview-offer-letter', methods=['GET'])
@jwt_required()
def download_offer_letter():
    """
    Download a file by file_path
    ---
    tags:
      - Files
    parameters:
      - name: file_path
        in: query
        type: string
        required: true
        description: Path to the file to download
    responses:
      200:
        description: File downloaded successfully
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        file_path = request.args.get('file_path')
        
        if not file_path:
            return jsonify({'error': 'file_path parameter is required'}), 400
        
        # Security: Ensure the file path is within allowed directories
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get mime type
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Send file
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500