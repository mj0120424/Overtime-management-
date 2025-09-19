import frappe
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip , process_loan_interest_accruals

class JordonSalarySlip(SalarySlip):
    
    @frappe.whitelist()
    def get_emp_and_working_day_details(self):
        """First time, load all the components from salary structure"""
        if self.employee:
            self.set("earnings", [])
            self.set("deductions", [])
            if hasattr(self, "loans"):
                self.set("loans", [])

            if self.payroll_frequency:
                self.get_date_details()

            self.validate_dates()

            # getin leave details
            self.get_working_days_details()
            struct = self.check_sal_struct()

            if struct:
                self.GetTotalWorkingHours() 
                self.set_salary_structure_doc()
                self.salary_slip_based_on_timesheet = (
                    self._salary_structure_doc.salary_slip_based_on_timesheet or 0
                )
                self.set_time_sheet()
                self.pull_sal_struct()

            process_loan_interest_accruals(self)
            
            
    def GetTotalWorkingHours(self) :
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