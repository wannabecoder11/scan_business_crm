import frappe
from frappe.utils import random_string
# this function not being used
def create_customer_account(doc, method):
    # Only run for new leads/opportunities with an email
    if not doc.contact_email:
        return

    # 1. Check if user already exists
    if not frappe.db.exists("User", doc.contact_email):
        # 2. Create a new User
        user = frappe.get_doc({
            "doctype": "User",
            "email": doc.contact_email,
            "first_name": doc.contact_display or doc.contact_email.split('@')[0],
            "send_welcome_email": 0, # We will send a custom one
            "user_type": "Website User"
        })
        user.insert(ignore_permissions=True)
        
        # 3. Add 'Customer' role
        user.add_roles("Customer")

        # 4. Set a temporary password
        temp_password = random_string(10)
        user_auth = frappe.get_doc("User", user.name)
        user_auth.new_password = temp_password
        user_auth.save(ignore_permissions=True)

        # 5. Send Email with Login Link
        send_login_details(doc.contact_email, temp_password, doc.name)

        # Create a Customer record if it doesn't exist and link it to the Opportunity
        if not frappe.db.exists("Customer", {"email_id": email}):
            new_cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": doc.contact_display or email,
                "customer_type": "Individual",
                "email_id": email
            }).insert(ignore_permissions=True)
        
        # Link the Opportunity to this new Customer
        doc.db_set("customer", new_cust.name)

def send_login_details(email, password, opp_name):
    subject = "Access Your 3D Scan Project Room"
    message = f"""
        <h3>Welcome to 3D Scan STL!</h3>
        <p>Your project <b>{opp_name}</b> has been received.</p>
        <p>We have created a portal account for you to track progress and chat with our team.</p>
        <p>
            <b>Login URL:</b> <a href="https://cp.3dscanstl.com/login">cp.3dscanstl.com/login</a><br>
            <b>Username:</b> {email}<br>
            <b>Password:</b> {password}
        </p>
        <p>Please change your password after your first login.</p>
    """
    frappe.sendmail(recipients=[email], subject=subject, message=message)