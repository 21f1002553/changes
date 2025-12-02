from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from models import User, LeaveBalance, SalaryRecord

salary_bp = Blueprint('salary', __name__)

# ---- Salary Calculation ----
@salary_bp.route('/calculate/<employee_id>', methods=['GET'])
def calculate_salary(employee_id):
    try:
        employee = User.query.get_or_404(employee_id)
        balance = LeaveBalance.query.filter_by(employee_id=employee.id).first()

        if not balance:
            balance = LeaveBalance(employee_id=employee.id)
            db.session.add(balance)
            db.session.commit()

        # Example salary logic:
        BASIC_SALARY = 30000  # Default base salary (you can later fetch from DB)
        LOP_DEDUCTION_PER_DAY = 1000

        lop_days = balance.lop_leave
        deduction = lop_days * LOP_DEDUCTION_PER_DAY
        net_salary = BASIC_SALARY - deduction

        # Record the calculation
        today = datetime.now()
        salary_record = SalaryRecord(
            employee_id=employee.id,
            month=today.month,
            year=today.year,
            basic_salary=BASIC_SALARY,
            deduction=deduction,
            net_salary=net_salary
        )
        db.session.add(salary_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Salary calculated successfully',
            'data': {
                'employee': employee.name,
                'month': today.month,
                'year': today.year,
                'basic_salary': BASIC_SALARY,
                'lop_days': lop_days,
                'deduction': deduction,
                'net_salary': net_salary
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salary_bp.route('/deduction', methods=['POST'])
def apply_deduction():
    try:
        data = request.get_json()
        employee_id = data['employee_id']
        amount = float(data['amount'])
        reason = data.get('reason', '')

        employee = User.query.get_or_404(employee_id)

        # Find the latest salary record for the employee
        latest_salary = (
            SalaryRecord.query.filter_by(employee_id=employee.id)
            .order_by(SalaryRecord.generated_at.desc())
            .first()
        )

        if not latest_salary:
            return jsonify({'error': 'No salary record found. Calculate salary first.'}), 400

        # Apply deduction
        latest_salary.deduction += amount
        latest_salary.net_salary -= amount
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Deduction applied successfully',
            'data': {
                'employee': employee.name,
                'deduction_amount': amount,
                'reason': reason,
                'updated_net_salary': latest_salary.net_salary
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@salary_bp.route('/payroll/<int:month>/<int:year>', methods=['GET'])
def get_payroll_summary(month, year):
    try:
        # Get all salary records for that month & year
        salaries = SalaryRecord.query.filter_by(month=month, year=year).all()

        if not salaries:
            return jsonify({'message': 'No payroll records found for this month/year'}), 404

        payroll_data = []
        for record in salaries:
            payroll_data.append({
                'employee': record.employee.name if record.employee else None,
                'month': record.month,
                'year': record.year,
                'basic_salary': record.basic_salary,
                'deduction': record.deduction,
                'net_salary': record.net_salary
            })

        return jsonify({
            'success': True,
            'data': payroll_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
