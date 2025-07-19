import frappe
from frappe import _
from frappe.utils import time_diff
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee as GetHolidayListForEmployee
from jordon_hr.utilites import (
    GetEmployeeSalary,
    GetJordonHrSettingByCompany ,
    CreateAdditionalSalary ,
    GetShiftDetailsForEmployee,
)


def AttendanceOnSubmit(Doc , Events) :
    try :
        if Doc.shift and Doc.in_time and Doc.out_time :  
            ShiftDetails = GetShiftDetailsForEmployee(Doc.shift)
            if frappe.db.get_value("Employee" , Doc.employee , "allow_overtime") and ShiftDetails.get("calculate_overtime_after"):  
                CalculateOverTime(Doc , ShiftDetails)
                
            if Doc.late_entry and ShiftDetails.get("enable_late_entry_marking") and ShiftDetails.get("late_entry_grace_period") and ShiftDetails.get("late_entry_salary_component") :
                CalculateLateEntry(Doc , ShiftDetails)
                
    except frappe.ValidationError as e :
        Doc.add_comment("Comment" , str(e))
        
    except Exception as e :
        frappe.log_error("Attendance Calculation OverTime Or Late Entry")
        
        


def TimeDiffInMintues(CheckOutDateTime , ShiftEndTime):
    ShiftEndDateTime =  "{0} {1}".format( CheckOutDateTime.date() , ShiftEndTime)
    return time_diff(ShiftEndDateTime, CheckOutDateTime).total_seconds() / 60


def CalculateOverTime(Doc , ShiftDetails:dict) :
    
    if CalculateOvertimeAfter := ShiftDetails.get("calculate_overtime_after") :
        ShiftEndTime = ShiftDetails.get("end_time")
        OverTime = abs(TimeDiffInMintues(Doc.out_time , ShiftEndTime))
        if OverTime > CalculateOvertimeAfter :
            IsHoliday = CheckIfHoliday(Doc.employee , Doc.attendance_date)
            CreateOverTimeRequest(OverTime , Doc , ShiftEndTime , IsHoliday)
            
    
def CheckIfHoliday(Employee , AttendanceDate) :    
    HolidayList = GetHolidayListForEmployee(Employee, False)
    return is_holiday(HolidayList , AttendanceDate) if HolidayList else False
 
    
def CreateOverTimeRequest(OverTime , Doc:dict , ShiftEndTime , IsHoliday=False) :
    
    OverTimeRequest = frappe.new_doc("Overtime request")
    OverTimeRequest.attendance = Doc.get("name")
    OverTimeRequest.employee = Doc.get("employee")
    OverTimeRequest.request_status = "Draft"
    OverTimeRequest.day = Doc.get("attendance_date")
    OverTimeRequest.from_time = ShiftEndTime
    OverTimeRequest.to_time = Doc.get("out_time")
    OverTimeRequest.overtime_hours = OverTime / 60
    OverTimeRequest.is_holiday = IsHoliday
    OverTimeRequest.flags.ignore_permissions = True
    OverTimeRequest.save()

    
def CalculateLateEntry(Doc , ShiftDetails:dict):
    TimeDiffInHour = abs(TimeDiffInMintues(Doc.in_time , ShiftDetails.get("start_time"))) / 60
    if not TimeDiffInHour : 
        return 
    
    JordonHrSetting = GetJordonHrSettingByCompany(Doc.company)
    if not JordonHrSetting.get("total_working_hours_per_month") :
        frappe.throw(_("Missing Number of Total Working Hour in Settings"))
    
    EmployeeSalary = GetEmployeeSalary(Doc.employee , Doc.attendance_date, JordonHrSetting)
    LateEntryValue = (1 * EmployeeSalary * TimeDiffInHour) / JordonHrSetting.get("total_working_hours_per_month")
    CreateAdditionalSalary(
        LateEntryValue ,
        ShiftDetails.get("late_entry_salary_component") ,
        frappe._dict({
            "day" : Doc.attendance_date ,
            "employee" : Doc.employee,
            "company" : Doc.company ,
            "doctype" : Doc.doctype,
            "name" : Doc.name
        })
    )
    
    
