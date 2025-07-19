// Copyright (c) 2025, Basel Waheed and contributors
// For license information, please see license.txt

let FieldsOfSalaryStructureAssignment = [];


frappe.ui.form.on("Overtime HR Setting", {
	refresh(frm) {
        frm.trigger("GetFieldsForSalaryStructureAssignment");
	},

    GetFieldsForSalaryStructureAssignment(frm) {
        if (FieldsOfSalaryStructureAssignment.length == 0) {
            frappe.model.with_doctype("Salary Structure Assignment" , () => {
                FieldsOfSalaryStructureAssignment = frappe.get_meta("Salary Structure Assignment").fields.filter(r => ["Float" ,"Currency"].includes(r.fieldtype)).map(r => r.fieldname) ;
            })
        }
        setTimeout(() => {
            cur_frm.trigger("GetFieldsToTable");
        }, 300);
    },

    GetFieldsToTable(frm) {
        let FieldsNamesAdded = cur_frm.doc.overtime_fields.map(r => r.field_name) ;
        let FieldsNotSelected = FieldsOfSalaryStructureAssignment.filter(Field => FieldsNamesAdded.includes(Field) == false) ;
        cur_frm.fields_dict["overtime_fields"].grid.update_docfield_property("field_name" , "options" , FieldsNotSelected);   
    }
});


frappe.ui.form.on("Calculation Fields" , {
    overtime_fields_add(frm ,cdt ,cdn) {
       frm.events.GetFieldsToTable();
    },
    overtime_fields_remove(frm ,cdt ,cdn) {
       frm.events.GetFieldsToTable();
    }
})