# Noreli North Brokerage Statement Importer - API Documentation

**Version 1.2.0**
**Last Updated:** January 11, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Whitelisted API Methods](#whitelisted-api-methods)
4. [Helper Functions](#helper-functions)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)

---

## Overview

Statement Importer exposes three whitelisted API methods for PDF processing and transaction parsing. All methods follow standard Frappe patterns with proper permission checks and error handling.

### Base Module

```python
statement_importer.statement_importer.api
```

### Dependencies

- `frappe` - Frappe framework
- `pdfplumber` - PDF text/table extraction
- `norelinorth_ai_assistant.ai_assistant.api` - AI parsing (optional)

---

## Authentication & Authorization

### Permission Model

All whitelisted methods check permissions before execution:

```python
if not frappe.has_permission("Statement Import", "write"):
    frappe.throw(_("No permission to process statements"))
```

### Required Roles

| Method | Required Permission | Recommended Roles |
|--------|-------------------|------------------|
| `extract_pdf_preview()` | Statement Import (write) | Accounts Manager, Accounts User |
| `parse_transactions_with_ai()` | Statement Import (write) | Accounts Manager, Accounts User |
| `create_journal_entries()` | Statement Import (write) | Accounts Manager |

### Session Authentication

All API calls must be made with a valid Frappe session (cookie-based) or API key.

**Client-side (in DocType JS):**
```javascript
frappe.call({
    method: 'statement_importer.statement_importer.api.extract_pdf_preview',
    args: {
        statement_doc_name: frm.doc.name
    },
    callback: function(r) {
        // Handle response
    }
});
```

**Server-side (Python):**
```python
import frappe
from statement_importer.statement_importer.api import extract_pdf_preview

result = extract_pdf_preview("SI-2025-00001")
```

---

## Whitelisted API Methods

### 1. extract_pdf_preview()

Extract text and tables from uploaded PDF and return preview HTML.

**Method Path:**
```python
statement_importer.statement_importer.api.extract_pdf_preview
```

**Decorator:**
```python
@frappe.whitelist()
```

**Signature:**
```python
def extract_pdf_preview(statement_doc_name: str) -> str
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `statement_doc_name` | str | ✅ Yes | Name of the Statement Import document |

**Returns:**

| Type | Description |
|------|-------------|
| `str` | HTML preview of extracted PDF data |

**Process Flow:**

1. Load Statement Import document
2. Check write permission
3. Validate PDF file is attached
4. Extract text and tables using `pdfplumber`
5. Store extracted data in `preview_data` field (JSON)
6. Generate HTML preview
7. Save document
8. Return HTML for display

**Error Conditions:**

| Error | Condition | HTTP Status |
|-------|-----------|-------------|
| `frappe.PermissionError` | User lacks write permission | 403 |
| `frappe.ValidationError` | No PDF file attached | 400 |
| `frappe.ValidationError` | PDF file not found on disk | 400 |
| `frappe.ValidationError` | PDF file is empty/corrupted | 400 |
| `Exception` | PDF extraction fails | 500 |

**Example Usage:**

```python
import frappe

# Get document name
doc_name = "SI-2025-00001"

# Extract PDF preview
html = frappe.call(
    'statement_importer.statement_importer.api.extract_pdf_preview',
    statement_doc_name=doc_name
)

# Display in dialog
frappe.msgprint(html)
```

**Client-side (JavaScript):**

```javascript
frappe.call({
    method: 'statement_importer.statement_importer.api.extract_pdf_preview',
    args: {
        statement_doc_name: 'SI-2025-00001'
    },
    callback: function(r) {
        if (r.message) {
            // Show HTML in dialog
            let d = new frappe.ui.Dialog({
                title: 'PDF Preview',
                fields: [{
                    fieldtype: 'HTML',
                    options: r.message
                }]
            });
            d.show();
        }
    },
    error: function(r) {
        frappe.msgprint(__('Failed to extract PDF: {0}', [r.message]));
    }
});
```

**Preview HTML Format:**

```html
<h3>PDF Extraction Preview</h3>
<p><strong>File:</strong> statement.pdf (125.4 KB)</p>
<p><strong>Pages:</strong> 15</p>
<p><strong>Tables Found:</strong> 3</p>

<h4>Text Content (first 2000 characters):</h4>
<pre style='background: #f5f5f5; padding: 10px; white-space: pre-wrap;'>
[Extracted text...]
</pre>

<h4>Tables:</h4>
<table class='table table-bordered'>
[Extracted tables...]
</table>
```

---

### 2. parse_transactions_with_ai()

Parse transactions from PDF using AI with provider-specific prompts.

**Method Path:**
```python
statement_importer.statement_importer.api.parse_transactions_with_ai
```

**Decorator:**
```python
@frappe.whitelist()
```

**Signature:**
```python
def parse_transactions_with_ai(statement_doc_name: str) -> dict
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `statement_doc_name` | str | ✅ Yes | Name of the Statement Import document |

**Returns:**

| Type | Description |
|------|-------------|
| `dict` | Result dictionary with transactions and statistics |

**Return Structure:**

```python
{
    "success": True,
    "transactions_parsed": 25,
    "valid_transactions": 23,
    "invalid_transactions": 2,
    "message": "Successfully parsed 23 transactions"
}
```

**Process Flow:**

1. Load Statement Import document
2. Check write permission
3. Validate prerequisites:
   - Company is set
   - Statement Provider is selected
   - Preview data exists (PDF extracted)
   - Statement Provider is enabled
   - Statement Provider has prompt template
4. Build AI parsing prompt using provider template
5. Call AI Assistant to parse transactions
6. Validate AI response JSON
7. Validate each transaction (dates, amounts, balancing)
8. Clear existing transactions and add validated ones
9. Update transactions_found counter
10. Save document
11. Return summary statistics

**Error Conditions:**

| Error | Condition | HTTP Status |
|-------|-----------|-------------|
| `frappe.PermissionError` | User lacks write permission | 403 |
| `frappe.ValidationError` | Company not set | 400 |
| `frappe.ValidationError` | No statement provider selected | 400 |
| `frappe.ValidationError` | PDF not extracted yet | 400 |
| `frappe.ValidationError` | Provider not enabled | 400 |
| `frappe.ValidationError` | Provider has no prompt template | 400 |
| `frappe.ValidationError` | AI Assistant not installed | 400 |
| `frappe.ValidationError` | AI returned empty response | 400 |
| `frappe.ValidationError` | Invalid JSON response from AI | 400 |
| `frappe.ValidationError` | No valid transactions found | 400 |

**Example Usage:**

```python
import frappe

# Parse transactions
result = frappe.call(
    'statement_importer.statement_importer.api.parse_transactions_with_ai',
    statement_doc_name='SI-2025-00001'
)

print(f"Parsed {result['transactions_parsed']} transactions")
print(f"Valid: {result['valid_transactions']}")
print(f"Invalid: {result['invalid_transactions']}")
```

**Client-side (JavaScript):**

```javascript
frappe.call({
    method: 'statement_importer.statement_importer.api.parse_transactions_with_ai',
    args: {
        statement_doc_name: frm.doc.name
    },
    freeze: true,
    freeze_message: __('Parsing transactions with AI...'),
    callback: function(r) {
        if (r.message && r.message.success) {
            frappe.msgprint({
                title: __('Success'),
                indicator: 'green',
                message: __(r.message.message)
            });
            frm.reload_doc();
        }
    },
    error: function(r) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('AI parsing failed: {0}', [r.message])
        });
    }
});
```

**Transaction Validation Rules:**

```python
# Valid transaction requirements:
{
    "date": "YYYY-MM-DD",              # Required, valid date format
    "description": "string",           # Required, non-empty
    "currency": "USD",                 # Required, 3-letter code
    "account_debit": "account name",   # Required
    "debit_amount": 1000.00,          # Required, > 0
    "account_credit": "account name",  # Required
    "credit_amount": 1000.00          # Required, > 0, must equal debit
}
```

---

### 3. create_journal_entries()

Create Journal Entries from validated transactions (Phase 3 - placeholder).

**Method Path:**
```python
statement_importer.statement_importer.api.create_journal_entries
```

**Decorator:**
```python
@frappe.whitelist()
```

**Signature:**
```python
def create_journal_entries(statement_doc_name: str) -> dict
```

**Status:** 🔲 **Not Implemented** (Placeholder for Phase 3)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `statement_doc_name` | str | ✅ Yes | Name of the Statement Import document |

**Current Behavior:**

Throws error message:
```python
frappe.throw(_("Journal Entry creation not yet implemented. This will be added in Phase 3."))
```

**Planned Implementation (Phase 3):**

Will create Journal Entries for all validated transactions with status "Validated".

---

## Helper Functions

### check_ai_enabled()

Check if AI Assistant app is installed and functional.

**Method Path:**
```python
statement_importer.statement_importer.api.check_ai_enabled
```

**Decorator:**
```python
@frappe.whitelist()
```

**Signature:**
```python
def check_ai_enabled() -> bool
```

**Returns:**

| Type | Description |
|------|-------------|
| `bool` | `True` if AI Assistant is available, `False` otherwise |

**Example Usage:**

```python
import frappe

if frappe.call('statement_importer.statement_importer.api.check_ai_enabled'):
    print("AI parsing is available")
else:
    print("AI parsing not available - install norelinorth_ai_assistant app")
```

---

### build_parsing_prompt()

Build AI parsing prompt using provider template (Internal use).

**Signature:**
```python
def build_parsing_prompt(extracted_data: dict, doc: object) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `extracted_data` | dict | PDF extraction data (text, tables, page_count) |
| `doc` | Document | Statement Import document |

**Returns:**

| Type | Description |
|------|-------------|
| `str` | Formatted prompt for AI parsing |

**Template Placeholders:**

| Placeholder | Replaced With |
|------------|---------------|
| `{text}` | Extracted PDF text |
| `{tables}` | Extracted tables (JSON) |
| `{company}` | Company name |
| `{statement_period}` | Statement period |

**Example Template:**

```text
You are parsing a {provider_name} statement for {company} for period {statement_period}.

Extracted Text:
{text}

Extracted Tables:
{tables}

Extract all transactions and return as JSON array...
```

---

### validate_parsed_transactions()

Validate AI response and filter valid transactions (Internal use).

**Signature:**
```python
def validate_parsed_transactions(transactions: list, doc: object) -> list
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `transactions` | list | List of transaction dicts from AI |
| `doc` | Document | Statement Import document |

**Returns:**

| Type | Description |
|------|-------------|
| `list` | List of validated transactions |

**Validation Checks:**

1. **Date Validation:** Must be valid date in YYYY-MM-DD format
2. **Amount Validation:** Must be positive numbers
3. **Balance Validation:** Debit must equal credit (within 0.01)
4. **Required Fields:** date, description, currency, accounts, amounts

**Invalid Transactions:**

Logged as warnings via `frappe.msgprint()` but not included in output.

---

### parse_ai_response()

Parse JSON response from AI (Internal use).

**Signature:**
```python
def parse_ai_response(ai_response: str) -> list
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `ai_response` | str | JSON string from AI |

**Returns:**

| Type | Description |
|------|-------------|
| `list` | Parsed transaction list |

**Error Handling:**

- Removes markdown code fences if present (```json...```)
- Handles JSON parsing errors gracefully
- Validates response is a list

---

## Error Handling

### Error Logging

All errors are logged to Frappe Error Log:

```python
frappe.log_error(
    message=f"Detailed error: {str(e)}\n{frappe.get_traceback()}",
    title="Statement Import - PDF Extraction Error"
)
```

### User-Friendly Messages

Errors shown to users are translated and helpful:

```python
frappe.throw(_("PDF file appears to be empty or corrupted. No pages found."))
```

### Error Response Format

```python
{
    "exc_type": "ValidationError",
    "exception": "Error message here",
    "_server_messages": "[{\"message\": \"User-friendly error\"}]"
}
```

---

## Code Examples

### Complete Workflow Example

```python
import frappe

def process_statement(doc_name):
    """
    Complete workflow: Extract PDF → Parse with AI → Review
    """
    try:
        # Step 1: Extract PDF
        print("Extracting PDF...")
        html = frappe.call(
            'statement_importer.statement_importer.api.extract_pdf_preview',
            statement_doc_name=doc_name
        )
        print(f"✅ Extracted {len(html)} chars of preview")

        # Step 2: Parse with AI
        print("Parsing with AI...")
        result = frappe.call(
            'statement_importer.statement_importer.api.parse_transactions_with_ai',
            statement_doc_name=doc_name
        )
        print(f"✅ Parsed {result['transactions_parsed']} transactions")
        print(f"   Valid: {result['valid_transactions']}")
        print(f"   Invalid: {result['invalid_transactions']}")

        # Step 3: Review document
        doc = frappe.get_doc("Statement Import", doc_name)
        print(f"\n📊 Final Summary:")
        print(f"   Company: {doc.company}")
        print(f"   Provider: {doc.statement_provider}")
        print(f"   Period: {doc.statement_period}")
        print(f"   Transactions: {doc.transactions_found}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.log_error(str(e), "Statement Processing Error")
        return False

# Usage
process_statement("SI-2025-00001")
```

### Batch Processing Example

```python
import frappe

def batch_process_statements(date_from, date_to):
    """
    Process all statements in a date range
    """
    statements = frappe.get_all(
        "Statement Import",
        filters={
            "import_date": ["between", [date_from, date_to]],
            "docstatus": 0,  # Draft
            "transactions_found": 0  # Not processed yet
        },
        fields=["name", "company", "statement_provider"]
    )

    results = {
        "success": 0,
        "failed": 0,
        "errors": []
    }

    for stmt in statements:
        try:
            # Extract and parse
            frappe.call('statement_importer.statement_importer.api.extract_pdf_preview',
                       statement_doc_name=stmt.name)

            result = frappe.call('statement_importer.statement_importer.api.parse_transactions_with_ai',
                               statement_doc_name=stmt.name)

            results["success"] += 1
            print(f"✅ {stmt.name}: {result['transactions_parsed']} transactions")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "document": stmt.name,
                "error": str(e)
            })
            print(f"❌ {stmt.name}: {str(e)}")

    return results

# Usage
results = batch_process_statements("2025-01-01", "2025-01-31")
print(f"Success: {results['success']}, Failed: {results['failed']}")
```

---

## Best Practices

### 1. Always Check Permissions

```python
# Before calling API
if not frappe.has_permission("Statement Import", "write"):
    frappe.msgprint("You don't have permission to process statements")
    return
```

### 2. Use Error Handling

```python
try:
    result = frappe.call('statement_importer.statement_importer.api.parse_transactions_with_ai',
                        statement_doc_name=doc_name)
except frappe.PermissionError:
    frappe.msgprint("Permission denied")
except frappe.ValidationError as e:
    frappe.msgprint(f"Validation error: {str(e)}")
except Exception as e:
    frappe.log_error(str(e), "Statement Processing Error")
    frappe.msgprint("An error occurred. Please contact administrator.")
```

### 3. Validate Prerequisites

```python
# Before AI parsing
doc = frappe.get_doc("Statement Import", doc_name)

if not doc.company:
    frappe.throw("Company is required")

if not doc.statement_provider:
    frappe.throw("Please select a Statement Provider")

if not doc.preview_data:
    frappe.throw("Please extract PDF data first")
```

### 4. Use Freeze for Long Operations

```javascript
// Show loading indicator during AI parsing
frappe.call({
    method: 'statement_importer.statement_importer.api.parse_transactions_with_ai',
    args: { statement_doc_name: frm.doc.name },
    freeze: true,
    freeze_message: __('Parsing transactions with AI... This may take up to 90 seconds.'),
    callback: function(r) {
        // Handle response
    }
});
```

### 5. Reload Document After API Calls

```javascript
// Reload to show updated transactions
frappe.call({
    method: 'statement_importer.statement_importer.api.parse_transactions_with_ai',
    args: { statement_doc_name: frm.doc.name },
    callback: function(r) {
        if (r.message && r.message.success) {
            frm.reload_doc();  // ✅ Refresh to show new transactions
        }
    }
});
```

---

## API Version History

### Version 1.2.0 (Current)

- Added provider-based AI parsing
- Enhanced error messages
- Added transaction validation
- Improved permission checks

### Version 1.1.0

- Added `parse_transactions_with_ai()` method
- Added AI integration
- Added transaction validation

### Version 1.0.0

- Initial API release
- `extract_pdf_preview()` method
- Basic PDF extraction

---

## Support

For API questions or issues:

- **GitHub Issues:** https://github.com/norelinorth/statement_importer/issues
- **Discussions:** https://github.com/norelinorth/statement_importer/discussions
- **Email:** https://github.com/norelinorth/statement_importer/issues

---

**Document Version:** 1.0
**Last Updated:** January 11, 2025
**Maintained by:** Noreli North
