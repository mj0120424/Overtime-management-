// Copyright (c) 2025, Basel Waheed and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Time Card"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default" : frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_end()
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 0
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "status" && value == "Absent") {
			value = "<span style='color:red'>" + value + "</span>";
		} else if (column.fieldname == "status" && value == "On Leave") {
			value = "<span style='color:blue'>" + value + "</span>";
		} else if (column.fieldname == "status" && value == "Present") {
			value = "<span style='color:green'>" + value + "</span>";
		} else if (column.fieldname == "status" && value == "Dayoff") {
			value = "<span style='color:orange'>" + value + "</span>";
		} 
		if (!data.parent_employee){
			value = "<span style='font-weight:bold'>" + value + "</span>";
		}

		return value;
	},
	tree: true,
	name_field: "employee_name",
	parent_field: "parent_employee",
	initial_depth: 0,
};
