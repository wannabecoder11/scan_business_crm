import frappe

def get_context(context):
    name = frappe.form_dict.get('name')
    
    if not name:
        return context

    # 1. Get list of shared IDs
    shared_with_user = frappe.get_all("DocShare", 
        filters={"share_doctype": "Opportunity", "user": frappe.session.user}, 
        pluck="share_name")

    try:
        doc = frappe.get_doc("Opportunity", name)
        
        # 2. Security Check (The OR logic)
        is_shared = name in shared_with_user
        is_owner = doc.opportunity_owner == frappe.session.user
        is_contact = doc.contact_email == frappe.session.user

        if not (is_shared or is_owner or is_contact):
            # Instead of throwing a hard error, we can redirect to a 403 page
            frappe.throw("You do not have permission to view this project.", frappe.PermissionError)
            
        context.doc = doc
        
    except frappe.DoesNotExistError:
        context.doc = None

    return context