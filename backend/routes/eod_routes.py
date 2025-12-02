from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from models import Role, EODReport  

eod_bp = Blueprint('eod', __name__)

@eod_bp.route('/submit', methods=['POST'])
def submit_eod():
  try:
    data = request.get_json()

    employee_id = data.get("employee_id")
    report_id = data.get("report_id")
    role = data.get("role")
    date_str = data.get("date")
    time_str = data.get("time")
    
    tasks = data.get('data', {})
    
    if not employee_id or not report_id or not role or not date_str or not time_str or not tasks:
        return jsonify({"error": "Missing required fields"}), 400

    if role not in ["teacher", "admin"]:
        return jsonify({"error": "Invalid role"}), 400

    
    # Convert date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format (expected YYYY-MM-DD)"}), 400

    # Convert time
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid time format (expected HH:MM)"}), 400

    new_report = EODReport(
        employee_id = employee_id,
        report_id = report_id,
        role = role,
        date = date_obj,
        time = time_obj,
        tasks = tasks
    )

    db.session.add(new_report)
    db.session.commit()

    return jsonify({
        "message": "EOD report submitted successfully",
        "report": new_report.to_dict()
    }), 201
      
  except Exception as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 500

@eod_bp.route('/submissions', methods=['GET'])
def get_eod_submissions():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee = request.args.get('employee')
        role = request.args.get('role')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        query = EODReport.query

        # Date range filter
        if start_date:
            query = query.filter(EODReport.date >= start_date)
        if end_date:
            query = query.filter(EODReport.date <= end_date)

        # employee id filter (frontend will map name->id)
        if employee:
            query = query.filter(EODReport.employee_id == employee)

        # role filter
        if role:
            query = query.filter(EODReport.role == role.lower())

        # Pagination
        total_count = query.count()
        submissions = query.order_by(EODReport.date.desc()).paginate(page=page, per_page=limit, error_out=False)

        data = []
        for e in submissions.items:
            data.append({
                "id": e.id,
                "employee_id": e.employee_id,
                "role": e.role,
                "date": e.date.isoformat(),
                "time": str(e.time),
                "summary": e.ai_summary or "",   # Placeholder, if you generate later
                "detailed_data": e.tasks
            })

        return jsonify({
            "data": data,
            "pagination": {
                "current_page": page,
                "total_pages": submissions.pages,
                "total_count": total_count
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
      

@eod_bp.route('/submissions/<id>', methods=['GET'])
def get_eod_by_id(id):
    try:
        report = EODReport.query.get(id)
        if not report:
            return jsonify({"error": "EOD Report not found"}), 404

        return jsonify(report.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@eod_bp.route('/submissions/<id>', methods=['PUT'])
def update_eod(id):
    try:
        report = EODReport.query.get(id)
        if not report:
            return jsonify({"error": "EOD Report not found"}), 404

        data = request.get_json()

        # Update role
        report.role = data.get("role", report.role)

        # Update date (if provided)
        if "date" in data:
            report.date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        # Update time (if provided)
        if "time" in data:
            time_str = data["time"]
            try:
                report.time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                report.time = datetime.strptime(time_str, "%H:%M:%S").time()

        # Update tasks
        if "data" in data:
            report.tasks = data["data"]

        db.session.commit()

        return jsonify({"message": "Report updated", "report": report.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
      
@eod_bp.route('/submissions/<id>', methods=['DELETE'])
def delete_eod(id):
    try:
        report = EODReport.query.get(id)
        if not report:
            return jsonify({"error": "EOD Report not found"}), 404

        db.session.delete(report)
        db.session.commit()

        return jsonify({"message": "EOD Report deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@eod_bp.route('/templates/<role>', methods=['GET'])
def get_eod_template(role):
    role = role.lower()

    templates = {
        "teacher": {
            "classes_taught": "",
            "student_progress": ""
        },
        "admin": {
            "reports_completed": "",
            "action_items": ""
        }
    }

    if role not in templates:
        return jsonify({"error": "Invalid role"}), 400

    return jsonify({"role": role, "template": templates[role]}), 200

