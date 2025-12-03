# Copyright (c) 2025, Basel Waheed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from collections import defaultdict

def execute(filters=None):
    Columns = GetColumns(filters)
    DictOfParent , DictOfChild = GetParentsAndChilds(filters)
    Data = HandleParentsAndChilds(DictOfParent , DictOfChild)
    return Columns, Data



def GetColumns(filters) :
    return [
        {
            "fieldname" : "employee_name" ,
            "fieldtype" : "Data",
            "label"     : _("Employee"),
            # "options"   : "Employee",
            "width"     : 300
        },
        {
            "fieldname" : "attendance_date" ,
            "fieldtype" : "Date",
            "label"     : _("Attendance Date"),
            "width"     : 140
        },
        {
            "fieldname" : "attendance" ,
            "fieldtype" : "Link",
            "label" : _("Attendance"),
            "options" : "Attendance" ,
            "width" : 180,
        },
        {
            "fieldname" : "check_in" ,
            "fieldtype" : "Data",
            "label" : _("Check in"),
            "width" : 100,
        },
        {
            "fieldname" : "check_out" ,
            "fieldtype" : "Data",
            "label" : _("Check Out"),
            "width" : 100,
        },
        {
            "fieldname" : "status" ,
            "fieldtype" : "Data",
            "label"     : _("Status"),
            "width"     : 100
        },
        {
            "fieldname" : "total_working_hour" ,
            "fieldtype" : "Float",
            "label"     : _("Total Working Hours"),
            "width"     : 160,
            "precision" : 2
        },
        {
            "fieldname" : "overtime_hours" ,
            "fieldtype" : "Float",
            "label"     : _("Overtime Hours"),
            "width"     : 140,
            "precision" : 2
        },
        {
            "fieldname" : "overtime_value" ,
            "fieldtype" : "Float",
            "label"     : _("Overtime Value"),
            "width"     : 140,
            "precision" : 2
        },
    ]
    
    
def GetData(filters):
    Conditions = ""
    if filters.get("company"):
        Conditions += " AND a.company = %(company)s "

    if filters.get("from_date") and filters.get("to_date"):
        Conditions += " AND a.attendance_date BETWEEN %(from_date)s AND %(to_date)s "

    if filters.get("employee"):
        Conditions += " AND a.employee = %(employee)s "
  
    SqlQuery = """
        SELECT
            a.name as attendance ,
            a.attendance_date  ,
            a.employee ,
            a.employee_name ,
            TIME_FORMAT(TIME(a.in_time),%(time_format)s) as check_in,
            TIME_FORMAT(TIME(a.out_time),%(time_format)s) as check_out,
            a.status ,
            IFNULL(TIME_TO_SEC(TIMEDIFF(TIME(a.out_time), TIME(a.in_time))) / 3600 , 0.00)  as total_working_hour ,
            IFNULL(o.overtime_hours ,0.00) as overtime_hours ,
            IFNULL(ad.amount , 0.00 )  as overtime_value
   
        FROM `tabAttendance` a
        LEFT JOIN `tabOvertime request` o
            ON o.attendance = a.name AND o.request_status ="Accepted" AND o.employee = a.employee AND o.docstatus = 1
        LEFT JOIN `tabAdditional Salary` ad
            ON ad.ref_doctype = "Overtime request" AND ad.ref_docname = o.name AND o.employee = ad.employee AND ad.docstatus = 1
            
        WHERE a.docstatus = 1
            {Conditions}
        ORDER BY a.attendance_date DESC , a.employee ;
    """.format(Conditions=Conditions)
    
    return frappe.db.sql(SqlQuery , {
        "time_format" : "%H:%i" ,
        "from_date" : filters.get('from_date') ,
        "to_date" : filters.get('to_date') ,
        "employee" : filters.get('employee') ,
        "company"  : filters.get("company"),
    } , as_dict=True)
    
    
    
def GetParentsAndChilds(filters) :
    DictOfParent = defaultdict(lambda : {"indent" : 0, "parent_employee": "" , "employee": "" ,"total_working_hour": 0.00,"overtime_hours": 0.00 , "overtime_value": 0.00})
    DictOfChild = defaultdict(list)
    ListOfData = GetData(filters)
    for Row in ListOfData :
        EmployeeID = Row['employee'] # Use a unique ID from the Row as the key
        DictOfParent[EmployeeID]["employee"] = Row['employee']
        DictOfParent[EmployeeID]["employee_name"] = Row['employee_name']
        DictOfParent[EmployeeID]["total_working_hour"] += float(Row['total_working_hour'])
        DictOfParent[EmployeeID]["overtime_hours"] += float(Row['overtime_hours'])
        DictOfParent[EmployeeID]["overtime_value"] += float(Row['overtime_value'])

        DictOfChild[EmployeeID].append({
            "indent" : 1 , 
            "parent_employee" : EmployeeID , 
            "attendance" : Row.get("attendance"),
            "attendance_date" : Row.get("attendance_date"),
            "check_in" : Row.get("check_in"),
            "check_out" : Row.get("check_out"),
            "status" : Row.get("status"),
            "total_working_hour" : Row.get("total_working_hour"),
            "overtime_hours" : Row.get("overtime_hours"),
            "overtime_value" : Row.get("overtime_value"),
        })
        
    return DictOfParent , DictOfChild


def HandleParentsAndChilds(DictOfParent:defaultdict ,DictOfChild:defaultdict):
    ListOfData = []
    for Key , Value in DictOfParent.items() :
        ListOfData.append(Value)
        if ListOfChild := DictOfChild.get(Key):
            ListOfData += ListOfChild
    return ListOfData