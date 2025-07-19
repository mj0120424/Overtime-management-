import frappe


def GetShiftDetailsForEmployee(ShiftType) -> dict :
    return frappe.db.get_value("Shift Type" , {"name" : ShiftType} , [
        "salary_component_for_overtime" ,
        "salary_component_for_overtime_in_holiday",
        "calculate_overtime_after" , 
        "overtime_value", 
        "overtime_in_holiday_value" ,
        "start_time",
        "end_time" ,
        "enable_late_entry_marking",
        "late_entry_grace_period",
        "late_entry_salary_component",
    ] , as_dict=True , cache=True)



def GetEmployeeSalary(Employee , FromDate , JordonHrSetting) :
    ListOfFieldsIncludedInSalary = list(map(lambda x : x.get("field_name") , JordonHrSetting.get("overtime_fields") ))
    LastSalaryStructureAssignment = GetLastSalaryStructureAssignment(Employee , FromDate , ListOfFieldsIncludedInSalary)
    TotalSalary = sum(map(lambda x : x , LastSalaryStructureAssignment)) if LastSalaryStructureAssignment else 0.00
    return TotalSalary or 0.00


def CreateAdditionalSalary(OverTimeValue , SalaryComponent , Document:frappe._dict) -> int|float:

    AdditionalSalary = frappe.new_doc("Additional Salary")
    AdditionalSalary.employee = Document.employee
    AdditionalSalary.company = Document.company
    AdditionalSalary.payroll_date = Document.day
    AdditionalSalary.amount = OverTimeValue
    AdditionalSalary.salary_component = SalaryComponent
    AdditionalSalary.overwrite_salary_structure_amount = 0
    AdditionalSalary.ref_doctype = Document.doctype 
    AdditionalSalary.ref_docname = Document.name
    AdditionalSalary.flags.ignore_permissions = True
    AdditionalSalary.save()
    AdditionalSalary.submit()



def GetLastSalaryStructureAssignment(Employee , FromDate , ListOfFields=["name"]) :
    ListofSalaryStructureAssignment = frappe.db.get_all("Salary Structure Assignment" , {
        "docstatus" : 1 , 
        "employee" : Employee , 
        "from_date" : ["<=" , FromDate]
    }, ListOfFields , order_by="from_date desc", as_list=True) 
    
    return ListofSalaryStructureAssignment[0] if ListofSalaryStructureAssignment else None


def GetJordonHrSettingByCompany(Company) : 
    return frappe.get_cached_doc("Overtime HR Setting" , Company)