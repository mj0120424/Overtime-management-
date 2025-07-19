import frappe
from click import secho
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def AfterAppInstall(AppName) :
    
    if AppName != "jordon_hr" : return 
    
    CreateAdditionalFields()
    
    secho("HR Jordon Setup Successfully" , fg="blue")
    
    
def CreateAdditionalFields() :
    
    CustomFields = {
        "Employee" : [
            {
                "fieldname" : "allow_overtime" ,
                "label" : "Allow Overtime" ,
                "fieldtype" : "Check",
                "insert_after" : "salutation"
            }  
        ],
        "Shift Type" : [
            {
                "fieldname": "late_entry_salary_component",
                "label" : "Late Entry Salary Componenet" ,
                "fieldtype" : "Link" ,
                "options" : "Salary Component" ,
                "insert_after": "late_entry_grace_period",
                "depends_on" : "eval: doc.late_entry_grace_period && doc.enable_late_entry_marking ;"
            },
            {
                "fieldname": "overtime_details",
                "label" : "Overtime Details" ,
                "fieldtype" : "Section Break" ,
                "insert_after": "early_exit_grace_period",
                "hide_border" : 1
            },
            {
                "fieldname": "calculate_overtime_after",
                "label" : "Calculate Overtime After ( In Minutes)" ,
                "fieldtype" : "Int" ,
                "insert_after": "overtime_details",
                "default" : "30"
            },
            {
                "fieldname": "section_break102",
                "fieldtype" : "Section Break" ,
                "insert_after": "calculate_overtime_after",
                "hide_border" : 1
            },
            {
                "fieldname": "salary_component_for_overtime",
                "label" : "Salary Component For Overtime" ,
                "fieldtype" : "Link" ,
                "options" : "Salary Component" ,
                "insert_after": "section_break102",
            },
            {
                "fieldname" : "overtime_value" ,
                "label" : "Overtime Value Per Hour"  ,
                "fieldtype" : "Float",
                "insert_after" : "salary_component_for_overtime",
                "default" : "1.25"
            },
            {
                "fieldname" : "column_break105",
                "fieldtype" : "Column Break" ,
                "insert_after" : "overtime_value"  
            },
            {
                "fieldname": "salary_component_for_overtime_in_holiday",
                "label" : "Salary Component For Overtime ( Holiday )" ,
                "fieldtype" : "Link" ,
                "options" : "Salary Component" ,
                "insert_after": "column_break105",
            },
            {
                "fieldname" : "overtime_in_holiday_value" ,
                "label" : "Overtime Value ( Holiday ) Per Hour"  ,
                "fieldtype" : "Float",
                "insert_after" : "salary_component_for_overtime_in_holiday",
                "default" : "1.50"
            },
        ]
    }
    
    
    create_custom_fields(CustomFields , update=True)