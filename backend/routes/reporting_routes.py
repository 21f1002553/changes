from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from sqlalchemy import func, and_, or_
from app import db
from models import (
    Report, EODReport, ExpenseReport, User, Application, Interview
)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get overall dashboard statistics"""
    try:
        # Get date range (default: last 30 days)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        # EOD Reports Stats
        total_eod = db.session.query(func.count(EODReport.id)).filter(
            and_(
                EODReport.date >= start_date,
                EODReport.date <= end_date
            )
        ).scalar()
        
        # Application Stats (replacing Leave Requests)
        total_applications = db.session.query(func.count(Application.id)).filter(
            and_(
                Application.applied_at >= datetime.combine(start_date, datetime.min.time()),
                Application.applied_at <= datetime.combine(end_date, datetime.max.time())
            )
        ).scalar()
        
        pending_applications = db.session.query(func.count(Application.id)).filter(
            Application.status == 'applied'
        ).scalar()
        
        # Expense Reports Stats
        total_expenses_sum = db.session.query(func.sum(ExpenseReport.total)).filter(
            ExpenseReport.report_id.in_(
                db.session.query(Report.id).filter(
                    and_(
                        Report.start_date >= start_date,
                        Report.end_date <= end_date,
                        Report.report_type == 'expense'
                    )
                )
            )
        ).scalar() or 0
        
        pending_expenses = db.session.query(func.count(ExpenseReport.id)).filter(
            ExpenseReport.status == 'pending'
        ).scalar()
        
        # Active Employees (Users with 'active' status)
        active_employees = db.session.query(func.count(User.id)).filter(
            User.status == 'active'
        ).scalar()
        
        return jsonify({
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "statistics": {
                "eod_reports": {
                    "total": total_eod or 0
                },
                "applications": {
                    "total": total_applications or 0,
                    "pending": pending_applications or 0
                },
                "expenses": {
                    "total_amount": float(total_expenses_sum),
                    "pending_count": pending_expenses or 0
                },
                "employees": {
                    "active": active_employees or 0
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route('/eod-summary', methods=['GET'])
def get_eod_summary():
    """Get EOD reports summary"""
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        employee_id = request.args.get('employee_id')
        role = request.args.get('role')
        
        # Default date range: last 7 days
        if not end_date_str:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
        if not start_date_str:
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        
        # Build query
        query = db.session.query(EODReport).filter(
            and_(
                EODReport.date >= start_date,
                EODReport.date <= end_date
            )
        )
        
        if employee_id:
            query = query.filter(EODReport.employee_id == employee_id)
        
        if role:
            query = query.filter(EODReport.role == role)
        
        reports = query.order_by(EODReport.date.desc()).all()
        
        # Group by date
        summary_by_date = {}
        for report in reports:
            date_key = report.date.isoformat()
            if date_key not in summary_by_date:
                summary_by_date[date_key] = {
                    "date": date_key,
                    "total_reports": 0,
                    "reports": []
                }
            summary_by_date[date_key]["total_reports"] += 1
            summary_by_date[date_key]["reports"].append(report.to_dict())
        
        return jsonify({
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_reports": len(reports),
            "summary": list(summary_by_date.values())
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route('/application-analytics', methods=['GET'])
def get_application_analytics():
    """Get application analytics (replaces leave analytics)"""
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Default date range: current year
        if not end_date_str:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
        if not start_date_str:
            start_date = datetime(end_date.year, 1, 1).date()
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        
        # Convert dates to datetime for comparison
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get all applications in range
        applications = db.session.query(Application).filter(
            and_(
                Application.applied_at >= start_datetime,
                Application.applied_at <= end_datetime
            )
        ).all()
        
        # Analytics by status
        by_status = {}
        
        # Analytics by job
        by_job = {}
        
        total_applications = len(applications)
        
        for application in applications:
            # Status count
            status = application.status or 'applied'
            by_status[status] = by_status.get(status, 0) + 1
            
            # Job count
            if application.job:
                job_title = application.job.title
                by_job[job_title] = by_job.get(job_title, 0) + 1
        
        return jsonify({
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_applications": total_applications,
            "by_status": by_status,
            "by_job": by_job
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route('/expense-summary', methods=['GET'])
def get_expense_summary():
    """Get expense summary"""
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Default date range: current month
        if not end_date_str:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
        if not start_date_str:
            start_date = datetime(end_date.year, end_date.month, 1).date()
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        
        # Get expense reports through Report table
        expense_report_ids = db.session.query(Report.id).filter(
            and_(
                Report.report_type == 'expense',
                Report.start_date >= start_date,
                Report.end_date <= end_date
            )
        ).all()
        
        expense_report_ids = [r[0] for r in expense_report_ids]
        
        # Get expense reports
        expenses = db.session.query(ExpenseReport).filter(
            ExpenseReport.report_id.in_(expense_report_ids)
        ).all() if expense_report_ids else []
        
        # Calculate summaries
        total_amount = 0
        by_status = {
            "pending": {"count": 0, "amount": 0},
            "approved": {"count": 0, "amount": 0},
            "rejected": {"count": 0, "amount": 0}
        }
        
        for expense in expenses:
            amount = float(expense.total) if expense.total else 0
            total_amount += amount
            
            # By status
            status = expense.status or 'pending'
            if status in by_status:
                by_status[status]["count"] += 1
                by_status[status]["amount"] += amount
        
        return jsonify({
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_expenses": len(expenses),
            "total_amount": total_amount,
            "by_status": by_status
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================
# CUSTOM REPORT GENERATION
# ============================================

@reports_bp.route('/generate', methods=['POST'])
def generate_custom_report():
    """Generate custom reports based on type and filters"""
    try:
        data = request.get_json()
        
        # Validate required fields
        report_type = data.get('report_type')
        date_range = data.get('date_range', {})
        filters = data.get('filters', {})
        format_type = data.get('format', 'json')
        
        if not report_type:
            return jsonify({"error": "report_type is required"}), 400
        
        if report_type not in ['eod', 'application', 'expense', 'interview']:
            return jsonify({"error": "Invalid report_type"}), 400
        
        # Parse date range
        try:
            start_date = datetime.strptime(date_range.get('start'), "%Y-%m-%d").date()
            end_date = datetime.strptime(date_range.get('end'), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid date format (expected YYYY-MM-DD)"}), 400
        
        # CHANGED: Use 'user_id' instead of 'generated_by'
        user_id = data.get('user_id', 'system')  # Changed variable name
        
        # Generate report based on type
        report_data = None
        
        if report_type == 'eod':
            report_data = generate_eod_report(start_date, end_date, filters)
        elif report_type == 'application':
            report_data = generate_application_report(start_date, end_date, filters)
        elif report_type == 'expense':
            report_data = generate_expense_report(start_date, end_date, filters)
        elif report_type == 'interview':
            report_data = generate_interview_report(start_date, end_date, filters)
        
        # Save report record
        report = Report(
            report_type=report_type,
            user_id=user_id,  # CHANGED: Use user_id instead of generated_by
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            format=format_type,
            data=report_data
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Return based on format
        if format_type == 'json':
            return jsonify({
                "report_id": report.id,
                "report_type": report_type,
                "generated_at": report.generated_at.isoformat(),
                "data": report_data
            }), 200
        elif format_type == 'pdf':
            # TODO: Implement PDF generation
            return jsonify({
                "message": "PDF generation not yet implemented",
                "report_id": report.id
            }), 501
        elif format_type == 'excel':
            # TODO: Implement Excel generation
            return jsonify({
                "message": "Excel generation not yet implemented",
                "report_id": report.id
            }), 501
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_eod_report(start_date, end_date, filters):
    """Generate EOD report data"""
    query = db.session.query(EODReport).filter(
        and_(
            EODReport.date >= start_date,
            EODReport.date <= end_date
        )
    )
    
    # Apply filters
    if filters.get('role'):
        query = query.filter(EODReport.role == filters['role'])
    
    if filters.get('employee_ids'):
        query = query.filter(EODReport.employee_id.in_(filters['employee_ids']))
    
    reports = query.order_by(EODReport.date.desc()).all()
    
    return {
        "total_reports": len(reports),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "reports": [report.to_dict() for report in reports]
    }


def generate_application_report(start_date, end_date, filters):
    """Generate application report data"""
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    query = db.session.query(Application).filter(
        and_(
            Application.applied_at >= start_datetime,
            Application.applied_at <= end_datetime
        )
    )
    
    # Apply filters
    if filters.get('candidate_ids'):
        query = query.filter(Application.candidate_id.in_(filters['candidate_ids']))
    
    if filters.get('job_ids'):
        query = query.filter(Application.job_id.in_(filters['job_ids']))
    
    if filters.get('status'):
        query = query.filter(Application.status == filters['status'])
    
    applications = query.order_by(Application.applied_at.desc()).all()
    
    return {
        "total_applications": len(applications),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "applications": [app.to_dict() for app in applications]
    }


def generate_expense_report(start_date, end_date, filters):
    """Generate expense report data"""
    # Get expense reports through Report table
    report_query = db.session.query(Report.id).filter(
        and_(
            Report.report_type == 'expense',
            Report.start_date >= start_date,
            Report.end_date <= end_date
        )
    )
    
    # Apply user filter if provided
    if filters.get('employee_ids'):
        report_query = report_query.filter(
            Report.generated_by.in_(filters['employee_ids'])
        )
    
    expense_report_ids = [r[0] for r in report_query.all()]
    
    expenses = db.session.query(ExpenseReport).filter(
        ExpenseReport.report_id.in_(expense_report_ids)
    ).all() if expense_report_ids else []
    
    total_amount = sum(float(exp.total) if exp.total else 0 for exp in expenses)
    
    return {
        "total_expenses": len(expenses),
        "total_amount": total_amount,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "expenses": [expense.to_dict() for expense in expenses]
    }


def generate_interview_report(start_date, end_date, filters):
    """Generate interview report data"""
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    query = db.session.query(Interview).filter(
        and_(
            Interview.scheduled_at >= start_datetime,
            Interview.scheduled_at <= end_datetime
        )
    )
    
    # Apply filters
    if filters.get('interviewer_ids'):
        query = query.filter(Interview.interviewer_id.in_(filters['interviewer_ids']))
    
    if filters.get('status'):
        query = query.filter(Interview.status == filters['status'])
    
    interviews = query.order_by(Interview.scheduled_at.desc()).all()
    
    return {
        "total_interviews": len(interviews),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "interviews": [interview.to_dict() for interview in interviews]
    }