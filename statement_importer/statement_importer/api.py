# Copyright (c) 2026, Noreli North and contributors
# For license information, please see license.txt

"""
API endpoints for Statement Importer
Standard Frappe pattern: Whitelisted methods with permission checks
"""

import json
import os

import frappe
import pdfplumber
from frappe import _
from frappe.utils import get_files_path


@frappe.whitelist()
def extract_pdf_preview(statement_doc_name):
	"""
	Extract preview data from uploaded PDF
	Phase 1: Basic text and table extraction

	Standard Frappe pattern:
	- Permission check
	- Get File attachment
	- Extract using pdfplumber
	- Return structured preview

	Args:
		statement_doc_name: Name of Statement Import document

	Returns:
		dict: {
			"success": bool,
			"text_preview": str,
			"tables_found": int,
			"tables_preview": list
		}
	"""
	# Permission check (standard pattern)
	if not frappe.has_permission("Statement Import", "write"):
		frappe.throw(_("No permission to process statements"))

	try:
		# Get statement document
		statement = frappe.get_doc("Statement Import", statement_doc_name)

		# Check if PDF file is attached
		if not statement.statement_file:
			frappe.throw(_("Please attach a PDF statement file first"))

		# FIX Issue #2 (v1.3.7): Add error handling for missing/corrupted File records
		# Get file path from attached file
		try:
			file_doc = frappe.get_doc("File", {
				"file_url": statement.statement_file,
				"attached_to_doctype": "Statement Import",
				"attached_to_name": statement.name
			})
		except frappe.DoesNotExistError:
			frappe.throw(
				_("PDF file record not found in database. The file may have been deleted or not properly attached. Please try re-uploading the statement PDF."),
				title=_("File Record Missing")
			)

		# Validate file_doc has required fields
		if not file_doc.file_name:
			frappe.throw(
				_("PDF file record is corrupted (missing file name). Please re-upload the statement PDF."),
				title=_("Corrupted File Record")
			)

		# Construct full file path (standard Frappe pattern)
		file_path = get_files_path(file_doc.file_name, is_private=file_doc.is_private)

		# Validate file exists on disk
		if not os.path.exists(file_path):
			frappe.throw(
				_("PDF file not found at expected location. Please try re-uploading the statement file."),
				title=_("File Not Found")
			)

		# FIX Issue #3: Validate file size before processing (prevent DoS)
		file_size = os.path.getsize(file_path)
		
		# Get limit from settings (standard Frappe pattern)
		max_size_mb = frappe.db.get_single_value("Statement Importer Settings", "max_file_size_mb") or 50
		max_size = max_size_mb * 1024 * 1024

		if file_size > max_size:
			frappe.throw(
				_("PDF file is too large ({0:.2f} MB). Maximum allowed size is {1} MB. Please use a smaller file.").format(
					file_size / (1024 * 1024),
					max_size_mb
				),
				title=_("File Too Large")
			)

		# Extract data using pdfplumber
		extracted_data = extract_pdf_data(file_path)

		# Update statement with preview
		statement.preview_data = format_preview_html(extracted_data)
		statement.save()
		# FIX Issue #1: Manual commit removed - Frappe handles this automatically

		return {
			"success": True,
			"text_preview": extracted_data["text"][:1000],  # First 1000 chars
			"tables_found": len(extracted_data["tables"]),
			"tables_preview": extracted_data["tables"][:3]  # First 3 tables
		}

	except Exception as e:
		if isinstance(e, frappe.ValidationError):
			raise e
		# FIX Issue #2: Don't expose raw exception messages to users (security + UX)
		frappe.log_error(
			message=f"Error extracting PDF: {e!s}\n{frappe.get_traceback()}",
			title="Statement Importer - PDF Extraction Error"
		)
		frappe.throw(
			_("Failed to extract PDF data. Please check if the file is a valid PDF and try again. If the issue persists, contact administrator."),
			title=_("PDF Extraction Failed")
		)


def extract_pdf_data(file_path):
	"""
	Extract text and tables from PDF using pdfplumber

	Standard pattern: Return structured data for further processing

	Args:
		file_path: Full path to PDF file

	Returns:
		dict: {
			"text": str,
			"tables": list of table data,
			"page_count": int
		}
	"""
	with pdfplumber.open(file_path) as pdf:
		# Validate PDF has pages
		if not pdf.pages or len(pdf.pages) == 0:
			frappe.throw(_("PDF file appears to be empty or corrupted. No pages found."))

		# Extract text from all pages
		text = ""
		tables = []

		for page in pdf.pages:
			# Extract text
			page_text = page.extract_text()
			if page_text:
				text += page_text + "\n\n"

			# Extract tables
			page_tables = page.extract_tables()
			if page_tables:
				for table in page_tables:
					# Filter out empty tables
					if table and len(table) > 0:
						tables.append(table)

		return {
			"text": text,
			"tables": tables,
			"page_count": len(pdf.pages)
		}


def format_preview_html(extracted_data):
	"""
	Format extracted data as HTML for preview

	Standard Frappe pattern: Use HTML for Text Editor field

	Args:
		extracted_data: Dict with text and tables

	Returns:
		str: HTML formatted preview
	"""
	html = "<h3>PDF Preview</h3>"

	# Add page count
	html += f"<p><strong>Pages:</strong> {extracted_data['page_count']}</p>"

	# Add text preview (handle potential empty text)
	html += "<h4>Text Content (first 2000 characters):</h4>"
	html += "<pre style='background: #f5f5f5; padding: 10px; white-space: pre-wrap;'>"
	text_preview = extracted_data.get('text', '')[:2000]
	if text_preview:
		html += frappe.utils.html_utils.escape_html(text_preview)
	else:
		html += "<em>No text content extracted</em>"
	html += "</pre>"

	# Add tables preview
	if extracted_data['tables']:
		html += f"<h4>Tables Found: {len(extracted_data['tables'])}</h4>"

		for idx, table in enumerate(extracted_data['tables'][:3], start=1):
			# Skip empty tables
			if not table or len(table) == 0:
				continue

			html += f"<p><strong>Table {idx}:</strong></p>"
			html += "<table class='table table-bordered table-sm' style='font-size: 12px;'>"

			# Add table rows
			for row_idx, row in enumerate(table[:10]):  # First 10 rows
				html += "<tr>"
				for cell in row:
					cell_content = str(cell) if cell is not None else ""
					tag = "th" if row_idx == 0 else "td"
					html += f"<{tag}>{frappe.utils.html_utils.escape_html(cell_content)}</{tag}>"
				html += "</tr>"

			# Calculate colspan safely (check if first row exists and is not None)
			if len(table) > 10 and table[0] and len(table[0]) > 0:
				html += f"<tr><td colspan='{len(table[0])}' class='text-muted'>... {len(table) - 10} more rows</td></tr>"

			html += "</table>"

	return html


@frappe.whitelist()
def parse_transactions_with_ai(statement_doc_name):
	"""
	Parse transactions using AI (Phase 2)

	Integrates with ai_assistant app to extract structured transaction data
	from the PDF text and tables

	Standard Frappe pattern:
	- Permission check
	- Load extracted data
	- Call AI with structured prompt
	- Parse JSON response
	- Validate transactions
	- Populate transaction lines

	Args:
		statement_doc_name: Name of Statement Import document

	Returns:
		dict: {
			"success": bool,
			"transactions_parsed": int,
			"transactions": list
		}
	"""
	# Permission check (standard pattern)
	if not frappe.has_permission("Statement Import", "write"):
		frappe.throw(_("No permission to parse transactions"))

	try:
		# Get statement document
		statement = frappe.get_doc("Statement Import", statement_doc_name)

		# Check if AI is enabled
		if not check_ai_enabled():
			frappe.throw(
				_("AI Assistant app is not installed or enabled. Please install norelinorth_ai_assistant app first.")
			)

		# Check if provider is selected (standard pattern)
		if not statement.statement_provider:
			frappe.throw(
				_("Statement Provider is required to parse transactions. Please select a provider and save the statement."),
				title=_("Missing Provider")
			)

		# Check if PDF has been extracted
		if not statement.preview_data:
			frappe.throw(_("Please extract PDF data first before parsing transactions"))

		# FIX Issue #3 (v1.3.9): Atomic status update to prevent race condition
		#
		# IMPROVED: Use standard Frappe pattern without private APIs
		#
		# Strategy:
		# 1. Use atomic UPDATE with conditional WHERE
		# 2. Check status after update to verify success
		# 3. If status didn't change, someone else got the lock
		#
		# This prevents concurrent requests from processing the same document simultaneously.
		# Query is safe: Uses parameterized query (%(name)s), no SQL injection risk

		# Get current status BEFORE update (for logging)
		status_before = frappe.db.get_value("Statement Import", statement_doc_name, "status")

		# Atomic update: Only succeeds if status is Draft/Completed/Failed
		frappe.db.sql("""
			UPDATE `tabStatement Import`
			SET status = 'Processing', modified = NOW()
			WHERE name = %(name)s
			AND status IN ('Draft', 'Completed', 'Failed')
		""", {"name": statement_doc_name})

		# Check if update succeeded by reading status back
		# If status is 'Processing', we got the lock
		# If status is something else, someone else got it first
		status_after = frappe.db.get_value("Statement Import", statement_doc_name, "status")

		if status_after != "Processing":
			# Update failed - document is being processed by another request
			frappe.log_error(
				message=f"Race condition detected: Status before={status_before}, status after={status_after}",
				title="Statement Importer - Race Condition"
			)

			if status_after == "Processing":
				# Most common case: another request is already processing
				frappe.throw(
					_("This statement is already being processed by another request. Please wait for the current operation to complete."),
					title=_("Processing In Progress")
				)
			else:
				# Unexpected status
				frappe.throw(
					_("Cannot process statement with status '{0}'. Status changed unexpectedly. Please try again.").format(status_after),
					title=_("Status Conflict")
				)

		# Reload document to get updated status
		statement.reload()

		# Re-extract PDF data for AI parsing
		# NOTE: We re-extract here rather than reusing preview_data because:
		# 1. preview_data contains HTML for display, not structured JSON
		# 2. Adding a new JSON field would require DocType migration
		# 3. Re-extraction only happens once during AI parsing (acceptable tradeoff)
		# Future improvement: Add extracted_data JSON field to avoid re-extraction
		if not statement.statement_file:
			frappe.throw(_("No statement file attached"))

		# FIX Issue #2 (v1.3.7): Add error handling for missing/corrupted File records
		# Get file and extract data
		try:
			file_doc = frappe.get_doc("File", {
				"file_url": statement.statement_file,
				"attached_to_doctype": "Statement Import",
				"attached_to_name": statement.name
			})
		except frappe.DoesNotExistError:
			frappe.throw(
				_("PDF file record not found in database. The file may have been deleted or not properly attached. Please try re-uploading the statement PDF."),
				title=_("File Record Missing")
			)

		# Validate file_doc has required fields
		if not file_doc.file_name:
			frappe.throw(
				_("PDF file record is corrupted (missing file name). Please re-upload the statement PDF."),
				title=_("Corrupted File Record")
			)

		file_path = get_files_path(file_doc.file_name, is_private=file_doc.is_private)

		# Validate file exists on disk
		if not os.path.exists(file_path):
			frappe.throw(
				_("PDF file not found at expected location. Please try re-uploading the statement file."),
				title=_("File Not Found")
			)

		extracted_data = extract_pdf_data(file_path)

		# Parse with AI
		transactions = parse_with_ai(extracted_data, statement)

		# Clear existing transactions
		statement.transactions = []

		# Add parsed transactions
		for txn in transactions:
			# FIX Issue #7: Validate amounts exist and are > 0 (no silent zero defaults)
			debit_amt = txn.get("debit_amount")
			credit_amt = txn.get("credit_amount")
			txn_desc = txn.get("description", "Unnamed")

			if not debit_amt or frappe.utils.flt(debit_amt) <= 0:
				frappe.throw(
					_("Transaction '{0}': Debit amount is required and must be greater than zero. Got: {1}").format(
						txn_desc[:50] if len(txn_desc) > 50 else txn_desc,
						debit_amt
					)
				)

			if not credit_amt or frappe.utils.flt(credit_amt) <= 0:
				frappe.throw(
					_("Transaction '{0}': Credit amount is required and must be greater than zero. Got: {1}").format(
						txn_desc[:50] if len(txn_desc) > 50 else txn_desc,
						credit_amt
					)
				)

			statement.append("transactions", {
				"transaction_date": txn.get("date"),
				"description": txn.get("description"),
				"currency": txn.get("currency"),  # No fallback - validation ensures this exists
				"account_debit": txn.get("account_debit"),
				"debit_amount": frappe.utils.flt(debit_amt),
				"account_credit": txn.get("account_credit"),
				"credit_amount": frappe.utils.flt(credit_amt),
				"status": "Pending"
			})

		# Update status
		statement.status = "Completed"
		statement.save()
		# FIX Issue #1: Manual commit removed - Frappe handles this automatically

		return {
			"success": True,
			"transactions_parsed": len(transactions),
			"transactions": transactions
		}

	except Exception as e:
		if isinstance(e, frappe.ValidationError):
			raise e

		# Update status to failed
		try:
			statement.status = "Failed"
			statement.error_log = f"AI Parsing Error: {e!s}"
			statement.save()
		except Exception as update_error:
			# Log the failure to update status (don't hide this error)
			frappe.log_error(
				message=f"Failed to update statement status after AI error: {update_error!s}\n{frappe.get_traceback()}",
				title="Statement Importer - Status Update Error"
			)

		# Standard Frappe pattern: Log error, show user-friendly message
		frappe.log_error(
			message=f"Error parsing transactions with AI: {e!s}\n{frappe.get_traceback()}",
			title="Statement Importer - AI Parsing Error"
		)
		# FIX Issue #2: Don't expose raw exception to users
		frappe.throw(
			_("Failed to parse transactions with AI. Please check the Error Log for details or contact administrator."),
			title=_("AI Parsing Failed")
		)


def check_ai_enabled():
	"""
	Check if AI Assistant is available and can be imported

	Standard Frappe pattern: Check if app is installed and functional

	Returns:
		bool: True if AI Assistant is available
	"""
	try:
		# Check if norelinorth_ai_assistant is installed
		if 'norelinorth_ai_assistant' not in frappe.get_installed_apps():
			return False

		# Check if AI Provider exists and is configured
		if not frappe.db.exists("DocType", "AI Provider"):
			return False

		settings = frappe.get_single("AI Provider")

		# Check if AI Provider is active and has required fields
		if not settings.is_active:
			return False

		# Check for required configuration (don't expose specific field names in logs)
		if not settings.default_model or not settings.get("api_key"):
			return False

		# Verify the API module can be imported (consistency with parse_with_ai)
		try:
			from norelinorth_ai_assistant.ai_provider_api import call_ai
		except ImportError:
			return False

		return True
	except Exception:
		return False


def parse_with_ai(extracted_data, statement):
	"""
	Parse transactions from extracted PDF data using AI

	Leverages existing ai_helper.py pattern from Journal Validation app

	Args:
		extracted_data: Dict with text and tables
		statement: Statement Import document

	Returns:
		list: Parsed transactions
	"""
	try:
		from norelinorth_ai_assistant.ai_provider_api import call_ai
	except ImportError:
		frappe.throw(_("AI Assistant app not properly installed. Please install norelinorth_ai_assistant app."))

	# Build prompt for statement parsing (provider-agnostic)
	prompt = build_parsing_prompt(extracted_data, statement)

	# Call AI API
	response = call_ai(prompt=prompt)

	# FIX Issue #2 (v1.3.9): Comprehensive AI response validation
	response = validate_ai_response(response)

	# Parse JSON response (same pattern as journal_validation/ai_helper.py)
	transactions = parse_ai_response(response)

	# Validate transactions
	validated_transactions = validate_parsed_transactions(transactions, statement)

	return validated_transactions


def validate_ai_response(response):
	"""
	Comprehensive validation of AI response before parsing
	FIX Issue #2 (v1.3.9): Enhanced validation to catch invalid responses early

	Standard Frappe pattern: Fail fast with helpful errors

	Validates:
	- Type (must be string)
	- Not empty
	- Valid UTF-8 encoding
	- Not an HTML error page
	- Not an error message format
	- Reasonable size

	Args:
		response: AI response (expected to be string)

	Returns:
		str: Validated response (stripped of whitespace)

	Raises:
		frappe.ValidationError: If response is invalid
	"""
	# Check type - must be string
	if not isinstance(response, str):
		frappe.log_error(
			message=f"AI returned non-string response: type={type(response)}, value={response!r}",
			title="Statement Importer - Invalid Response Type"
		)
		frappe.throw(
			_("AI returned invalid response type. Expected text, got {0}. Please check AI Provider configuration.").format(type(response).__name__),
			title=_("Invalid AI Response")
		)

	# Check not empty
	if not response or not response.strip():
		frappe.throw(
			_("AI returned empty response. Please check AI Provider configuration and try again."),
			title=_("Empty AI Response")
		)

	# Strip whitespace for further checks
	response = response.strip()

	# Check encoding is valid UTF-8
	try:
		response.encode('utf-8')
	except UnicodeEncodeError as e:
		frappe.log_error(
			message=f"AI response has encoding issues: {e!s}\nResponse preview: {response[:500]}",
			title="Statement Importer - Encoding Error"
		)
		frappe.throw(
			_("AI response contains invalid characters. Please try again or contact administrator."),
			title=_("Encoding Error")
		)

	# Check for HTML error pages (common when API fails)
	if response.lower().startswith('<!doctype') or response.lower().startswith('<html'):
		frappe.log_error(
			message=f"AI returned HTML instead of JSON:\n{response[:1000]}",
			title="Statement Importer - HTML Response"
		)
		frappe.throw(
			_("AI returned HTML error page instead of JSON. The AI service may be down. Please try again later or contact administrator."),
			title=_("AI Service Error")
		)

	# Check for common error message formats
	error_indicators = [
		"error:",
		"exception:",
		"failed:",
		"internal server error",
		"service unavailable",
		"timeout",
		"rate limit"
	]
	response_lower = response.lower()
	for indicator in error_indicators:
		if response_lower.startswith(indicator):
			frappe.log_error(
				message=f"AI returned error message:\n{response}",
				title="Statement Importer - AI Error Message"
			)
			frappe.throw(
				_("AI service returned an error. Please try again later or contact administrator."),
				title=_("AI Service Error")
			)

	# Check response size is reasonable (not too large - indicates something wrong)
	max_size = 500000  # 500KB - should be more than enough for JSON
	if len(response) > max_size:
		frappe.log_error(
			message=f"AI response too large: {len(response)} bytes (max {max_size})\nFirst 1000 chars: {response[:1000]}",
			title="Statement Importer - Response Too Large"
		)
		frappe.throw(
			_("AI returned unusually large response ({0} KB). This may indicate an error. Please try again or contact administrator.").format(len(response) // 1024),
			title=_("Invalid Response Size")
		)

	# Check response is not just "I cannot help" or similar refusal
	refusal_patterns = [
		"i cannot",
		"i am unable",
		"i can't",
		"apologies, but",
		"sorry, but",
		"unfortunately, i cannot"
	]
	for pattern in refusal_patterns:
		if pattern in response_lower and len(response) < 1000:
			# Likely a refusal message - log it
			frappe.log_error(
				message=f"AI refused to parse:\n{response}",
				title="Statement Importer - AI Refusal"
			)
			frappe.throw(
				_("AI was unable to parse the statement. The PDF may not contain clear transaction data, or the format is not recognized. Please ensure the PDF contains a detailed transaction list with dates and amounts."),
				title=_("AI Cannot Parse Statement")
			)

	# All validations passed
	return response


def build_parsing_prompt(extracted_data, statement):
	"""
	Build AI prompt for parsing brokerage statements
	REQUIRES Statement Provider to be configured - no hardcoded fallbacks

	Standard Frappe pattern: All configuration from database

	Args:
		extracted_data: Dict with text and tables
		statement: Statement Import document

	Returns:
		str: Prompt for AI

	Raises:
		frappe.ValidationError: If provider not configured or invalid
	"""
	# CRITICAL: Provider MUST be configured (no hardcoded fallbacks)
	if not statement.statement_provider:
		frappe.throw(
			_("Statement Provider is required. Please select a provider (Interactive Brokers, Charles Schwab, etc.) before parsing transactions."),
			title=_("Provider Not Configured")
		)

	# Load provider configuration
	try:
		provider = frappe.get_doc("Statement Provider", statement.statement_provider)
	except Exception as e:
		frappe.log_error(
			message=f"Failed to load provider: {e!s}",
			title="Statement Importer - Provider Load Error"
		)
		frappe.throw(
			_("Failed to load Statement Provider '{0}'. Please verify the provider exists and try again.").format(statement.statement_provider)
		)

	# Validate provider is enabled
	if not provider.enabled:
		frappe.throw(
			_("Statement Provider '{0}' is disabled. Please enable it or select a different provider.").format(provider.provider_name),
			title=_("Provider Disabled")
		)

	# Validate provider has prompt template
	if not provider.prompt_template:
		frappe.throw(
			_("Statement Provider '{0}' has no prompt template configured. Please configure the prompt template before parsing.").format(provider.provider_name),
			title=_("Prompt Template Missing")
		)

	# Build prompt from template (pass provider for accounting rules)
	return build_prompt_from_template(provider, extracted_data, statement)


def get_allowed_account_names(provider, company):
	"""
	Get list of allowed account names from provider's accounting rules

	Args:
		provider: Statement Provider document
		company: Company name

	Returns:
		set: Set of allowed account names
	"""
	company_abbr = frappe.db.get_value("Company", company, "abbr")
	if not company_abbr:
		return set()

	allowed_accounts = set()

	if not provider.accounting_rules:
		return allowed_accounts

	for rule in provider.accounting_rules:
		if not rule.enabled:
			continue

		# Build account names same way as in examples
		debit_account = rule.debit_account_template.replace("{provider}", provider.provider_name)
		credit_account = rule.credit_account_template.replace("{provider}", provider.provider_name)

		debit_account_full = f"{debit_account} - {company_abbr}"
		credit_account_full = f"{credit_account} - {company_abbr}"

		allowed_accounts.add(debit_account_full)
		allowed_accounts.add(credit_account_full)

	return allowed_accounts


def generate_accounting_examples(provider, company):
	"""
	Generate JSON examples from provider's accounting rules
	OPTIMIZED: Reduced prompt size by ~70% (from ~4500 to ~1500 chars)

	Standard Frappe pattern: Configuration from database, no hardcoded values

	Args:
		provider: Statement Provider document
		company: Company name

	Returns:
		str: Formatted JSON examples for AI prompt
	"""
	# Get company abbreviation for account names
	company_abbr = frappe.db.get_value("Company", company, "abbr")
	if not company_abbr:
		frappe.throw(_("Company '{0}' has no abbreviation set").format(company))

	# Check if provider has accounting rules
	if not provider.accounting_rules or len(provider.accounting_rules) == 0:
		# No rules configured - return generic guidance
		return _("Use standard accounting account names (e.g., 'Cash - Bank Account', 'Investments - Securities', 'Interest Income', etc.)")

	# Build examples from accounting rules (limit to first 4 for prompt size)
	examples = []
	for idx, rule in enumerate(provider.accounting_rules):
		if not rule.enabled:
			continue
		if len(examples) >= 4:  # Limit to 4 examples max
			break

		# Replace {provider} placeholder in account templates
		debit_account = rule.debit_account_template.replace("{provider}", provider.provider_name)
		credit_account = rule.credit_account_template.replace("{provider}", provider.provider_name)

		# Add company abbreviation
		debit_account_full = f"{debit_account} - {company_abbr}"
		credit_account_full = f"{credit_account} - {company_abbr}"

		# Generate example based on transaction type
		example = {
			"date": frappe.utils.nowdate(),
			"description": rule.description_template or f"Example {rule.transaction_type}",
			"currency": "USD",
			"account_debit": debit_account_full,
			"debit_amount": 100.00,
			"account_credit": credit_account_full,
			"credit_amount": 100.00
		}
		examples.append(example)

	if not examples:
		return _("No enabled accounting rules found. Use standard account names.")

	# Format as JSON string for prompt (compact to save space)
	import json
	examples_json = json.dumps(examples, separators=(',', ':'))

	# Extract unique account names from ALL rules (not just first 5) for whitelist
	unique_accounts = set()
	for rule in provider.accounting_rules:
		if not rule.enabled:
			continue
		debit_account = rule.debit_account_template.replace("{provider}", provider.provider_name)
		credit_account = rule.credit_account_template.replace("{provider}", provider.provider_name)
		unique_accounts.add(f"{debit_account} - {company_abbr}")
		unique_accounts.add(f"{credit_account} - {company_abbr}")

	# Build whitelist as comma-separated (saves space vs bullet points)
	whitelist = ", ".join([f"'{acc}'" for acc in sorted(unique_accounts)])

	# OPTIMIZED: Compact prompt (reduced from ~4500 to ~1500 chars)
	return f"""
ALLOWED ACCOUNTS (use EXACT names):
{whitelist}

TRANSACTION EXAMPLES:
{examples_json}

CRITICAL RULES:
1. Copy account names EXACTLY from allowed list (character-by-character)
2. DO NOT translate account names (always use English, even if PDF is German/other language)
3. DO NOT shorten or simplify names (e.g., "Cash" → WRONG, must be "Cash - Interactive Brokers Account - {company_abbr}")
4. Every account MUST include the " - {company_abbr}" suffix
5. If German PDF: "Barmittel"→"Cash - Interactive Brokers Account - {company_abbr}", "Dividenden"→"Dividend Income - {company_abbr}", "Provisionen"→"Brokerage Fees - {company_abbr}"
6. Only use accounts from the allowed list above - never invent new ones
"""


def build_prompt_from_template(provider, extracted_data, statement):
	"""
	Build prompt from provider template by replacing placeholders

	Placeholder syntax: {placeholder_name}

	Standard placeholders:
	- {company}: Company name
	- {statement_period}: Statement period
	- {import_date}: Import date
	- {text}: Extracted PDF text
	- {tables}: Formatted tables
	- {provider}: Provider name
	- {accounting_examples}: JSON examples from accounting rules (NEW)

	Args:
		provider: Statement Provider document (with accounting_rules)
		extracted_data: Dict with text and tables
		statement: Statement Import document

	Returns:
		str: Rendered prompt
	"""
	# Format tables for prompt
	tables_text = format_tables_for_prompt(extracted_data['tables'])

	# Validate required data (no fallback values per standards)
	if not statement.company:
		frappe.throw(_("Company is required for AI parsing"))

	# Generate accounting examples from provider's accounting rules
	accounting_examples = generate_accounting_examples(provider, statement.company)

	# Build placeholder values (no fallback values - fail if missing)
	placeholders = {
		"company": statement.company,
		"statement_period": statement.statement_period or _("Not specified"),
		"import_date": str(statement.import_date) if statement.import_date else str(frappe.utils.today()),
		"text": extracted_data['text'][:3000],  # First 3000 chars
		"tables": tables_text,
		"provider": statement.statement_provider,
		"accounting_examples": accounting_examples
	}

	# Replace placeholders in template
	prompt = provider.prompt_template
	for key, value in placeholders.items():
		placeholder = "{" + key + "}"
		prompt = prompt.replace(placeholder, str(value))

	# BACKWARDS COMPATIBILITY: If {accounting_examples} wasn't in the template,
	# append it to the end. This ensures optimized accounting examples are always included.
	if "{accounting_examples}" not in provider.prompt_template:
		prompt += "\n\n" + accounting_examples

	return prompt


def format_tables_for_prompt(tables, max_tables=5, max_rows=20):
	"""
	Format tables as text for prompt inclusion

	Args:
		tables: List of table data
		max_tables: Maximum number of tables to include
		max_rows: Maximum rows per table

	Returns:
		str: Formatted tables text
	"""
	tables_text = ""
	for idx, table in enumerate(tables[:max_tables], start=1):
		# Skip empty or None tables
		if not table:
			continue

		tables_text += f"\n\nTable {idx}:\n"
		for _row_idx, row in enumerate(table[:max_rows]):
			# Skip None or empty rows
			if not row:
				continue
			tables_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"

		if len(table) > max_rows:
			tables_text += f"... ({len(table) - max_rows} more rows)\n"

	return tables_text if tables_text else "No tables found"


def parse_ai_response(response):
	"""
	Parse AI JSON response into structured transactions

	Same pattern as journal_validation/ai_helper.py:133-157

	Args:
		response: AI response string

	Returns:
		list: Parsed transactions
	"""
	# Strip markdown code fences if present
	cleaned = response.strip()
	if cleaned.startswith('```'):
		lines = cleaned.split('\n')
		# Remove opening fence (e.g., ```json)
		if lines[0].startswith('```'):
			lines = lines[1:]
		# Remove closing fence
		if lines and lines[-1].strip() == '```':
			lines = lines[:-1]
		cleaned = '\n'.join(lines).strip()

	# Try to parse JSON
	try:
		transactions = json.loads(cleaned)
		if isinstance(transactions, list):
			return transactions
		else:
			frappe.throw(_("AI response is not a list of transactions"))
	except json.JSONDecodeError as e:
		# AGGRESSIVE TRUNCATION RECOVERY
		# For large statements, AI often hits token limits and returns incomplete JSON
		# Try to salvage what we can by finding the last complete transaction
		# Check if response was truncated (common with large statements)
		# "Expecting property name" or "Unterminated string" indicates truncation
		error_msg = str(e)
		is_truncation_error = "Expecting property name" in error_msg or "Unterminated string" in error_msg

		# Log the error details for debugging
		frappe.log_error(
			message=f"JSON Parse Error: {error_msg}\n\n"
					f"Is Truncation Error: {is_truncation_error}\n\n"
					f"Response Length: {len(response)} chars\n\n"
					f"Cleaned Length: {len(cleaned)} chars\n\n"
					f"Last 500 chars: {cleaned[-500:] if len(cleaned) > 500 else cleaned}",
			title="Statement Importer - Parse Error Debug"
		)

		if is_truncation_error:
			# Attempt to recover by finding last complete transaction
			# Strategy: Find the last closing brace before the error
			last_complete = -1

			# Use error position if available
			# FIX: Check 'is not None' instead of truthiness (pos=0 is valid)
			if hasattr(e, 'pos') and e.pos is not None:
				error_pos = e.pos
				# Find last complete transaction (}) before error
				search_area = cleaned[:error_pos]
				last_brace = search_area.rfind("}")
				if last_brace > 0:
					# Verify this is end of transaction object by checking if next char is comma or whitespace
					next_chars = cleaned[last_brace+1:last_brace+5].strip()
					if not next_chars or next_chars.startswith(",") or next_chars.startswith("]"):
						last_complete = last_brace

			# Fallback: Find last },
			if last_complete < 0:
				last_brace_comma = cleaned.rfind("},")
				if last_brace_comma > 0:
					# Point to the } not the comma
					last_complete = last_brace_comma

			# Attempt recovery if we found a good cutoff point
			if last_complete > 0:
				# Close array after the last complete }
				fixed_json = cleaned[:last_complete+1] + "\n]"

				frappe.log_error(
					message=f"Attempting recovery...\n"
							f"Original length: {len(cleaned)}\n"
							f"Truncated at: {last_complete}\n"
							f"Fixed JSON length: {len(fixed_json)}\n"
							f"Fixed JSON: {fixed_json}",
					title="Statement Importer - Recovery Attempt"
				)

				try:
					transactions = json.loads(fixed_json)
					if isinstance(transactions, list) and len(transactions) > 0:
						frappe.msgprint(
							_("✅ Recovered {0} transactions from truncated response. Some may be missing.").format(len(transactions)),
							indicator="yellow",
							title=_("Partial Success")
						)
						return transactions
					else:
						frappe.log_error("Recovery produced empty or invalid result", "Statement Importer - Recovery Failed")
				except Exception as recovery_error:
					frappe.log_error(
						message=f"Recovery parse failed: {recovery_error!s}\n"
								f"Fixed JSON was: {fixed_json[:1000]}...",
						title="Statement Importer - Recovery Parse Failed"
					)
			else:
				frappe.log_error(
					f"Could not find valid truncation point. last_complete={last_complete}",
					"Statement Importer - No Recovery Point"
				)

		# Log detailed error
		frappe.log_error(
			message=f"Failed to parse AI response as JSON\n\n"
					f"Parse Error: {e!s}\n\n"
					f"Raw Response ({len(response)} chars):\n{response}\n\n"
					f"Cleaned Response ({len(cleaned)} chars):\n{cleaned}",
			title="Statement Importer - JSON Parse Error"
		)

		# User-friendly error message
		frappe.throw(
			_("AI returned invalid JSON format. This may happen with very large statements. Try processing a shorter date range or contact administrator."),
			title=_("AI Parsing Failed")
		)


def validate_account_exists(account_name, company):
	"""
	Check if account exists in Chart of Accounts

	Standard Frappe pattern: Database validation

	Args:
		account_name: Account name to check
		company: Company name

	Returns:
		bool: True if account exists, False otherwise
	"""
	if not account_name:
		return False

	# Check if account exists for this company
	exists = frappe.db.exists("Account", {"name": account_name, "company": company})
	return bool(exists)


def auto_correct_account_names(transactions, provider, company):
	"""
	Auto-correct AI-generated account names to match whitelist

	This is more reliable than trying to force AI to follow complex instructions.
	Let AI use natural language, then fix it in Python.

	Args:
		transactions: List of transactions with potentially wrong account names
		provider: Statement Provider document
		company: Company name

	Returns:
		list: Transactions with corrected account names
	"""
	allowed_accounts = get_allowed_account_names(provider, company)
	if not allowed_accounts:
		return transactions  # No rules configured, skip correction

	# Build German→English translation map
	german_to_english = {
		"Barmittel": "Cash",
		"Dividenden": "Dividend Income",
		"Provisionen": "Brokerage Fees",
		"Kommission": "Brokerage Fees",
		"Zinsen": "Interest Income",
		"Zinsertrag": "Interest Income",
		"Quellensteuer": "Brokerage Fees",
		"Transaktionsgebühren": "Brokerage Fees",
		"Sonstige Gebühren": "Brokerage Fees",
		"Wertpapiere": "Investments - Securities",
		"Sicherheiten": "Investments - Securities",
		"Sicherheitenwert": "Investments - Securities",
		"Einzahlung": "Bank - Transfer",
		"Auszahlung": "Bank - Transfer",
	}

	def find_best_match(account_name):
		"""
		Find best matching account from whitelist using confidence scoring
		FIX Issue #6 (v1.3.9): Improved matching with confidence scores

		Returns the BEST match (highest confidence) instead of first match

		Args:
			account_name: Account name to match (may be German or partial)

		Returns:
			tuple: (matched_account, confidence_score) or (None, 0) if no match
		"""
		if not account_name:
			return None, 0

		# Try exact match first (100% confidence)
		if account_name in allowed_accounts:
			return account_name, 1.0

		# Translate German words
		translated_name = account_name
		for german, english in german_to_english.items():
			if german in translated_name:
				translated_name = translated_name.replace(german, english)

		# Try exact match after translation (95% confidence)
		if translated_name in allowed_accounts:
			return translated_name, 0.95

		# Fuzzy matching with confidence scores
		account_lower = account_name.lower()
		best_match = None
		best_confidence = 0.0

		# Define matching rules with confidence scores
		matching_rules = [
			# (keywords, required_account_words, confidence)
			(["cash", "barmittel", "ib account"], ["Cash", "Interactive Brokers"], 0.85),
			(["dividend", "dividenden"], ["Dividend"], 0.90),
			(["commission", "fee", "provision", "gebühr"], ["Brokerage Fees"], 0.85),
			(["interest", "zins"], ["Interest"], 0.90),
			(["securities", "investment", "wertpapier", "sicherheit"], ["Securities", "Investments"], 0.80),
			(["transfer", "deposit", "withdrawal", "einzahlung", "auszahlung"], ["Transfer"], 0.75),
		]

		for keywords, required_words, confidence in matching_rules:
			# Check if any keyword matches
			if any(word in account_lower for word in keywords):
				# Find account with required words
				for acc in allowed_accounts:
					# Check if account contains all required words (OR logic for alternatives)
					if any(req_word in acc for req_word in required_words):
						# Calculate actual confidence based on keyword match quality
						# Exact keyword match = full confidence
						# Partial match = reduced confidence
						actual_confidence = confidence

						# Bonus for multiple keyword matches
						matches = sum(1 for kw in keywords if kw in account_lower)
						if matches > 1:
							actual_confidence = min(0.95, confidence + (matches * 0.05))

						# Update best match if this is better
						if actual_confidence > best_confidence:
							best_match = acc
							best_confidence = actual_confidence

		# Return best match found (or None if confidence too low)
		if best_match and best_confidence >= 0.70:  # Minimum 70% confidence threshold
			return best_match, best_confidence

		# No confident match found
		return None, 0

	corrected = []
	low_confidence_count = 0

	for txn in transactions:
		debit_orig = txn.get("account_debit")
		credit_orig = txn.get("account_credit")

		# Get best matches with confidence scores
		debit_corrected, debit_confidence = find_best_match(debit_orig)
		credit_corrected, credit_confidence = find_best_match(credit_orig)

		if debit_corrected and credit_corrected:
			# Apply corrections
			txn["account_debit"] = debit_corrected
			txn["account_credit"] = credit_corrected

			# Track low confidence corrections (70-80%)
			if debit_confidence < 0.80 or credit_confidence < 0.80:
				low_confidence_count += 1
				frappe.log_error(
					message=f"Low confidence auto-correction:\n"
							f"Debit: '{debit_orig}' → '{debit_corrected}' (confidence: {debit_confidence:.0%})\n"
							f"Credit: '{credit_orig}' → '{credit_corrected}' (confidence: {credit_confidence:.0%})\n"
							f"Transaction: {txn.get('description', 'No description')}\n"
							f"Please review this transaction for accuracy.",
					title="Statement Importer - Low Confidence Correction"
				)

			corrected.append(txn)
		else:
			# Log which accounts failed to match
			frappe.log_error(
				message=f"Could not auto-correct accounts:\n"
						f"Original Debit: '{debit_orig}' → {debit_corrected or 'NO MATCH'} (confidence: {debit_confidence:.0%})\n"
						f"Original Credit: '{credit_orig}' → {credit_corrected or 'NO MATCH'} (confidence: {credit_confidence:.0%})\n"
						f"Transaction: {txn.get('description', 'No description')}\n"
						f"Allowed accounts: {', '.join(sorted(allowed_accounts))}",
				title="Statement Importer - Auto-Correction Failed"
			)

	# Show summary message if there were low confidence corrections
	if low_confidence_count > 0:
		frappe.msgprint(
			_("{0} transaction(s) had low-confidence account mappings. Please review the transactions in the Error Log and verify the accounts are correct before posting Journal Entries.").format(low_confidence_count),
			indicator="orange",
			title=_("Low Confidence Corrections")
		)

	return corrected


def validate_parsed_transactions(transactions, statement):
	"""
	Validate parsed transactions before saving

	Standard Frappe pattern: Validation with helpful errors

	Args:
		transactions: List of transaction dicts
		statement: Statement Import document

	Returns:
		list: Validated transactions
	"""
	from frappe.utils import getdate

	# AUTO-CORRECT account names first
	provider = frappe.get_doc("Statement Provider", statement.statement_provider)
	transactions = auto_correct_account_names(transactions, provider, statement.company)

	validated = []

	for idx, txn in enumerate(transactions, start=1):
		# Validate required fields
		if not txn.get("date"):
			frappe.msgprint(_("Transaction {0}: Missing date, skipping").format(idx))
			continue

		if not txn.get("description"):
			txn["description"] = f"Transaction {idx}"

		# Validate amounts
		debit_amount = frappe.utils.flt(txn.get("debit_amount", 0))
		credit_amount = frappe.utils.flt(txn.get("credit_amount", 0))

		if debit_amount <= 0 or credit_amount <= 0:
			frappe.msgprint(_("Transaction {0}: Invalid amounts (must be positive), skipping").format(idx))
			continue

		# Reject unbalanced transactions (accounting requirement)
		if abs(debit_amount - credit_amount) > 0.01:
			frappe.msgprint(
				_("Transaction {0}: Unbalanced transaction (Debit: {1}, Credit: {2}). Skipping - all transactions must balance.").format(
					idx, debit_amount, credit_amount
				),
				indicator="red"
			)
			continue

		# Validate date format
		try:
			txn["date"] = getdate(txn["date"])
		except Exception:
			# FIX Issue #1 (v1.3.8): No fallback - skip transaction with invalid date
			# Standard Frappe pattern: Fail gracefully, don't use arbitrary defaults
			frappe.msgprint(
				_("Transaction {0}: Invalid date format, skipping. AI must provide valid dates.").format(idx),
				indicator="red"
			)
			continue

		# Validate required fields from AI (no hardcoded fallbacks per standards)
		if not txn.get("currency"):
			frappe.msgprint(
				_("Transaction {0}: Missing currency, skipping. AI must provide currency.").format(idx),
				indicator="red"
			)
			continue

		if not txn.get("account_debit"):
			frappe.msgprint(
				_("Transaction {0}: Missing debit account, skipping. AI must provide account mapping.").format(idx),
				indicator="red"
			)
			continue

		if not txn.get("account_credit"):
			frappe.msgprint(
				_("Transaction {0}: Missing credit account, skipping. AI must provide account mapping.").format(idx),
				indicator="red"
			)
			continue

		# NOTE: Whitelist validation removed - accounts are auto-corrected before this point
		# See auto_correct_account_names() function above

		# FEATURE: Validate that accounts exist in Chart of Accounts
		# This prevents journal entry creation failures later
		debit_account_exists = validate_account_exists(txn.get("account_debit"), statement.company)
		credit_account_exists = validate_account_exists(txn.get("account_credit"), statement.company)

		if not debit_account_exists:
			frappe.msgprint(
				_("Transaction {0}: Debit account '{1}' does not exist in Chart of Accounts for {2}. Please create it first or update the Statement Provider's accounting rules.").format(
					idx, txn.get("account_debit"), statement.company
				),
				indicator="red"
			)
			continue

		if not credit_account_exists:
			frappe.msgprint(
				_("Transaction {0}: Credit account '{1}' does not exist in Chart of Accounts for {2}. Please create it first or update the Statement Provider's accounting rules.").format(
					idx, txn.get("account_credit"), statement.company
				),
				indicator="red"
			)
			continue

		validated.append(txn)

	if not validated:
		frappe.throw(_("No valid transactions found in AI response"))

	return validated


@frappe.whitelist()
def create_journal_entries(statement_doc_name):
	"""
	Create Journal Entries from parsed transactions (Phase 3)

	Standard Frappe pattern:
	- Permission check
	- Validate transactions
	- Create JEs
	- Link to statement
	- Journal Validation app automatically validates (if installed)!

	Args:
		statement_doc_name: Name of Statement Import document

	Returns:
		dict: {
			"success": bool,
			"journal_entries_created": int,
			"transactions_posted": int,
			"journal_entry_names": list,
			"errors": list
		}
	"""
	# Permission check (standard pattern)
	if not frappe.has_permission("Statement Import", "write"):
		frappe.throw(_("No permission to create journal entries"))

	try:
		# Load Statement Import document
		statement = frappe.get_doc("Statement Import", statement_doc_name)

		# Validate prerequisites
		if not statement.transactions or len(statement.transactions) == 0:
			frappe.throw(_("No transactions found to create Journal Entries"))

		if not statement.company:
			frappe.throw(_("Company is required to create Journal Entries"))

		# Track results
		results = {
			"success": True,
			"journal_entries_created": 0,
			"transactions_posted": 0,
			"transactions_attempted": 0,
			"journal_entry_names": [],
			"errors": []
		}

		# Process each transaction
		for txn in statement.transactions:
			# FIX Issue #3 (v1.3.7): Enhanced status consistency checks
			# Check for already posted transactions
			if txn.status == "Posted":
				# Check for inconsistent state (Posted but no JE reference)
				if not txn.journal_entry:
					frappe.log_error(
						message=f"Transaction '{txn.description or 'Unnamed'}' has status 'Posted' but no journal_entry reference. Data inconsistency detected.",
						title="Statement Importer - Data Inconsistency"
					)
					results["errors"].append({
						"transaction": txn.description[:50] if txn.description else "Unnamed",
						"error": _("Inconsistent state: marked as Posted but no Journal Entry found")
					})
				continue  # Skip regardless

			# Check for orphaned journal entries (JE exists but status not Posted)
			if txn.journal_entry and txn.status != "Posted":
				frappe.msgprint(
					_("Transaction '{0}' has Journal Entry '{1}' but status is '{2}'. Skipping to prevent duplicate.").format(
						txn.description[:50] if txn.description else "Unnamed",
						txn.journal_entry,
						txn.status
					),
					indicator="orange"
				)
				continue

			# FIX Issue #4 (v1.3.7): Skip Error status silently (already failed)
			if txn.status == "Error":
				continue

			# Only process Validated or Pending transactions
			if txn.status not in ["Validated", "Pending"]:
				txn_desc = txn.description[:50] if txn.description else "Unnamed"
				results["errors"].append({
					"transaction": txn_desc,
					"error": _("Transaction status must be Validated or Pending (current: {0})").format(txn.status)
				})
				continue

			# Count attempted transactions
			results["transactions_attempted"] += 1

			try:
				# Create Journal Entry for this transaction
				je = create_journal_entry_from_transaction(txn, statement)

				# Link JE to transaction
				txn.journal_entry = je.name
				txn.status = "Posted"
				txn.error_message = None  # Clear any previous errors

				# Track success
				results["journal_entries_created"] += 1
				results["transactions_posted"] += 1
				results["journal_entry_names"].append(je.name)

			except Exception as e:
				# FIX Bug #3: Update transaction status and error message
				error_msg = str(e)
				txn.status = "Error"
				txn.error_message = error_msg

				# FIX Bug #4: Safe None handling
				txn_desc = txn.description[:50] if txn.description else "Unnamed"
				results["errors"].append({
					"transaction": txn_desc,
					"error": error_msg
				})

				frappe.log_error(
					message=f"Failed to create JE for transaction: {txn.description or 'Unnamed'}\n{error_msg}\n{frappe.get_traceback()}",
					title="Statement Import - JE Creation Error"
				)

		# Save statement with updated transactions
		statement.save()
		# FIX Bug #2: Remove manual commit - Frappe handles this automatically
		# frappe.db.commit()  # Removed - violates Frappe pattern

		# Show summary message
		if results["journal_entries_created"] > 0:
			# FIX Bug #5: Use attempted count, not total count
			frappe.msgprint(
				_("Successfully created {0} Journal Entries from {1} attempted transactions").format(
					results["journal_entries_created"],
					results["transactions_attempted"]
				),
				title=_("Journal Entries Created"),
				indicator="green"
			)

		if results["errors"]:
			# FIX Issue #3: Make error summary translatable
			error_summary = "<br>".join([
				_("• {0}: {1}").format(err['transaction'], err['error'])
				for err in results["errors"][:5]  # Show first 5 errors
			])
			frappe.msgprint(
				_("Some transactions failed:<br>{0}").format(error_summary),
				title=_("Partial Success"),
				indicator="orange"
			)

		return results

	except Exception as e:
		# Log error
		frappe.log_error(
			message=f"Error creating journal entries: {e!s}\n{frappe.get_traceback()}",
			title="Statement Import - JE Creation Error"
		)
		# FIX Issue #2: Don't expose raw exception to users
		frappe.throw(
			_("Failed to create Journal Entries. Please check the Error Log for details or contact administrator."),
			title=_("Journal Entry Creation Failed")
		)


def create_journal_entry_from_transaction(txn, statement):
	"""
	Create a Journal Entry from a single transaction

	Standard Frappe pattern:
	- Create JE document
	- Add accounting entries (debit and credit)
	- Set reference to Statement Import
	- Save (validation happens automatically)

	Args:
		txn: Statement Transaction Line (child table row)
		statement: Statement Import document (parent)

	Returns:
		Journal Entry document (saved but not submitted)
	"""
	# Validate required fields
	if not txn.account_debit:
		frappe.throw(
			_("Transaction '{0}': Debit account is required").format(txn.description[:50] if txn.description else "Unnamed")
		)

	if not txn.account_credit:
		frappe.throw(
			_("Transaction '{0}': Credit account is required").format(txn.description[:50] if txn.description else "Unnamed")
		)

	# FIX Bug #6: Enhanced account validation
	# Validate debit account
	debit_account = frappe.db.get_value(
		"Account",
		txn.account_debit,
		["name", "is_group", "company", "disabled"],
		as_dict=True
	)

	if not debit_account:
		frappe.throw(
			_("Debit account '{0}' does not exist in the Chart of Accounts").format(txn.account_debit)
		)

	if debit_account.is_group:
		frappe.throw(
			_("Debit account '{0}' is a Group account. Please use a ledger account (non-group) for transactions.").format(txn.account_debit)
		)

	if debit_account.company != statement.company:
		frappe.throw(
			_("Debit account '{0}' does not belong to company '{1}'. It belongs to '{2}'.").format(
				txn.account_debit,
				statement.company,
				debit_account.company
			)
		)

	if debit_account.disabled:
		frappe.throw(
			_("Debit account '{0}' is disabled and cannot be used in transactions").format(txn.account_debit)
		)

	# Validate credit account
	credit_account = frappe.db.get_value(
		"Account",
		txn.account_credit,
		["name", "is_group", "company", "disabled"],
		as_dict=True
	)

	if not credit_account:
		frappe.throw(
			_("Credit account '{0}' does not exist in the Chart of Accounts").format(txn.account_credit)
		)

	if credit_account.is_group:
		frappe.throw(
			_("Credit account '{0}' is a Group account. Please use a ledger account (non-group) for transactions.").format(txn.account_credit)
		)

	if credit_account.company != statement.company:
		frappe.throw(
			_("Credit account '{0}' does not belong to company '{1}'. It belongs to '{2}'.").format(
				txn.account_credit,
				statement.company,
				credit_account.company
			)
		)

	if credit_account.disabled:
		frappe.throw(
			_("Credit account '{0}' is disabled and cannot be used in transactions").format(txn.account_credit)
		)

	# Validate amounts
	debit_amount = frappe.utils.flt(txn.debit_amount)
	credit_amount = frappe.utils.flt(txn.credit_amount)

	if debit_amount <= 0:
		frappe.throw(
			_("Transaction '{0}': Debit amount must be greater than zero").format(txn.description[:50] if txn.description else "Unnamed")
		)

	if credit_amount <= 0:
		frappe.throw(
			_("Transaction '{0}': Credit amount must be greater than zero").format(txn.description[:50] if txn.description else "Unnamed")
		)

	# Check balanced (within tolerance)
	if abs(debit_amount - credit_amount) > 0.01:
		frappe.throw(
			_("Transaction '{0}': Debit and credit amounts must be equal (Debit: {1}, Credit: {2})").format(
				txn.description[:50] if txn.description else "Unnamed",
				debit_amount,
				credit_amount
			)
		)

	# FIX Issue #2 (v1.3.8): Validate transaction_date exists (no fallback)
	# Standard Frappe pattern: Validate required fields before use
	if not txn.transaction_date:
		frappe.throw(
			_("Transaction '{0}': Missing transaction date. This should not happen - validation should have set it.").format(
				txn.description[:50] if txn.description else "Unnamed"
			),
			title=_("Data Integrity Error")
		)

	# Create Journal Entry document
	je = frappe.get_doc({
		"doctype": "Journal Entry",
		"voucher_type": "Journal Entry",
		"company": statement.company,
		"posting_date": txn.transaction_date,  # FIX Issue #2 (v1.3.8): No fallback
		"user_remark": txn.description,  # FIX Issue #3 (v1.3.8): No fallback (validation sets it)
		"accounts": [
			{
				# Debit entry
				"account": txn.account_debit,
				"debit_in_account_currency": debit_amount,
				"credit_in_account_currency": 0,
				"user_remark": txn.description  # FIX Issue #3 (v1.3.8): No fallback
			},
			{
				# Credit entry
				"account": txn.account_credit,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": credit_amount,
				"user_remark": txn.description  # FIX Issue #3 (v1.3.8): No fallback
			}
		]
	})

	# Save JE (this triggers validation and Journal Validation hooks if installed)
	je.insert()

	# Add reference back to Statement Import in remarks for audit trail
	je.add_comment(
		"Comment",
		_("Created from Statement Import: {0}, Transaction: {1}").format(
			statement.name,
			txn.description[:100] if txn.description else "Unnamed"
		)
	)

	return je
