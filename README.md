### Scan Business Crm

This modules has scripts, functions that is used to automate fucntional requirements of 3d scanning business.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app scan_business_crm
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/scan_business_crm
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

### Older code
```pthon
# Check if the trigger field is checked
if doc.custom_send_invite_and_open_discussion and doc.email_id:
    frappe.msgprint(f"Opportunity creating.")
    # 1. Create the Opportunity
    if not frappe.db.exists("Opportunity", {"party_name": doc.name}):
        opp = frappe.get_doc({
            "doctype": "Opportunity",
            "opportunity_from": "Lead",
            "party_name": doc.name,
            "title": doc.lead_name,
            "owner": doc.email_id,  # Set the customer as the owner
            "company": doc.company or frappe.defaults.get_user_default("company")
        })
        opp.insert(ignore_permissions=True)
        on_submit(opp, doc)
        frappe.msgprint(f"Opportunity {opp.name} created.")

    # 2. Create the Website User
    if not frappe.db.exists("User", doc.email_id):
        user = frappe.get_doc({
            "doctype": "User",
            "email": doc.email_id,
            "first_name": doc.lead_name,
            "send_welcome_email": 1,
            "user_type": "Website User",
            "roles": [{"role": "Customer"}]
        })
        user.insert(ignore_permissions=True)
        frappe.msgprint(f"User account created for {doc.email_id}.")
    else:
        # If user exists, ensure they have the Customer role
        existing_user = frappe.get_doc("User", doc.email_id)
        existing_user.add_roles("Customer")

```
