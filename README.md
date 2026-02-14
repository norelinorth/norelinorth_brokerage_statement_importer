# Noreli North Brokerage Statement Importer

**Automatic Journal Entry creation from brokerage statement PDFs for ERPNext**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frappe v15](https://img.shields.io/badge/Frappe-v15.84.0+-blue.svg)](https://frappeframework.com)
[![Frappe v16](https://img.shields.io/badge/Frappe-v16.0.0+-blue.svg)](https://frappeframework.com)
[![ERPNext v15](https://img.shields.io/badge/ERPNext-v15.81.0+-green.svg)](https://erpnext.com)
[![ERPNext v16](https://img.shields.io/badge/ERPNext-v16.0.0+-green.svg)](https://erpnext.com)
[![Standards Compliance](https://img.shields.io/badge/Frappe%20Standards-100%25-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/norelinorth/norelinorth_brokerage_statement_importer/pulls)
[![CI](https://img.shields.io/github/actions/workflow/status/norelinorth/norelinorth_brokerage_statement_importer/ci.yml?branch=main)](https://github.com/norelinorth/norelinorth_brokerage_statement_importer/actions/workflows/ci.yml)

## Overview

Noreli North Brokerage Statement Importer is a production-ready Frappe/ERPNext app that automates Journal Entry creation from brokerage statement PDFs. It leverages AI-powered transaction parsing and supports multiple brokerage providers including Interactive Brokers and custom templates.

**Designed specifically for investment brokerage statements** - extracts buy/sell trades, dividends, interest, and fees to create accurate accounting entries.

### Key Features

- 📄 **PDF Upload & Extraction** - Upload PDF statements and extract text/tables automatically
- 🤖 **AI-Powered Parsing** - Intelligent transaction extraction using provider-specific templates
- 🏦 **Multi-Provider Support** - Interactive Brokers and custom templates (extensible)
- ✅ **Transaction Validation** - Automatic validation of debits/credits, balancing, and required fields
- 🔒 **Security First** - Permission checks, file validation, XSS prevention
- 🌍 **Internationalization** - All strings translatable, multi-currency ready
- 📊 **Professional Quality** - 100% Frappe/ERPNext standards compliance (v15 & v16 compatible)

### Supported Providers

| Provider | Status | Notes |
|----------|--------|-------|
| Interactive Brokers | ✅ Supported | Full transaction parsing |
| Charles Schwab | ✅ Supported | Configurable rules |
| Fidelity | ✅ Supported | Configurable rules |
| Custom Providers | ✅ Extensible | Add via Statement Provider DocType |

## Requirements

- **Frappe Framework:** v15.84.0+ or v16.0.0+ ✅ Both supported
- **ERPNext:** v15.81.0+ or v16.0.0+ ✅ Both supported
- **Python:** 3.11+
- **Dependencies:** pdfplumber (auto-installed)
- **Optional:** norelinorth_ai_assistant app (for AI parsing features)

See [V16_COMPATIBILITY.md](V16_COMPATIBILITY.md) for full version compatibility details.

## Documentation

For a complete walkthrough of all features, roles, and workflows, please consult the:

👉 **[Comprehensive User Guide](USER_GUIDE.md)**

It covers:
- detailed prerequisites
- step-by-step import workflow
- troubleshooting common errors (PDF issues, balancing)
- best practices for accounting automation


## Quick Start Guide

### 1. Navigate to Statement Importer

**Desk → Statement Importer → Statement Import**

### 2. Create New Statement Import

- **Company:** Select your company
- **Import Date:** Today (auto-filled)
- **Statement Period:** e.g., "2026-01"
- **Statement Provider:** Select (Interactive Brokers, Schwab, or Fidelity)

### 3. Upload PDF Statement

- Click **Attach** button
- Select your brokerage PDF statement
- Save the document

### 4. Extract PDF Data

- Click **Actions → Extract PDF Data**
- Review the extracted text and tables in the preview
- Verify all pages were processed correctly

### 5. Parse Transactions with AI

- Click **Actions → Parse with AI**
- Wait for AI processing (progress shown)
- Review parsed transactions in the **Transactions** table

### 6. Review & Validate

- Check transaction dates, descriptions, amounts
- Verify debit/credit accounts are correct
- Ensure all transactions balance (debit = credit)
- Update transaction status to "Validated" for approved transactions

### 7. Create Journal Entries

- Click **Actions → Create Journal Entries**
- System validates all accounts and amounts
- Journal Entries are created automatically
- If Journal Validation app is installed, JEs are automatically validated
- Review created Journal Entries in ERPNext
- Submit Journal Entries as needed

## Configuration

### Statement Provider Setup

**Desk → Statement Importer → Statement Provider**

Each provider has:
- **Provider Name:** Display name (e.g., "Interactive Brokers")
- **Enabled:** Toggle to enable/disable provider
- **Prompt Template:** AI parsing instructions (provider-specific)
- **Accounting Rules:** Transaction type mappings (buy/sell/dividend/fee)

### AI Integration (Critical for Phase 2)

To enable AI-powered transaction parsing, you must configure the **Noreli North AI Assistant**:

1. **Configure Provider**:
   - Navigate to **Desk → AI Assistant → AI Provider**
   - Create a new provider (e.g., "OpenAI" or "Anthropic")
   - Enter your **API Key**
   - Set as **Default**

2. **Verify**:
   - Go to **Statement Importer → Statement Provider**
   - Ensure your providers (e.g., "Interactive Brokers") are enabled

> **Note:** Without this configuration, the "Parse with AI" action will fail or return empty results.

## Features by Phase

### ✅ Phase 1: PDF Extraction (Complete)

- PDF upload and secure storage
- Text extraction from all pages
- Table extraction for structured data
- HTML preview with extracted content
- Error handling and logging
- File validation (PDF only, size limits)

### ✅ Phase 2: AI Parsing (Complete)

- AI-powered transaction parsing
- Provider-specific prompt templates
- Comprehensive accounting rules (buy/sell/dividends/fees/transfers)
- Transaction validation (dates, amounts, balancing)
- Interactive parsing results dialog
- Progress indicators for AI processing
- Error handling with user-friendly messages

### ✅ Phase 3: Journal Entry Creation (Complete)

- Automatic Journal Entry creation from validated transactions
- Account validation before JE creation
- Transaction status tracking (Pending → Validated → Posted)
- Journal Entry linking for audit trail
- Automatic integration with Journal Validation app (if installed)
- Batch processing with error handling
- Detailed success/error reporting

## Architecture

### DocTypes

| DocType | Type | Purpose |
|---------|------|---------|
| **Statement Import** | Parent | Main document for PDF statement processing |
| **Statement Transaction Line** | Child Table | Individual transactions parsed from statement |
| **Statement Provider** | Master | Provider configuration (IB, Schwab, Fidelity, etc.) |
| **Statement Accounting Rule** | Child Table | Transaction type to account mappings |

### API Endpoints

| Method | Permission | Purpose |
|--------|-----------|---------|
| `extract_pdf_preview(statement_doc_name)` | Statement Import (write) | Extract and preview PDF data |
| `parse_transactions_with_ai(statement_doc_name)` | Statement Import (write) | AI-powered transaction parsing |
| `create_journal_entries(statement_doc_name)` | Statement Import (write) | Create Journal Entries |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API reference.

### Workflow

```
PDF Upload → Extract Text/Tables → Parse with AI → Validate Transactions → Create Journal Entries
```

## Standards Compliance

This app is built with **100% Frappe/ERPNext standards compliance**:

- ✅ **No hardcoded values** - All configuration from database
- ✅ **No custom fields on core DocTypes** - Only custom DocTypes used
- ✅ **No core modifications** - All functionality in custom app
- ✅ **Permission checks** on all API endpoints
- ✅ **Standard Frappe patterns** - ORM, error handling, validation
- ✅ **Internationalization ready** - All strings use `_()` translation
- ✅ **Security best practices** - SQL injection prevention, XSS protection, file validation

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive user guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Developer API reference
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

## Support

### Getting Help

- **Issues:** [GitHub Issues](https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/norelinorth/norelinorth_brokerage_statement_importer/discussions)

### Reporting Bugs

Please open a GitHub Issue with:
1. ERPNext version
2. Statement Importer version
3. Steps to reproduce
4. Expected vs actual behavior
5. Error logs (if applicable)

### Feature Requests

We welcome feature requests! Please open a GitHub Issue with:
- Clear description of the feature
- Use case / business value
- Any relevant examples or mockups

## Contributing

We welcome contributions! Please follow these guidelines:

### Code Standards

- Follow Frappe/ERPNext coding conventions
- Add docstrings to all classes and methods
- All strings must use `_()` for translation
- Ensure code quality before submitting PR

### Pre-commit Hooks

- **ruff** - Python linting
- **eslint** - JavaScript linting
- **prettier** - Code formatting
- **pyupgrade** - Python modernization

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Roadmap

### Version 1.3.8

- ✅ Multi-provider support (IB, Schwab, Fidelity)
- ✅ Provider configuration UI
- ✅ Customizable accounting rules
- ✅ **Automatic Journal Entry creation**
- ✅ **Integration with Journal Validation** (automatic)
- ✅ **Transaction status tracking**
- ✅ **100% Standards Compliance**

### Version 1.4.0 (Current)

- ✅ **Frappe v16 Compatibility** (Python 3.12/3.13 ready)
- ✅ **Automated CI Patching** (Type hints & uuid7)
- ✅ **Enhanced Documentation** (AI Config & User Guide)
- ✅ **Stability Fixes** (Redis & Node deps)

### Version 1.5.0 (Future)

- 🔲 Multi-currency support for transactions
- 🔲 Advanced account mapping wizard
- 🔲 Scheduled batch processing
- 🔲 Duplicate detection

### Version 2.0.0 (Future)

- 🔲 Bank statement support
- 🔲 Credit card statement support
- 🔲 Advanced matching algorithms
- 🔲 Reporting and analytics dashboards

## License

MIT License

Copyright (c) 2026 Noreli North

See [LICENSE](license.txt) for full license text.

## Credits

**App:** Noreli North Brokerage Statement Importer
**Author:** Noreli North
**Maintainer:** Noreli North
**Version:** 1.4.0

### Built With

- [Frappe Framework](https://frappeframework.com) - Web framework for rapid application development
- [ERPNext](https://erpnext.com) - Open source ERP
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF data extraction

### Acknowledgments

- Frappe Technologies team for the excellent framework
- ERPNext community for best practices and patterns
- Contributors and testers

---



For support, please use [GitHub Issues](https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues)
