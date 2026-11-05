// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("User Creation Request", {
	refresh(frm) {
		if (frm.doc.status !== "Pending Approval" || !frappe.user.has_role("System Manager")) {
			return;
		}

		frm.add_custom_button(__("Approve and Create User"), async () => {
			const response = await frappe.call({
				method: "erpnext.utilities.doctype.user_creation_request.user_creation_request.approve_user_creation_request",
				args: { name: frm.doc.name },
				freeze: true,
				freeze_message: __("Creating User"),
			});
			frappe.set_route("Form", "User", response.message.user);
		});
	},
});
