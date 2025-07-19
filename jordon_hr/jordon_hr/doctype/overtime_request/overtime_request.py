# Copyright (c) 2025, Basel Waheed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_link_to_form
from frappe.model.document import Document
from jordon_hr.utilites import (
    GetEmployeeSalary,
    GetLastSalaryStructureAssignment,
    GetJordonHrSettingByCompany ,
    CreateAdditionalSalary ,
    GetShiftDetailsForEmployee,
)


class Overtimerequest(Document):
    
    def validate(self) :
        self.ValidateDuplicateOvertimeInSameDate()
        self.ValidateEmployeeHasSalaryStructureAssignment()
  
  
    def ValidateDuplicateOvertimeInSameDate(self) :
        
        if OverTimeRequest := frappe.db.exists(self.doctype , {"day" : self.day , "employee" : self.employee , "dostatus" : ["!=" , 2]}) :
            frappe.throw(_("There is OverTime Request in Same Date For Employee {0} = {1}").format(
                self.employee ,
                frappe.bold(get_link_to_form(self.doctype , OverTimeRequest))
            ) , frappe.ValidationError)

    def ValidateEmployeeHasSalaryStructureAssignment(self) :
     
        if not GetLastSalaryStructureAssignment(self.employee , self.day) :
            frappe.throw(_("Employee Not Have Salary Structure Assignment") , frappe.ValidationError)
   

    def ValidateShiftDetails(self , ShiftDetails: dict) :
        ListOfFields = [ "salary_component_for_overtime" , "salary_component_for_overtime_in_holiday" , "overtime_value",  "overtime_in_holiday_value"]
  
        for Field in ListOfFields :
            if ShiftDetails.get(Field) in [None , ""] :
                frappe.throw(_("Missing Data In Shift {0}").format(Field.replace("_" , " ").title()))

  
    def on_submit(self) :
        self.HandleCreateAdditionalSalary()
  
  
    def HandleCreateAdditionalSalary(self) :
        
        if self.request_status == "Accepted" :
            ShiftDetails = GetShiftDetailsForEmployee(self.shift)
            self.ValidateShiftDetails(ShiftDetails)
            JordonHrSetting = GetJordonHrSettingByCompany(self.company)
            EmployeeBaseSalary = GetEmployeeSalary(self.employee , self.day , JordonHrSetting)
            
            if not JordonHrSetting.get("total_working_hours_per_month") :
                frappe.throw(_("Missing Number of Total Working Hour in Settings"))
            # OverTimeValue = ( EmployeeBaseSalary / 30 / 8 )  * ( ShiftDetails.overtime_in_holiday_value if self.is_holiday else ShiftDetails.overtime_value ) * self.overtime_hours
            OverTimeValue = (self.overtime_hours * EmployeeBaseSalary * ( ShiftDetails.overtime_in_holiday_value if self.is_holiday else ShiftDetails.overtime_value ) ) / JordonHrSetting.get("total_working_hours_per_month")
            CreateAdditionalSalary(
                OverTimeValue , 
                ShiftDetails.get("salary_component_for_overtime_in_holiday") if self.is_holiday else ShiftDetails.get("salary_component_for_overtime"),
                self
            ) 
            
            
    def on_cancel(self) :
        self.CancelAdditionalSalary()
        
        
    def CancelAdditionalSalary(self) :
        ListOfAdditionalSalary = frappe.db.get_all("Additional Salary" , {"ref_doctype" : self.doctype , "ref_docname" : self.name , "docstatus" : 1} , pluck="name")
        
        for AdditionalSalary in ListOfAdditionalSalary :
            frappe.get_doc("Additional Salary" , AdditionalSalary).cancel() 
            
            
    def on_trash(self) : 
        self.DeleteAdditionalSalary()
        
        
    def DeleteAdditionalSalary(self) :
        ListOfAdditionalSalary = frappe.db.get_all("Additional Salary" , {"ref_doctype" : self.doctype , "ref_docname" : self.name , "docstatus" : 2} , pluck="name")
        
        for AdditionalSalary in ListOfAdditionalSalary :
            frappe.delete_doc("Additional Salary" , AdditionalSalary)
            
  
