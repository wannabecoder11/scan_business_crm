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