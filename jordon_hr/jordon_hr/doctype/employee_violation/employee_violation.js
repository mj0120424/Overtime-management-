// Copyright (c) 2025, Basel Waheed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Violation", {
	refresh(frm) {
        frm.trigger("SetupQueries");
	},

    SetupQueries(frm) {
        frm.set_query("violation" , () => {
            return {
                filters : {
                    is_active: true
                }
            }
        })
    },

    employee(frm) {
        frm.trigger("GetEmployeeDetailsForViolation");
    },

    violation(frm) {
        frm.trigger("GetEmployeeDetailsForViolation");
    },

    GetEmployeeDetailsForViolation(frm) {
        if (frm.doc.employee && frm.doc.violation) {
            frappe.call({
                method : "GetEmployeeDetailsForViolation",
                doc : frm.doc ,
                callback:(r) => {
                    if (r.message) {
                        cur_frm.set_value(r.message);
                    }
                }
            })
        }
    }

});
