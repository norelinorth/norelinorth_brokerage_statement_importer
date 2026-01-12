app_name = "statement_importer"
app_title = "Noreli North Brokerage Statement Importer"
app_publisher = "Noreli North"
app_description = "Automatic Journal Entry posting from brokerage statement PDFs (Interactive Brokers, Charles Schwab, Fidelity, etc.)"
app_email = "https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues"
app_license = "mit"
app_version = "1.3.8"

# Apps
# ------------------

required_apps = ["frappe", "erpnext"]

# Fixtures (for loading default data)
fixtures = [
	{
		"dt": "Statement Provider",
		"filters": [["provider_name", "in", ["Interactive Brokers", "Charles Schwab", "Fidelity"]]]
	},
	{
		"dt": "Workspace",
		"filters": [["name", "=", "Statement Importer"]]
	}
]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ib_importer",
# 		"logo": "/assets/ib_importer/logo.png",
# 		"title": "IB Statement Importer",
# 		"route": "/ib_importer",
# 		"has_permission": "ib_importer.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ib_importer/css/ib_importer.css"
# app_include_js = "/assets/ib_importer/js/ib_importer.js"

# include js, css files in header of web template
# web_include_css = "/assets/ib_importer/css/ib_importer.css"
# web_include_js = "/assets/ib_importer/js/ib_importer.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ib_importer/public/scss/website"

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
# app_include_icons = "ib_importer/public/icons.svg"

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
# 	"methods": "ib_importer.utils.jinja_methods",
# 	"filters": "ib_importer.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ib_importer.install.before_install"
# after_install = "ib_importer.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ib_importer.uninstall.before_uninstall"
# after_uninstall = "ib_importer.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ib_importer.utils.before_app_install"
# after_app_install = "ib_importer.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ib_importer.utils.before_app_uninstall"
# after_app_uninstall = "ib_importer.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ib_importer.notifications.get_notification_config"

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ib_importer.tasks.all"
# 	],
# 	"daily": [
# 		"ib_importer.tasks.daily"
# 	],
# 	"hourly": [
# 		"ib_importer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ib_importer.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ib_importer.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ib_importer.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ib_importer.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ib_importer.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ib_importer.utils.before_request"]
# after_request = ["ib_importer.utils.after_request"]

# Job Events
# ----------
# before_job = ["ib_importer.utils.before_job"]
# after_job = ["ib_importer.utils.after_job"]

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
# 	"ib_importer.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

