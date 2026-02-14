# Noreli North Brokerage Statement Importer - User Guide

**Version 1.2.0**
**Last Updated:** January 11, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Statement Import Workflow](#statement-import-workflow)
4. [Provider Configuration](#provider-configuration)
5. [Transaction Management](#transaction-management)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [FAQ](#faq)

---

## Introduction

Statement Importer automates the processing of brokerage PDF statements into ERPNext. It uses AI-powered parsing to extract transactions and prepare them for Journal Entry creation.

### What This App Does

- **Upload PDF Statements** from Interactive Brokers or custom providers
- **Extract Text & Tables** automatically using intelligent PDF parsing
- **Parse Transactions** using AI with provider-specific templates
- **Validate Transactions** ensuring all debits/credits balance correctly
- **Prepare for Journal Entry** (Phase 3 - coming soon)

### Who Should Use This

- **Accounting Teams** managing investment portfolios
- **Finance Managers** reconciling brokerage accounts
- **ERPNext Administrators** automating Journal Entry creation
- **Anyone** who needs to process brokerage statements regularly

---

## Getting Started

### Prerequisites

Before using Statement Importer, ensure you have:

1. **ERPNext v15.81.0+** installed
2. **Company** configured in ERPNext
3. **User Permission** to create Statement Import documents
4. **PDF Statements** from supported brokers
5. **(Optional) AI Assistant app** for AI-powered parsing

### Accessing the Module

1. Log in to ERPNext Desk
2. Navigate to **Statement Importer** workspace
   (Look for the module in the sidebar or use the awesome bar: `Ctrl+K` → type "Statement Importer")
3. Click **Statement Import** to see the list view

### User Roles Required

| Role | Access Level |
|------|-------------|
| **Accounts Manager** | Full access (create, edit, delete) |
| **Accounts User** | Read-only access |
| **System Manager** | Full access including settings |

---

## Statement Import Workflow

### Step 1: Create New Statement Import

1. Click **New** button in Statement Import list
2. Fill in required fields:
   - **Company:** Select the company receiving the statement
   - **Import Date:** Defaults to today (you can change if needed)
   - **Statement Period:** Enter period like "2025-01" or "2025-Q1"
   - **Statement Provider:** Select your brokerage (IB, Schwab, Fidelity, or custom)
3. Click **Save**

**Field Guide:**

- **Company** (Required): The ERPNext company that owns the brokerage account
- **Import Date**: Date you're processing the statement (for tracking purposes)
- **Statement Period**: The period covered by the statement (helps organize multiple statements)
- **Statement Provider**: Critical for AI parsing - each provider has different formats
- **Status**: Automatically set to "Draft" when created

### Step 2: Upload PDF Statement

1. In the Statement Import document, click **Attach** button (paperclip icon)
2. Select your PDF statement file
3. Wait for upload to complete
4. **Save** the document again

**Supported File Types:**
- ✅ PDF (.pdf) files only
- ❌ Scanned images (must be text-based PDFs)
- ❌ Password-protected PDFs (unlock before uploading)

**File Size Limits:**
- Recommended: Under 10 MB
- Maximum: 25 MB (configurable by administrator)

### Step 3: Extract PDF Data

1. Click **Actions** dropdown in top-right
2. Select **Extract PDF Data**
3. Wait for processing (usually 5-30 seconds)
4. Review the preview HTML that appears

**What Gets Extracted:**

- **Text Content:** All text from every page
- **Tables:** Structured data (transactions, holdings, balances)
- **Page Count:** Number of pages processed
- **Metadata:** File size, processing date

**Preview Includes:**

- First 2000 characters of extracted text
- All tables found (in structured format)
- Summary statistics (pages, tables found)

**⚠️ Warning Signs:**

- If preview shows "No text content extracted" → Your PDF may be scanned/image-based
- If tables look garbled → PDF may have complex formatting
- If fewer pages than expected → PDF may be corrupted

### Step 4: Parse Transactions with AI

**Prerequisites for AI Parsing:**

1. AI Assistant app must be installed
2. AI Provider must be configured with API keys
3. Statement Provider must be selected on the document

**Steps:**

1. After extracting PDF data, click **Actions** → **Parse with AI**
2. Wait for AI processing (30-90 seconds typically)
3. A dialog will show parsing progress
4. Review the parsed transactions that appear in the **Transactions** table

**What AI Does:**

The AI analyzes your PDF using the provider-specific template and:

- Identifies transaction types (buy, sell, dividend, interest, fee, transfer)
- Extracts dates, descriptions, amounts
- Determines proper debit/credit accounts
- Validates all transactions balance
- Flags any errors or warnings

**Transaction Fields Populated:**

| Field | Description | Example |
|-------|-------------|---------|
| **Transaction Date** | Date the transaction occurred | 2025-01-15 |
| **Description** | What happened | "Bought 100 shares AAPL @ $150.00" |
| **Currency** | Transaction currency | USD |
| **Account Debit** | Account to debit | "Investment - Brokerage Account" |
| **Debit Amount** | Amount to debit | 15,000.00 |
| **Account Credit** | Account to credit | "Cash - Brokerage Account" |
| **Credit Amount** | Amount to credit | 15,000.00 |
| **Status** | Transaction status | Pending |

### Step 5: Review & Validate Transactions

After AI parsing, carefully review each transaction:

**Validation Checklist:**

- [ ] All dates are correct
- [ ] Descriptions are clear and accurate
- [ ] Debit/credit accounts are appropriate
- [ ] Amounts match the PDF statement
- [ ] Each transaction balances (debit = credit)
- [ ] Currency is correct
- [ ] No duplicate transactions

**Editing Transactions:**

1. Click **Edit** in the transaction table row
2. Modify any field as needed
3. Ensure debit still equals credit after changes
4. Save the parent document

**Deleting Transactions:**

1. Click the **X** button on the transaction row
2. Confirm deletion
3. Save the document

**Adding Manual Transactions:**

1. Click **Add Row** in the Transactions table
2. Fill in all required fields
3. Ensure debit = credit
4. Save the document

### Step 6: Finalize & Prepare for Journal Entry

Once all transactions are reviewed and validated:

1. Update transaction **Status** to "Validated" (optional)
2. Add any notes in the **Error Log** field (for audit trail)
3. Save the document
4. Status will update automatically based on progress

**Next Steps (Phase 3 - Coming Soon):**

- Click **Actions → Create Journal Entries**
- Journal Entries will be automatically generated
- Review and submit Journal Entries as needed

---

## Provider Configuration

### Understanding Statement Providers

Each brokerage formats statements differently. Statement Providers configure how the app processes each type of statement.

### Built-in Providers

The app comes with three pre-configured providers:

| Provider | Prompt Template | Accounting Rules |
|----------|----------------|------------------|
| **Interactive Brokers** | ✅ Included | 6 rules (buy/sell/dividend/interest/fee/transfer) |
| **Charles Schwab** | ✅ Included | 6 rules (buy/sell/dividend/interest/fee/transfer) |
| **Fidelity** | ✅ Included | 6 rules (buy/sell/dividend/interest/fee/transfer) |

### Viewing Provider Configuration

1. Navigate to **Statement Importer → Statement Provider**
2. Click on a provider name (e.g., "Interactive Brokers")
3. Review:
   - **Provider Name:** Display name
   - **Enabled:** Whether provider is active
   - **Prompt Template:** AI instructions for parsing
   - **Accounting Rules:** Transaction type mappings

### Customizing Providers

**⚠️ Administrator Access Required**

**To Customize Prompt Template:**

1. Open the Statement Provider document
2. Scroll to **Prompt Template** field
3. Edit the template using these placeholders:
   - `{text}` - Extracted PDF text
   - `{tables}` - Extracted tables
   - `{company}` - Company name
   - `{statement_period}` - Statement period
4. Save changes

**To Add/Edit Accounting Rules:**

1. Open the Statement Provider document
2. Scroll to **Accounting Rules** table
3. Add or edit rules:
   - **Transaction Type:** buy, sell, dividend, interest, fee, transfer, or other
   - **Account Debit:** Default debit account name (can use placeholders)
   - **Account Credit:** Default credit account name
   - **Description Pattern:** (Optional) Match specific descriptions
4. Save changes

### Creating Custom Providers

For unsupported brokerages:

1. Go to **Statement Provider** list
2. Click **New**
3. Enter:
   - **Provider Name:** e.g., "TD Ameritrade"
   - **Enabled:** Check to enable
   - **Prompt Template:** Copy from existing provider and modify
   - **Accounting Rules:** Add rules for transaction types
4. Save
5. Test with a sample PDF statement

---

## Transaction Management

### Transaction Statuses

| Status | Meaning | When to Use |
|--------|---------|-------------|
| **Pending** | Default status after AI parsing | Needs review |
| **Validated** | Manually reviewed and approved | Ready for Journal Entry |
| **Error** | Problem detected | Needs correction |
| **Posted** | Journal Entry created (Phase 3) | Completed |

### Manual Transaction Entry

If AI parsing fails or for manual adjustments:

1. Click **Add Row** in Transactions table
2. Fill in all fields manually
3. Ensure debit = credit
4. Set Status to "Pending" or "Validated"
5. Save document

### Bulk Editing Transactions

To edit multiple transactions:

1. Export to Excel (use List View export)
2. Edit in spreadsheet
3. Delete existing transactions
4. Import from Excel (use Data Import Tool)

### Transaction Validation Rules

**Automatic Validations:**

- ✅ **Date Required:** All transactions must have a date
- ✅ **Positive Amounts:** Debit and credit must be > 0
- ✅ **Balanced:** Debit amount must equal credit amount (within 0.01 tolerance)
- ✅ **Currency Required:** All transactions must specify currency
- ✅ **Description Required:** All transactions must have a description

**⚠️ Warnings (Non-blocking):**

- Missing account names (will be flagged)
- Unusual amount (very large or very small)
- Future dates (transaction date in future)

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "PDF file appears to be empty or corrupted"

**Cause:** PDF has no extractable pages

**Solutions:**
1. Verify PDF opens correctly in PDF reader
2. Check if PDF is password-protected (unlock first)
3. Try re-downloading PDF from broker
4. Check file size (0 bytes = corrupted)

#### Issue: "No text content extracted"

**Cause:** PDF is scanned image, not text-based

**Solutions:**
1. Verify PDF has selectable text (try to copy/paste text)
2. If scanned, use OCR tool to convert to text PDF
3. Request text-based PDF from broker

#### Issue: "AI Assistant app not properly installed"

**Cause:** AI Assistant app missing or not installed on site

**Solutions:**
```bash
# Install AI Assistant app
bench get-app https://github.com/norelinorth/norelinorth_ai_assistant.git
bench --site [your-site] install-app norelinorth_ai_assistant
bench restart
```

#### Issue: "No permission to process statements"

**Cause:** User lacks required permissions

**Solutions:**
1. Ask administrator to assign "Accounts Manager" or "Accounts User" role
2. Check DocType permissions (Statement Import → Read/Write)
3. Verify user is not restricted by user permissions

#### Issue: "AI returned empty response"

**Cause:** AI Provider not configured or API key invalid

**Solutions:**
1. Go to **AI Assistant → AI Provider**
2. Verify:
   - Provider is enabled
   - API key is valid
   - Default model is set
3. Test API connection
4. Check quota/credits with your AI provider

#### Issue: Transactions don't balance (debit ≠ credit)

**Cause:** AI parsing error or complex transaction

**Solutions:**
1. Manually review transaction in PDF
2. Edit debit or credit amount to balance
3. Split into multiple transactions if needed
4. Update accounting rules if pattern repeats

#### Issue: Wrong accounts assigned to transactions

**Cause:** Accounting rules not configured for transaction type

**Solutions:**
1. Edit transaction manually to correct accounts
2. Update **Statement Provider → Accounting Rules** for future statements
3. Consider creating custom provider for this broker

---

## Best Practices

### PDF Statement Preparation

1. **Download text-based PDFs** from broker (not scanned copies)
2. **Unlock password-protected PDFs** before uploading
3. **Use monthly statements** for easier processing
4. **Keep original PDFs** as backup in separate folder

### Processing Workflow

1. **Process statements chronologically** (oldest first)
2. **Review AI results immediately** while statement is fresh in mind
3. **Validate all transactions** before marking as Validated
4. **Document any manual changes** in Error Log field
5. **Create Journal Entries promptly** (when Phase 3 available)

### Account Setup

1. **Create dedicated accounts** for brokerage:
   - Cash - Brokerage Account
   - Investment - Brokerage Account
   - Income - Dividends
   - Income - Interest
   - Expense - Brokerage Fees
2. **Use consistent account names** across all statements
3. **Map accounts in provider rules** for automation

### Data Quality

1. **Verify statement period** matches actual PDF
2. **Check company selection** is correct
3. **Review transaction count** matches PDF
4. **Validate total amounts** against statement summary
5. **Document exceptions** for audit trail

### Security & Compliance

1. **Limit user access** to authorized accounting staff
2. **Use separate login** for sensitive statements
3. **Archive processed PDFs** securely
4. **Regular backups** of Statement Import documents
5. **Audit trail** via Error Log field

---

## FAQ

### General Questions

**Q: Which brokers are supported?**
A: Interactive Brokers, Charles Schwab, and Fidelity are pre-configured. You can add custom providers for any broker.

**Q: Do I need AI Assistant app?**
A: For Phase 2 (AI parsing), yes. Phase 1 (PDF extraction) works without it.

**Q: Can I process scanned PDF statements?**
A: No, PDFs must be text-based. Use OCR to convert scanned PDFs to text first.

**Q: How long does AI parsing take?**
A: Typically 30-90 seconds depending on statement size and AI provider.

**Q: Is my data sent to third parties?**
A: Only if you use AI parsing. The AI provider (OpenAI, Anthropic, etc.) will see your PDF content. Phase 1 extraction is 100% local.

### Technical Questions

**Q: What PDF libraries are used?**
A: pdfplumber for extraction (installed automatically).

**Q: Can I customize accounting rules?**
A: Yes, via Statement Provider → Accounting Rules table.

**Q: How do I handle multi-currency transactions?**
A: Currently single currency per transaction. Phase 3 will add multi-currency support.

**Q: Can I import multiple statements at once?**
A: Not yet. Batch processing planned for Phase 3.

**Q: How do I export transactions to Excel?**
A: Use ERPNext's standard List View export feature.

### Troubleshooting Questions

**Q: Why didn't AI find any transactions?**
A: Possible reasons: (1) Statement format not recognized, (2) Transactions in images not text, (3) Custom format needs provider configuration.

**Q: Can I re-run AI parsing?**
A: Yes, click **Actions → Parse with AI** again. Previous transactions will be replaced.

**Q: Why do I see duplicate transactions?**
A: AI may parse some sections twice. Delete duplicates manually before creating Journal Entries.

**Q: What if debit/credit don't balance?**
A: Edit the transaction to balance amounts, or split into multiple transactions.

---

## Getting Help

### Support Channels

- **GitHub Issues:** https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues
- **GitHub Discussions:** https://github.com/norelinorth/norelinorth_brokerage_statement_importer/discussions
- **Email Support:** https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues

### Reporting Bugs

Please include:
1. ERPNext version
2. Statement Importer version
3. Statement Provider used
4. Steps to reproduce
5. Error message (if any)
6. Sample PDF (sanitized/anonymized if possible)

### Feature Requests

Open an issue on GitHub with:
- Clear description of feature
- Business use case
- Expected behavior
- Any examples or mockups

---

## Appendix

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Awesome bar (search) |
| `Ctrl+G` | Go to list |
| `Ctrl+S` | Save document |
| `Ctrl+P` | Print/Export |

### Error Codes

| Code | Message | Solution |
|------|---------|----------|
| E001 | "PDF file appears to be empty" | Re-download PDF |
| E002 | "AI Assistant not installed" | Install AI app |
| E003 | "No permission to process" | Request Accounts Manager role |
| E004 | "Provider not configured" | Select Statement Provider |

---

**Document Version:** 1.0
**Last Updated:** January 11, 2025
**Maintained by:** Noreli North

For latest documentation, visit: https://github.com/norelinorth/norelinorth_brokerage_statement_importer
