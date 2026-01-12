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
		max_size = 50 * 1024 * 1024  # 50 MB limit

		if file_size > max_size:
			frappe.throw(
				_("PDF file is too large ({0:.2f} MB). Maximum allowed size is {1} MB. Please use a smaller file.").format(
					file_size / (1024 * 1024),
					max_size / (1024 * 1024)
				),
				title=_("File Too Large")
			)

		# Extract data using pdfplumber
		extracted_data = extract_pdf_data(file_path)

		# Update statement with preview
		statement.preview_data = format_preview_html(extracted_data)
		statement.save()
		# FIX Issue #1: Remove manual commit - Frappe handles this automatically

		return {
			"success": True,
			"text_preview": extracted_data["text"][:1000],  # First 1000 chars
			"tables_found": len(extracted_data["tables"]),
			"tables_preview": extracted_data["tables"][:3]  # First 3 tables
		}

	except Exception as e:
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

		# Check if PDF has been extracted
		if not statement.preview_data:
			frappe.throw(_("Please extract PDF data first before parsing transactions"))

		# FIX Issue #1 (v1.3.7): Atomic status update to prevent race condition
		#
		# CRITICAL: We MUST use raw SQL here (standard Frappe pattern for atomic operations)
		#
		# Why we can't use ORM:
		# 1. frappe.db.set_value() - Doesn't support conditional WHERE (race condition remains)
		# 2. doc.reload() + check + doc.save() - Race condition window between check and save
		# 3. Frappe doesn't provide row-level locking API
		#
		# This is the ONLY way to atomically check current status AND update it in one operation,
		# preventing concurrent requests from processing the same document simultaneously.
		#
		# Similar patterns used in Frappe/ERPNext core for atomic operations.
		# Query is safe: Uses parameterized query (%(name)s), no SQL injection risk
		affected = frappe.db.sql("""
			UPDATE `tabStatement Import`
			SET status = 'Processing'
			WHERE name = %(name)s
			AND status IN ('Draft', 'Completed', 'Failed')
		""", {"name": statement_doc_name})

		# Check if update succeeded (means we got the lock)
		if not affected:
			# Reload to get current status
			statement.reload()
			if statement.status == "Processing":
				frappe.throw(
					_("This statement is already being processed. Please wait for the current operation to complete."),
					title=_("Processing In Progress")
				)
			else:
				# Status is something unexpected
				frappe.throw(
					_("Cannot process statement with status '{0}'. Please reset to Draft, Completed, or Failed.").format(statement.status),
					title=_("Invalid Status")
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
		# FIX Issue #1: Remove manual commit - Frappe handles this automatically

		return {
			"success": True,
			"transactions_parsed": len(transactions),
			"transactions": transactions
		}

	except Exception as e:
		# Update status to failed
		try:
			statement.status = "Failed"
			statement.error_log = f"AI Parsing Error: {e!s}"
			statement.save()
			# FIX Issue #1: Remove manual commit - Frappe handles this automatically
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

	# Handle empty response
	if not response or not response.strip():
		frappe.throw(_("AI returned empty response. Please check AI Provider configuration."))

	# Parse JSON response (same pattern as journal_validation/ai_helper.py)
	transactions = parse_ai_response(response)

	# Validate transactions
	validated_transactions = validate_parsed_transactions(transactions, statement)

	return validated_transactions


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

	# Build prompt from template
	return build_prompt_from_template(provider.prompt_template, extracted_data, statement)


def build_prompt_from_template(template, extracted_data, statement):
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

	Args:
		template: Prompt template string
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

	# Build placeholder values (no fallback values - fail if missing)
	placeholders = {
		"company": statement.company,
		"statement_period": statement.statement_period or _("Not specified"),
		"import_date": str(statement.import_date) if statement.import_date else str(frappe.utils.today()),
		"text": extracted_data['text'][:3000],  # First 3000 chars
		"tables": tables_text,
		"provider": statement.statement_provider
	}

	# Replace placeholders in template
	prompt = template
	for key, value in placeholders.items():
		placeholder = "{" + key + "}"
		prompt = prompt.replace(placeholder, str(value))

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
			if hasattr(e, 'pos') and e.pos:
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
