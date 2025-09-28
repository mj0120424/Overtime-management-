import frappe
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip 


class JordonSalarySlip(SalarySlip):
    
    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        self.GetTotalWorkingHours()
        super().get_emp_and_working_day_details()

            
    def GetTotalWorkingHours(self) :
        if self.employee and self.start_date and self.end_date:
            DailyEmployee = frappe.db.get_value("Employee" , self.employee ,"daily_employee")
            if not DailyEmployee : return 
            self.total_working_hours = GetWorkingHoursFromAttendance(self.employee , self.start_date , self.end_date)
        
        
def GetWorkingHoursFromAttendance(Employee , StartDate , EndDate) :
    SqlQuery = """ 
        SELECT 
            SUM(ROUND(TIMESTAMPDIFF(SECOND, in_time,out_time) / 3600, 2)) AS working_hours
        FROM `tabAttendance` 
        WHERE docstatus = 1
            AND employee = %(Employee)s
            AND attendance_date BETWEEN %(StartDate)s AND %(EndDate)s
            AND status NOT IN ( 'On Leave' , 'Absent' )
    """
    TotalWorkingHourList =  frappe.db.sql(SqlQuery , {"Employee" : Employee , "StartDate":StartDate , "EndDate":EndDate}, as_dict=True)
    return 0 if not TotalWorkingHourList else TotalWorkingHourList[0].get("working_hours")