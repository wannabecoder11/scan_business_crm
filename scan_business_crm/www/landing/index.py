import frappe

def get_context(context):
    if frappe.session.user != "Guest":
        # Use the explicit redirect function
        frappe.redirect_to("/opps/opps")
        
    context.title = "Welcome to 3D Scan STL"