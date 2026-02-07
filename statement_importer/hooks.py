app_name = "statement_importer"
app_title = "Noreli North Brokerage Statement Importer"
app_publisher = "Noreli North"
app_description = "Automatic Journal Entry posting from brokerage statement PDFs (Interactive Brokers and custom providers)"
app_email = ""
app_license = "mit"
app_version = "1.3.9"

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

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

