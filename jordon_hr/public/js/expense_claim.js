

frappe.ui.form.on("Expense Claim", {
    expenses_remove(frm) {
        frm.set_value("auto_attendance" , ISExpenseTypeTravelExists() ? 1 : 0);
    },

    validate(frm) {
        if ( frm.doc.auto_attendance) {
            if (frm.doc.from_date > frm.doc.to_date) {
                frappe.msgprint(__("To Date Must be Greater Than From Date"))
                frappe.validated = false;
            }
        }
    }
})


frappe.ui.form.on("Expense Claim Detail", {
    expense_type(frm ,cdt,cdn) {
        frm.set_value("auto_attendance" , ISExpenseTypeTravelExists() ? 1 : 0);
    }
})



let ISExpenseTypeTravelExists = () => {
    return cur_frm.doc.expenses.find(x => x.expense_type == "Travel")
}