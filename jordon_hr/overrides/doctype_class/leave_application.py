
import frappe
from jordon_hr.events.attendance import HandleAdditionalSalaryOnLeave
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication

class JordonLeaveApplication(LeaveApplication) :
    def create_or_update_attendance(self, attendance_name, date):
        super().create_or_update_attendance(attendance_name, date)
        if attendance_name:
            AttendanceDoc = frappe.get_doc("Attendance" , attendance_name)
            HandleAdditionalSalaryOnLeave(AttendanceDoc)