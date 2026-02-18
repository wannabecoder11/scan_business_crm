import frappe

def handle_lead_automation(doc, method):
	"""Create a Customer/Opportunity for a Lead and enqueue user creation.

	This implementation is defensive:
	- uses try/except to avoid blocking the calling process
	- enqueues user creation/email sending to a background worker
	- fixes message printing and accidental decorator placement
	"""
	if not (getattr(doc, "custom_send_invite_and_open_discussion", False) and getattr(doc, "email_id", None)):
		return

	# 1. Create Customer first (so Opportunity and User can link to it)
	customer_name = getattr(doc, "lead_name", None) or getattr(doc, "company_name", None) or "Customer"
	target_customer = None
	try:
		if not frappe.db.exists("Customer", {"email_id": doc.email_id}):
			customer = frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_type": "Individual" if not getattr(doc, "company_name", None) else "Company",
					"email_id": doc.email_id,
					"lead_name": doc.name,
					"territory": getattr(doc, "territory", "All Territories"),
					"customer_group": "All Customer Groups",
				}
			)
			customer.insert(ignore_permissions=True)
			target_customer = customer.name
			frappe.msgprint(f"Customer created: {target_customer}")
		else:
			target_customer = frappe.db.get_value("Customer", {"email_id": doc.email_id}, "name")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "handle_lead_automation: create customer failed")

	# 2. Create Opportunity (linked to Customer)
	# opp_name = None
	# try:
	# 	if target_customer:
	# 		if not frappe.db.exists("Opportunity", {"party_name": target_customer, "status": "Open"}):
	# 			opp = frappe.get_doc(
	# 				{
	# 					"doctype": "Opportunity",
	# 					"opportunity_from": "Customer",
	# 					"party_name": target_customer,
	# 					"contact_email": doc.email_id,
	# 					"title": f"Scan Project: {customer_name}",
	# 					"company": doc.company or frappe.db.get_default("company"),
	# 				}
	# 			)
	# 			opp.insert(ignore_permissions=True)
	# 			doc_name = getattr(opp, "name", None)
	# 			opp_name = doc_name or opp.name
	# 			frappe.msgprint(f"Opportunity created: {opp_name}")
	# 		else:
	# 			opp_name = frappe.db.get_value("Opportunity", {"party_name": target_customer, "status": "Open"}, "name")
	# except Exception:
	# 	frappe.log_error(frappe.get_traceback(), "handle_lead_automation: create opportunity failed")

	# 3. Enqueue/Create User in background (avoid blocking the request)
	try:
		if not frappe.db.exists("User", doc.email_id):
			frappe.enqueue(
				"scan_business_crm.logic.lead.create_customer_user_background",
				queue="short",
				timeout=300,
				email=doc.email_id,
				first_name=getattr(doc, "lead_name", None),
			)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "handle_lead_automation: enqueue create user failed")

	# 4. Handle Sharing
	try:
		if opp_name:
			if not frappe.db.exists("DocShare", {"share_doctype": "Opportunity", "share_name": opp_name, "user": doc.email_id}):
				frappe.share.add(
					"Opportunity",
					opp_name,
					doc.email_id,
					read=1,
					write=1,
					notify=1,
					flags={"ignore_share_permission": True},
				)
				frappe.msgprint(f"Opportunity {opp_name} shared with {doc.email_id}")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "handle_lead_automation: sharing failed")

		
		def create_customer_user_background(email, first_name=None):
			"""Background job: create a Website User and send welcome email.

			This runs in a worker process (enqueued from `handle_lead_automation`).
			"""
			try:
				if frappe.db.exists("User", email):
					return

				user = frappe.get_doc(
					{
						"doctype": "User",
						"email": email,
						"first_name": first_name or email.split("@")[0],
						"user_type": "Website User",
						"send_welcome_email": 0,
					}
				)
				user.insert(ignore_permissions=True)
				user.add_roles("Customer")

				# Send welcome email from the background worker (may fail without blocking callers)
				try:
					if hasattr(user, "send_welcome_email"):
						user.send_welcome_email()
				except Exception:
					frappe.log_error(frappe.get_traceback(), "create_customer_user_background: send welcome failed")
			except Exception:
				frappe.log_error(frappe.get_traceback(), "create_customer_user_background: create user failed")

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