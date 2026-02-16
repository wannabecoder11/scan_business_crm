import frappe

def create_opportunity(document)
	if not frappe.db.exists("Opportunity", {"party_name": document.name}):
		opp = frappe.get_doc({
			"doctype": "Opportunity",
			"opportunity_from": "Lead",
			"party_name": document.name,
			"title": f"Scan Project: {document.lead_name}",
			"company": document.company or frappe.db.get_default("company")
		})
		opp.insert(ignore_permissions=True)


def create_customer_user(document)
	if not frappe.db.exists("User", document.email_id):
		user = frappe.get_doc({
			"doctype": "User",
			"email": document.email_id,
			"first_name": document.lead_name,
			"user_type": "Website User",
			"send_welcome_email": 1
		})
		user.insert(ignore_permissions=True)
		user.add_roles("Customer")


@frappe.whitelist()
def handle_lead_automation(doc, method):
    """
    doc: The Lead record being saved
    method: The event (e.g., after_insert)
    """
    if doc.send_invite_and_open_discussion and doc.email_id:

		# 1. Create Opportunity
		create_opportunity(doc)
        # 2. Create/Invite User
		create_customer_user(doc)

        # 3. Handle Sharing (DocShare is safe here!)
        if not frappe.db.exists("DocShare", {"share_doctype": "Opportunity", "share_name": opp.name, "user": doc.email_id}):
            frappe.share.add("Opportunity", opp.name, doc.email_id, read=1, write=1, notify=1)
