import frappe

@frappe.whitelist()
def handle_lead_automation(doc, method):
	"""
	doc: The Lead record being saved
	"""
	if doc.custom_send_invite_and_open_discussion and doc.email_id:
		
		# 1. Create Customer first (so Opportunity and User can link to it)
		customer_name = doc.lead_name or doc.company_name
		if not frappe.db.exists("Customer", {"email_id": doc.email_id}):
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": customer_name,
				"customer_type": "Individual" if not doc.company_name else "Company",
				"email_id": doc.email_id,
				"lead_name": doc.name,
				"territory": doc.territory or "All Territories",
				"customer_group": "All Customer Groups"
			})
			customer.insert(ignore_permissions=True)
			target_customer = customer.name
		else:
			target_customer = frappe.db.get_value("Customer", {"email_id": doc.email_id}, "name")

		# 2. Create Opportunity
		# Linked to Customer instead of Lead for better portal flow
		if not frappe.db.exists("Opportunity", {"party_name": target_customer, "status": "Open"}):
			opp = frappe.get_doc({
				"doctype": "Opportunity",
				"opportunity_from": "Customer",
				"party_name": target_customer,
				"contact_email": doc.email_id,
				"title": f"Scan Project: {customer_name}",
				"company": doc.company or frappe.db.get_default("company")
			})
			opp.insert(ignore_permissions=True)
			opp_name = opp.name
		else:
			opp_name = frappe.db.get_value("Opportunity", {"party_name": target_customer, "status": "Open"}, "name")

		# 3. Create/Invite User
		if not frappe.db.exists("User", doc.email_id):
			user = frappe.get_doc({
				"doctype": "User",
				"email": doc.email_id,
				"first_name": doc.lead_name,
				"user_type": "Website User",
				"send_welcome_email": 1,
			})
			user.insert(ignore_permissions=True)
			user.add_roles("Customer")
		
		# 4. Handle Sharing
		# We share the Opportunity with the User so they can see it in their list
		if not frappe.db.exists("DocShare", {"share_doctype": "Opportunity", "share_name": opp_name, "user": doc.email_id}):
			frappe.share.add("Opportunity", opp_name, doc.email_id, read=1, write=1, notify=1)@frappe.whitelist()
def add_opportunity_note(opportunity, note):
    # 1. Security Check: Is the user logged in?
    if frappe.session.user == "Guest":
        frappe.throw("You must be logged in to post notes.", frappe.PermissionError)

    # 2. Security Check: Does the user own this Opportunity?
    # We check if the Opportunity is linked to a Lead/Customer associated with this user
    opp = frappe.get_doc("Opportunity", opportunity)
    
    # Simple check: Is the user the creator or is the email matching?
    # You can expand this to check Lead/Customer links
    if opp.opportunity_owner != frappe.session.user and opp.contact_email != frappe.session.user:
        frappe.throw("You do not have permission to add notes to this project.", frappe.PermissionError)

    # 3. Add the note
    opp.append("notes", {
        "note": note,
        "added_by": frappe.session.user,
        "added_on": frappe.utils.now_datetime()
    })
    
    opp.save(ignore_permissions=True)
    return "Success"


@frappe.whitelist()
def get_user_opportunities():
	"""Return a list of Opportunity records owned by the logged-in user.

	This is intentionally simple: it filters by the document `owner` field.
	You can expand this later to include DocShare/shared records.
	"""
	user = frappe.session.user
	if user == "Guest":
		return []

	# Filter opportunities where owner_email OR contact_email matches the logged-in user
	ops = frappe.get_all(
		"Opportunity",
		fields=[
			"name",
			"title",
			"owner_email",
			"contact_email",
		],
		filters=[
			["or", ["owner_email", "=", user], ["contact_email", "=", user]]
		],
		order_by="modified desc",
		limit_page_length=100,
	)
	return ops

@frappe.whitelist()
def has_app_permission(doc, ptype, user=None, debug=False):
	"""Permission hook used by Frappe for `Opportunity`.

	Allows access if the current `user` matches `owner`, `owner_email`, or
	`contact_email`, or if the document is shared with the user via `DocShare`.
	"""
	user = user or frappe.session.user
	if user == "Guest":
		return False
	if user == "Administrator":
		return True

	# `doc` can be a Document or a dict-like
	def _get(field):
		try:
			if hasattr(doc, 'get'):
				return doc.get(field)
			return getattr(doc, field, None)
		except Exception:
			return None

	owner = _get("owner")
	owner_email = _get("owner_email")
	contact_email = _get("contact_email")

	doctype = _get("doctype") or (doc.doctype if hasattr(doc, 'doctype') else None)
	name = _get("name") or (doc.name if hasattr(doc, 'name') else None)

	if user in (owner, owner_email, contact_email):
		return True

	if doctype and name:
		if frappe.db.exists("DocShare", {"share_doctype": doctype, "share_name": name, "user": user}):
			return True

	return False