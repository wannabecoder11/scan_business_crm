import frappe

@frappe.whitelist()
def handle_lead_automation(doc, method):
	"""
	doc: The Lead record being saved
	method: The event (e.g., after_insert)
	"""
	if doc.custom_send_invite_and_open_discussion and doc.email_id:
		# 1. Create Opportunity
		if not frappe.db.exists("Opportunity", {"party_name": doc.name}):
			opp = frappe.get_doc({
				"doctype": "Opportunity",
				"opportunity_from": "Lead",
				"party_name": doc.name,
				"title": f"Scan Project: {doc.lead_name}",
				"company": doc.company or frappe.db.get_default("company")
			})
			opp.insert(ignore_permissions=True)

			# 2. Create/Invite User
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

			# 3. Handle Sharing (DocShare is safe here!)
			if not frappe.db.exists(
				"DocShare",
				{"share_doctype": "Opportunity", "share_name": opp.name, "user": doc.email_id},
			):
				frappe.share.add("Opportunity", opp.name, doc.email_id, read=1, write=1, notify=1)
@frappe.whitelist()
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