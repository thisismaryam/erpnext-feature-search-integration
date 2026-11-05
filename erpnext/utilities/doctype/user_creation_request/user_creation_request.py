# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address


class UserCreationRequest(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		created_user: DF.Link | None
		birth_date: DF.Data | None
		email: DF.Data
		full_name: DF.Data
		gender: DF.Data | None
		language: DF.Data | None
		mobile_no: DF.Data | None
		phone: DF.Data | None
		requested_by: DF.Link
		role_to_assign: DF.Link
		status: DF.Literal["Pending Approval", "Approved"]
		time_zone: DF.Data | None
	# end: auto-generated types

	def before_insert(self):
		self.requested_by = frappe.session.user
		self.status = "Pending Approval"
		self.created_user = None

	def validate(self):
		if not self.full_name or len(self.full_name.strip()) > 140:
			frappe.throw(_("Enter a valid full name."))
		if any(ord(character) < 32 for character in self.full_name):
			frappe.throw(_("The full name contains unsupported characters."))
		validate_email_address(self.email, throw=True)

		if self.status not in ("Pending Approval", "Approved"):
			frappe.throw(_("Invalid User creation request status."))
		if self.status == "Pending Approval" and self.created_user:
			frappe.throw(_("A pending request cannot have a created User."))
		if self.status == "Approved" and not self.created_user:
			frappe.throw(_("An approved request must reference its created User."))


def has_permission(doc, user=None, ptype=None):
	user = user or frappe.session.user
	if doc.owner == user and ptype in ("read", "select"):
		return True


def get_permission_query_conditions(user=None):
	user = user or frappe.session.user
	if user == "Administrator" or frappe.has_role("System Manager", user=user):
		return

	return f"`tabUser Creation Request`.owner = {frappe.db.escape(user)}"


@frappe.whitelist()
def approve_user_creation_request(name):
	if not frappe.has_role("System Manager"):
		frappe.throw(_("Only a System Manager can approve User creation requests."), frappe.PermissionError)
	frappe.has_permission("User", "create", throw=True)

	request = frappe.get_doc("User Creation Request", name)
	if request.status != "Pending Approval":
		frappe.throw(_("This User creation request has already been processed."))
	if not request.role_to_assign:
		frappe.throw(_("Select a desk-access role before approving this request."))
	if frappe.db.exists("User", request.email):
		frappe.throw(_("A User with this email address already exists."))

	role = frappe.get_doc("Role", request.role_to_assign)
	if not role.desk_access:
		frappe.throw(_("The selected role does not grant Desk access."))

	name_parts = request.full_name.split()
	user_values = {
		"doctype": "User",
		"email": request.email,
		"first_name": name_parts[0],
		"middle_name": " ".join(name_parts[1:-1]),
		"last_name": name_parts[-1] if len(name_parts) > 1 else "",
		"user_type": "System User",
		"enabled": 1,
		"send_welcome_email": 0,
		"roles": [{"role": role.name}],
	}
	for fieldname in ("mobile_no", "phone", "gender", "birth_date", "language", "time_zone"):
		if request.get(fieldname):
			user_values[fieldname] = request.get(fieldname)

	user = frappe.get_doc(user_values).insert()

	request.status = "Approved"
	request.created_user = user.name
	request.save()
	return {"user": user.name}
