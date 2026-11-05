# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe

from erpnext.tests.permission_test_utils import make_fenced_user
from erpnext.tests.utils import ERPNextTestSuite
from erpnext.utilities.doctype.user_creation_request.user_creation_request import approve_user_creation_request
from erpnext.utilities.page.erpnext_assistant.erpnext_assistant import _create_user_creation_request


class TestUserCreationRequest(ERPNextTestSuite):
	def test_request_does_not_create_user_before_approval(self):
		email = "assistant-draft@example.com"

		request = _create_user_creation_request(
			"Assistant Draft",
			email,
			{"mobile_no": "+1 555 0100", "phone": "+1 555 0101"},
		)

		self.assertEqual(request.status, "Pending Approval")
		self.assertEqual(request.mobile_no, "+1 555 0100")
		self.assertEqual(request.phone, "+1 555 0101")
		self.assertFalse(frappe.db.exists("User", email))

	def test_approval_creates_active_system_user_with_selected_role(self):
		email = "assistant-approved@example.com"
		request = _create_user_creation_request(
			"Assistant Approved User",
			email,
			{"mobile_no": "+1 555 0100", "phone": "+1 555 0101"},
		)
		role_name = "Assistant Test Desk Role"
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc(
				{"doctype": "Role", "role_name": role_name, "desk_access": 1}
			).insert(ignore_permissions=True)
		request.role_to_assign = role_name
		request.save()

		result = approve_user_creation_request(request.name)
		user = frappe.get_doc("User", result["user"])
		request.reload()

		self.assertEqual(user.name, email)
		self.assertEqual(user.first_name, "Assistant")
		self.assertEqual(user.middle_name, "Approved")
		self.assertEqual(user.last_name, "User")
		self.assertEqual(user.mobile_no, "+1 555 0100")
		self.assertEqual(user.phone, "+1 555 0101")
		self.assertEqual(user.user_type, "System User")
		self.assertEqual(user.enabled, 1)
		self.assertEqual(user.send_welcome_email, 0)
		self.assertIn(role_name, [user_role.role for user_role in user.roles])
		self.assertEqual(request.status, "Approved")
		self.assertEqual(request.created_user, user.name)
		self.assertRaises(frappe.ValidationError, approve_user_creation_request, request.name)

	def test_approval_requires_desk_role(self):
		request = _create_user_creation_request("Assistant Missing Role", "assistant-missing-role@example.com")

		self.assertRaises(frappe.ValidationError, approve_user_creation_request, request.name)
		self.assertFalse(frappe.db.exists("User", request.email))

	def test_only_system_manager_can_approve(self):
		request = _create_user_creation_request("Assistant Restricted", "assistant-restricted@example.com")
		user = make_fenced_user("assistant-reviewer@example.com", ["Sales User"])

		with self.set_user(user):
			self.assertRaises(
				frappe.PermissionError,
				approve_user_creation_request,
				request.name,
			)
