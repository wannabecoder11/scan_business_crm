import frappe
def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    
    user = frappe.session.user
    
    # Query logic: Owner OR Contact Email OR Shared via DocShare
    # We use frappe.get_all to fetch unique names first
    shared_with_user = frappe.get_all("DocShare", 
        filters={"share_doctype": "Opportunity", "user": user}, 
        pluck="share_name")

    opportunities = frappe.get_all("Opportunity",
        filters=[
            ["Opportunity", "name", "in", shared_with_user]
        ],
        fields=["name", "contact_email", "opportunity_owner", "title", "status"],
        ignore_permissions=True # ONLY for testing!
    )

    context.opportunities = opportunities #["test-opportunity", "test-opportunities2"] 
    context.title = ("My 3D Scan Projects")
    context.user = user
    return context