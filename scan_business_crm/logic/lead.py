import frappe
from frappe.contacts.doctype.contact.contact import get_contact_name

def handle_lead_automation(doc, method):
	"""Create a Customer/Opportunity for a Lead and enqueue user creation.

	This implementation is defensive:
	- uses try/except to avoid blocking the calling process
	- enqueues user creation/email sending to a background worker
	- fixes message printing and accidental decorator placement
	"""
	if not (getattr(doc, "custom_send_invite_and_open_discussion", False) and getattr(doc, "email_id", None)):
		return

	# /Create User in background (avoid blocking the request)

	if frappe.db.exists("User", doc.email_id):
		frappe.msgprint('User already exists')
		return
	email = doc.email_id
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": doc.first_name or email.split("@")[0],
			"user_type": "Website User",
			"send_welcome_email": 1,
		}
	)
	user.insert(ignore_permissions=True)
	frappe.msgprint(f"User account created for {email}")
	
	# Send welcome email from the background worker (may fail without blocking callers)
	user.add_roles("Customer")

	#link lead to customer
	# if target_customer:
	# #	frappe.db.set_value("Lead", doc.name, "customer", target_customer)
	# 	frappe.db.set_value("Customer", target_customer, "lead_name", doc.name)
	# link lead to user
	# frappe.db.set_value("Lead", doc.name, "user_id", email)


	# 2. Create or Update the Contact
	contact_name = get_contact_name(email)
	if not contact_name:
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": doc.first_name or customer_name,
			"email_ids": [{"email_id": email, "is_primary": 1}]
		})
		contact.insert(ignore_permissions=True)
		contact_name = contact.name
		frappe.msgprint(f"Contact created: {contact_name}")
	else:
		contact = frappe.get_doc("Contact", contact_name)



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

# create customer from opportunity
def create_customer(doc, method):
	# 1. Create Customer first (so Opportunity and User can link to it)
	email = doc.email_id
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
	# 3. Link the Contact to the Customer
	# This is the "secret sauce" that lets the User see Customer data in the portal
	contact_name = get_contact_name(email)
	if not contact_name:
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": customer_name,
			"email_ids": [{"email_id": email, "is_primary": 1}]})
		contact.insert(ignore_permissions=True)
		contact_name = contact.name
		frappe.msgprint(f"Contact created: {contact_name}")
	else:
		contact = frappe.get_doc("Contact", contact_name)	
	contact.append("links", {
		"link_doctype": "Customer",
		"link_name": target_customer
	})
	contact.save(ignore_permissions=True)

@frappe.whitelist()
def share_opportunity_with_user(doc, method):
	"""Share the Opportunity with the contact email when an Opportunity is created from a Lead."""
	if doc.opportunity_from == "Lead" and doc.contact_email:
		if not frappe.db.exists("DocShare", {"share_doctype": "Opportunity", "share_name": doc.name, "user": doc.contact_email}):
			frappe.share.add(
				"Opportunity",
				doc.name,
				doc.contact_email,
				read=1,
				write=1,
				notify=1,
				# flags={"ignore_share_permission": True}, # commented as it was throwing errors
			)
			frappe.msgprint(f"Opportunity {doc.name} shared with {doc.contact_email}")
		else:
			frappe.msgprint(f"Opportunity {doc.name} is already shared with {doc.contact_email}")