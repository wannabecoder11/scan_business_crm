import frappe

def get_context(context):
    # Get the Opportunity ID from the URL (?name=OPP-001)
    name = frappe.form_dict.get('name')
    
    if not name:
        return context

    # Security: Ensure user is allowed to see this
    try:
        doc = frappe.get_doc("Opportunity", name)
        # Check if the user is the owner or linked to the lead/customer
        if doc.owner != frappe.session.user and doc.contact_email != frappe.session.user:
            frappe.throw("Not Permitted", frappe.PermissionError)
            
        context.doc = doc
    except frappe.DoesNotExistError:
        context.doc = None

    return context