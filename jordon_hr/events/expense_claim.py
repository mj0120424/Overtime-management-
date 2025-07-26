import frappe
from frappe import _
from frappe.utils import getdate, add_days


def ValidateExpenseClaim(doc)  :
    
    if frappe.db.exists("Attendance" , {"employee" : doc.employee , "attendance_date" : ["between" , [doc.from_date ,  doc.to_date]] , "docstatus" : 1}) :
        frappe.throw(_("Employee Has Attendance in this Dates"))
        

def ExpenseClaimOnSubmit(doc , event) :
    
    if not doc.auto_attendance or not doc.from_date or not doc.to_date  : 
        return 
    
    ValidateExpenseClaim(doc)
    CreateAttendanceIFOlder(doc)
    
    
def CreateAttendanceIFOlder(doc) :
    ListOfDates = []
    CurrentDate = getdate()
    DateTaken = getdate(doc.from_date)
    
    if DateTaken > CurrentDate :  return
    
    while DateTaken <= CurrentDate :
        ListOfDates.append(DateTaken)
        DateTaken = add_days(DateTaken, 1)
        
    if ListOfDates :
        CreateAttendanceBeforeToday(doc , ListOfDates)
        
         
def CreateAttendanceBeforeToday(doc , ListOfDates) :
    for AttendanceDate in ListOfDates :
        try:
            NewAttendance = frappe.new_doc("Attendance")
            NewAttendance.employee = doc.employee
            NewAttendance.company  = doc.company
            NewAttendance.attendance_date  = AttendanceDate
            NewAttendance.status  = "Work From Home"
            NewAttendance.expense_claim = doc.name
            NewAttendance.flags.ignore_mandatory = True
            NewAttendance.save()
            NewAttendance.submit()

        except Exception as e:
            frappe.throw(_("Can't Create Attendance in Date {0} => {1}").format(AttendanceDate , e))
            
        
    
    
def ExpenseClaimOnCancel(doc , event):
    
    ListOfAttendance = frappe.db.get_all("Attendance" , {"expense_claim" : doc.name , "docstatus" : 1 } , pluck="name")
    for AttendanceName in ListOfAttendance :
        frappe.get_doc("Attendance" ,  AttendanceName).cancel()