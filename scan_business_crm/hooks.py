app_name = "scan_business_crm"
app_title = "Scan Business Crm"
app_publisher = "wannabecoder11"
app_description = "This modules has scripts, functions that is used to automate fucntional requirements of 3d scanning business."
app_email = "wannabecoder11@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "scan_business_crm",
# 		"logo": "/assets/scan_business_crm/logo.png",
# 		"title": "Scan Business Crm",
# 		"route": "/scan_business_crm",
# 		"has_permission": "scan_business_crm.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/scan_business_crm/css/scan_business_crm.css"
# app_include_js = "/assets/scan_business_crm/js/scan_business_crm.js"

# include js, css files in header of web template
# web_include_css = "/assets/scan_business_crm/css/scan_business_crm.css"
# web_include_js = "/assets/scan_business_crm/js/scan_business_crm.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "scan_business_crm/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "scan_business_crm/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "scan_business_crm.utils.jinja_methods",
# 	"filters": "scan_business_crm.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "scan_business_crm.install.before_install"
# after_install = "scan_business_crm.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "scan_business_crm.uninstall.before_uninstall"
# after_uninstall = "scan_business_crm.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "scan_business_crm.utils.before_app_install"
# after_app_install = "scan_business_crm.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "scan_business_crm.utils.before_app_uninstall"
# after_app_uninstall = "scan_business_crm.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "scan_business_crm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = {
    "Lead": {
        "after_insert": "scan_business_crm.logic.lead.handle_lead_automation"
    },
    "Opportunity": {
        "after_insert": "scan_business_crm.logic.portal.create_customer_account"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"scan_business_crm.tasks.all"
# 	],
# 	"daily": [
# 		"scan_business_crm.tasks.daily"
# 	],
# 	"hourly": [
# 		"scan_business_crm.tasks.hourly"
# 	],
# 	"weekly": [
# 		"scan_business_crm.tasks.weekly"
# 	],
# 	"monthly": [
# 		"scan_business_crm.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "scan_business_crm.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "scan_business_crm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "scan_business_crm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["scan_business_crm.utils.before_request"]
# after_request = ["scan_business_crm.utils.after_request"]

# Job Events
# ----------
# before_job = ["scan_business_crm.utils.before_job"]
# after_job = ["scan_business_crm.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"scan_business_crm.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

has_permission = {
    "Opportunity": "scan_business_crm.logic.lead.has_app_permission"
}

portal_menu_items = [
    # {"title": "My 3D Scans", "route": "/project_room", "role": "Customer"},
    {"title": "My Discussions", "route": "/opps/opps", "role": "Customer"}
]

# your_app/hooks.py
website_route_rules = [
    {"from_route": "/opps/opps", "to_route": "opps/opps"},
    {"from_route": "/cp/project_room", "to_route": "cp/project_room"}
]

# Force redirect after login
login_redirect_url = "/opps/opps"


# Ensure that if they try to go to /me or /profile, they also get sent to your list
role_home_page = {
    "Customer": "/opps/opps",
    "Website User": "/opps/opps"
}