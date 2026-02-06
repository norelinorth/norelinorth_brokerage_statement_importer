# Privacy Policy

**Effective Date**: January 12, 2026
**Last Updated**: January 12, 2026

## Overview

This Privacy Policy describes how the Noreli North Brokerage Statement Importer app ("the App") handles data. **This is not a typical privacy policy** because the App runs entirely on your own infrastructure.

## Key Privacy Principles

### 1. No Data Collection by Developer

**The App developer does NOT collect, store, access, or transmit any of your data.**

- No analytics tracking
- No usage statistics
- No phone-home functionality
- No registration required
- No telemetry
- No cookies set by the developer

### 2. Your Data Stays on Your Server

All data created by the App is stored in:
- Your Frappe/ERPNext database (on your server or Frappe Cloud)
- Your file system (for PDF statements and attachments)
- Your server's local storage

The developer has **zero access** to your installation, brokerage statements, or financial data.

### 3. You Control Everything

You have complete control over:
- Where your data is stored
- Who has access to your brokerage statements
- How long data is retained
- Whether to enable optional AI features
- Data backup and recovery
- Data deletion and purging

## Data Stored by the App

The App stores the following types of data **in your database**:

### Statement Data
- Statement Import documents (company, provider, import date, period)
- Uploaded PDF brokerage statements (stored in your file system)
- Extracted text and tables from PDFs
- Parsed transaction details (dates, descriptions, amounts, accounts)

### Financial Data
- Transaction lines with debit/credit amounts
- Account mappings for journal entries
- Journal Entry references (links to generated entries)
- Transaction status (pending, validated, posted)

### Configuration Data
- Statement Provider configurations
- Accounting rules (transaction type to account mappings)
- AI prompt templates
- Provider-specific settings

### User Activity
- Standard Frappe audit trail (who created/modified records)
- User assignments and permissions
- Document comments and notes

### Sensitive Financial Information
The App processes **highly sensitive financial data**:
- Brokerage account statements
- Investment transaction details
- Account balances
- Security holdings

**Your Responsibility**: Secure your Frappe/ERPNext installation and restrict access to authorized personnel only.

## Optional Third-Party Integrations

The App includes **optional** features that may send data to third parties **only if you explicitly configure and enable them**:

### AI Features (Optional)
If you choose to enable AI features by installing norelinorth_ai_assistant:
- You must configure an AI provider (OpenAI, Anthropic, etc.)
- Data sent: Brokerage statement text, transaction descriptions, account information
- Purpose: Natural language processing for transaction parsing
- Privacy: Subject to your chosen AI provider's privacy policy
- **Warning**: Brokerage statements contain sensitive financial data - ensure your AI provider's privacy policy is acceptable
- Alternative: PDF extraction works without AI (Phase 1). Only AI parsing (Phase 2) requires external service.

### How to Use Without AI
The App has three phases:
1. **Phase 1**: PDF extraction (no external services, 100% local)
2. **Phase 2**: AI parsing (optional, requires AI provider)
3. **Phase 3**: Journal entry creation (no external services, 100% local)

You can use Phase 1 and Phase 3 without ever sending data externally. Simply don't install norelinorth_ai_assistant or manually enter transactions.

### How to Disable Optional Features
If AI Assistant is installed:
- Navigate to **AI Provider** settings
- Remove API keys
- Disable AI Provider

## Data Security

### Your Responsibility
Since the App runs on your infrastructure, data security is primarily your responsibility:

- Secure your Frappe/ERPNext installation with strong authentication
- Keep Frappe/ERPNext and the App updated
- Implement role-based access controls
- Use HTTPS for web access
- Configure firewall rules
- Perform regular backups (including PDF statements)
- Follow Frappe's security best practices
- Restrict access to brokerage statement data to authorized users only
- Consider encrypting file storage for PDF statements

### App Security Measures
The App follows security best practices:
- All database queries use parameterized statements (SQL injection prevention)
- Permission checks on all API endpoints
- XSS prevention via proper escaping
- CSRF protection via Frappe's built-in mechanisms
- Audit trail for all changes
- Role-based access control (Accounts Manager, Accounts User)
- File type validation (PDF only)
- File size limits

## Data Retention and Deletion

### Retention
- Data is retained according to your retention policies
- No automatic data purging (you control retention)
- You may configure your own retention rules
- Consider legal/regulatory retention requirements for financial records

### Deletion
To delete data:
- Uninstall the App via `bench --site [site] uninstall-app statement_importer`
- This removes all DocTypes and app-specific data
- PDF statements stored in file system must be deleted separately
- Standard Frappe/ERPNext data (like Journal Entries) is not affected
- You may also manually delete individual Statement Import documents

## Compliance with Data Protection Laws

### GDPR (European Union)
If you operate in the EU:
- You are the data controller
- The App is a tool you use to process data
- You must ensure your use complies with GDPR
- Brokerage statements may contain personal financial data
- You can export data, delete data, and exercise all GDPR rights

### CCPA (California)
If you operate in California:
- You control all data collected and stored
- You can provide data access and deletion to individuals
- The App does not "sell" personal information

### Financial Regulations
- You are responsible for compliance with financial regulations (SOX, FINRA, SEC, etc.)
- The App provides audit trails and data retention capabilities
- Consult legal/compliance counsel for specific regulatory guidance

### Other Regulations
- You are responsible for compliance with laws in your jurisdiction
- The App provides tools to manage financial data securely
- Consult qualified professionals as needed

## Transparency

The App operates under the MIT License:
- You can inspect all code to verify privacy claims
- You can modify the code to meet your privacy requirements
- No hidden functionality or backdoors
- Complete transparency about data handling

## Changes to This Privacy Policy

This Privacy Policy may be updated to reflect:
- Changes in App functionality
- Changes in data handling practices
- Legal or regulatory requirements

Updates will be:
- Documented in GitHub releases
- Posted in the CHANGELOG
- Effective immediately upon publication

## Your Privacy Rights

Because you control the App and your data, you have the right to:
- Access all data stored by the App
- Export data in standard formats
- Delete data at any time
- Modify the App's source code
- Fork the App and create your own version
- Disable AI features and keep all processing local

## Contact

For privacy questions or concerns:
- GitHub Issues: https://github.com/norelinorth/norelinorth_brokerage_statement_importer/issues
- GitHub Discussions: https://github.com/norelinorth/norelinorth_brokerage_statement_importer/discussions

For data privacy issues related to your installation, contact your Frappe/ERPNext administrator.

---

## Summary

**In Plain English:**

1. **We don't collect your data** - The App runs on your server, not ours
2. **You control everything** - All data stays in your database
3. **Sensitive financial data** - Brokerage statements contain sensitive information; secure appropriately
4. **Traditional Software** - You can inspect all code
5. **AI is optional** - PDF extraction works 100% locally without external services
6. **Standard Frappe security** - Follows all Frappe best practices
7. **You're the data controller** - You're responsible for compliance with data protection laws
8. **No developer access** - We never see your brokerage statements or financial data

---

**Last Updated**: January 12, 2026
**Version**: 1.0

---

**By using the App, you acknowledge that you have read and understood this Privacy Policy.**
