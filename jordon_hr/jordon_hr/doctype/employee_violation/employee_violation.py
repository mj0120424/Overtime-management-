# Copyright (c) 2025, Basel Waheed and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form , nowdate , add_to_date , get_datetime 
from hrms.hr.doctype.shift_assignment.shift_assignment import get_employee_shift as GetEmployeeShift
from jordon_hr.utilites import GetEmployeeSalary , GetJordonHrSettingByCompany , GetNumberOfShift , CreateAdditionalSalary


ViolationRepetision = {
    "1":"First Time",
    "2":"Second Time",
    "3":"Third Time",
    "4":"Fourth Time",
    "5":"Fifth Time",
}

class EmployeeViolation(Document):
    
    def validate(self) :
        self.ValidateViolation()
        self.ValidateViolationAfterOrBeforeDate()
        
        
    def ValidateViolation(self) :
        IsActive = frappe.db.get_value("Violations" , self.violation , "is_active")
        if not IsActive :
            frappe.throw(_("Violation {0} is not active").format(self.violation))
    
    
    def ValidateViolationAfterOrBeforeDate(self):        
        ListOfEmployeeViolatin = frappe.db.sql(""" 
            SELECT name , docstatus FROM `tabEmployee Violation` 
            WHERE  employee = %(Employee)s
                AND violation = %(Violation)s
                AND ( (violation_date >= %(ViolationDate)s  AND docstatus IN (1 , 0) ) OR  ( violation_date <  %(ViolationDate)s AND docstatus = 0 ) )
                AND name != %(Name)s
                                                                  
        """ ,{"Employee" : self.employee , "Violation" : self.violation , "ViolationDate" : self.violation_date , "Name" : self.name} , as_dict=True)
        
        for EmployeeViolation in ListOfEmployeeViolatin :
            frappe.throw(_("There is Violation {0} {1}").format(
                "After" if EmployeeViolation.get("docstatus") == 1 else "Before" ,
                frappe.bold(get_link_to_form(self.doctype , EmployeeViolation.get("name")))
            ))
    
    
    @frappe.whitelist()
    def GetEmployeeDetailsForViolation(self) :
        PenaltyAmount = 0.00
        RepeatedNumber = self.GetRepeatedNumberForViolation()
        ViolationDetails = self.GetViolationDetails(RepeatedNumber)
        if DeductionValue := ViolationDetails.get("deduction_value") :
            JordonHrSetting = GetJordonHrSettingByCompany(self.company)
            EmployeeSalary = GetEmployeeSalary(self.employee , self.violation_date , JordonHrSetting)
            EmployeeShiftDetails = GetEmployeeShift(self.employee , get_datetime(self.violation_date) , True , "forward")
            NumberofShiftHours = GetNumberOfShift(EmployeeShiftDetails.get('shift_type'))
            PenaltyAmount = (EmployeeSalary * NumberofShiftHours / JordonHrSetting.get("total_working_hours_per_month")) * DeductionValue
        return {
            "violation_repetision" : ViolationRepetision.get("{0}".format(RepeatedNumber)) ,
            "penalty" : ViolationDetails.get("action_type") ,
            "penalty_amount" : PenaltyAmount
        }
    
    
    def GetRepeatedNumberForViolation(self):
        ListOfNumber = frappe.db.get_all(self.doctype , {
            "name" : ["!=" , self.name] , "docstatus" : 1 , "employee" : self.employee ,
            "violation" : self.violation , "violation_date" : ["between" , [ add_to_date(nowdate() , months=-6), nowdate() ]]
        } , ["COUNT(name) as violation_count"])
        return ListOfNumber[0].get("violation_count") + 1
    
    
    def GetViolationDetails(self , RepeatedNumber) -> dict :
        ListOfViolationDetails = frappe.db.get_all("Violation Repetition Details" , {"parent" : self.violation } , ['action_type' , "deduction_value"] , order_by="idx asc")
        LengthOfViolationDetails = len(ListOfViolationDetails)
        if RepeatedNumber > LengthOfViolationDetails :
            RepeatedNumber -= LengthOfViolationDetails
            
        return ListOfViolationDetails[RepeatedNumber - 1]
    
    
    def on_submit(self):
        self.CreateAdditionalSalary()
        
        
    def CreateAdditionalSalary(self) :
        if self.penalty_amount :
            JordonHrSetting = GetJordonHrSettingByCompany(self.company)
            CreateAdditionalSalary(
                self.penalty_amount ,
                JordonHrSetting.get("salary_component_for_employee_violation") ,
                frappe._dict({
                    "day" : self.violation_date ,
                    "employee" : self.employee,
                    "company" : self.company ,
                    "doctype" : self.doctype,
                    "name" : self.name
                })
            )
            
            
    def on_cancel(self) :
        self.CancelAdditionalSalary()
        
    def CancelAdditionalSalary(self) :
        ListOfAdditionalSalary = frappe.db.get_all("Additional Salary" , {"ref_doctype" : self.doctype , "ref_docname" : self.name , "docstatus" : 1} , pluck="name")
        
        for AdditionalSalary in ListOfAdditionalSalary :
            frappe.get_doc("Additional Salary" , AdditionalSalary).cancel() 
            