import frappe

def get_context(context):
    # If the user is logged in, redirect them straight to their project list
    if frappe.session.user != "Guest":
        frappe.local.flags.redirect_location = "/opportunities"
        raise frappe.Redirect
    
    # If they are a guest, show the landing page with the signup/form option
    context.title = "Start Your 3D Scan Project"
    return context