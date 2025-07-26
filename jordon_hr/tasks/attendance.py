import frappe
from frappe import _
from frappe.utils import nowdate


def GetExpenseClaimsForToday() :
    return frappe.db.sql(""" 
        SELECT 
            ec.employee , ec.company , ec.name 
        FROM `tabExpense Claim` ec
        WHERE ec.docstatus = 1
            AND ec.auto_attendance = 1
            AND CURDATE() BETWEEN ec.from_date AND ec.to_date
            AND NOT EXISTS (
                SELECT 1
                FROM `tabAttendance` a
                WHERE a.expense_claim = ec.name
                    AND a.docstatus = 1
                    AND a.attendance_date = CURDATE() 
                    AND a.employee = ec.employee
            )
                         
    """ , as_dict=True)


def CreateAttendanceFromExpenseClaim():
    ListOfExpenseClaim = GetExpenseClaimsForToday()

    for ExpenseClaim in ListOfExpenseClaim :
        try:
            NewAttendance = frappe.new_doc("Attendance")
            NewAttendance.employee = ExpenseClaim.get("employee")
            NewAttendance.company  = ExpenseClaim.get("company")
            NewAttendance.attendance_date  = nowdate()
            NewAttendance.status  = "Work From Home"
            NewAttendance.expense_claim = ExpenseClaim.get("name")
            NewAttendance.flags.ignore_mandatory = True
            NewAttendance.save()
            NewAttendance.submit()

        except Exception as e:
            frappe.throw(_("Can't Create Attendance in Date {0} => {1}").format(nowdate() , e))
            
    