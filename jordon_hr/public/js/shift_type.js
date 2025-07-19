
frappe.ui.form.on("Shift Type" , {
    refresh(frm) {
        frm.trigger("SetupQuiryFilters");
    },

    SetupQuiryFilters(frm) {
        frm.set_query("salary_component_for_overtime" , () => {
            return {
                filters : {
                    type : "Earning"
                }
            }
        })

        frm.set_query("salary_component_for_overtime_in_holiday" , () => {
            return {
                filters : {
                    type : "Earning"
                }
            }
        })
    }
})