import frappe
from frappe import _, bold
from frappe.utils import comma_and , formatdate
from hrms.payroll.doctype.additional_salary.additional_salary import AdditionalSalary


class JordonAdditionalSalary(AdditionalSalary) :
    
    def validate_recurring_additional_salary_overlap(self):
        JordonHRSettings = GetJordonHrSettingByCompany(self.company)
        
        if self.is_recurring and JordonHRSettings.get("allow_multiple_recurring_additional_salary") == 0 :
            AdditionalSalary = frappe.qb.DocType("Additional Salary")

            additional_salaries = (
                frappe.qb.from_(AdditionalSalary)
                .select(AdditionalSalary.name)
                .where(
                    (AdditionalSalary.employee == self.employee)
                    & (AdditionalSalary.name != self.name)
                    & (AdditionalSalary.docstatus == 1)
                    & (AdditionalSalary.is_recurring == 1)
                    & (AdditionalSalary.salary_component == self.salary_component)
                    & (AdditionalSalary.to_date >= self.from_date)
                    & (AdditionalSalary.from_date <= self.to_date)
                    & (AdditionalSalary.disabled == 0)
                )
            ).run(pluck=True)

            if additional_salaries and len(additional_salaries):
                frappe.throw(
                    _(
                        "Additional Salary: {0} already exist for Salary Component: {1} for period {2} and {3}"
                    ).format(
                        bold(comma_and(additional_salaries)),
                        bold(self.salary_component),
                        bold(formatdate(self.from_date)),
                        bold(formatdate(self.to_date)),
                    )
                )
                
                
def GetJordonHrSettingByCompany(Company) :
    OvertimeHRSetting = {"allow_multiple_recurring_additional_salary" : 0}
    if OvertimeHRSetting := frappe.db.exists("Overtime HR Setting" , Company) :
        OvertimeHRSetting  = frappe.get_cached_doc("Overtime HR Setting" , OvertimeHRSetting)
    return OvertimeHRSetting