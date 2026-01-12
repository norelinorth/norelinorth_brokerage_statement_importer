# Frappe/ERPNext v16 Compatibility

**Status:** ✅ FULLY COMPATIBLE
**Tested:** v16.0.0+
**Date:** 2026-01-12

---

## Overview

Statement Importer v1.3.8 is fully compatible with both **Frappe Framework v15** and **Frappe Framework v16**, ensuring seamless migration and long-term support.

---

## Version Support Matrix

| Component | Version 15 | Version 16 | Status |
|-----------|------------|------------|--------|
| **Frappe Framework** | v15.84.0+ | v16.0.0+ | ✅ Both |
| **ERPNext** | v15.81.0+ | v16.0.0+ | ✅ Both |
| **Python** | 3.11+ | 3.11+ | ✅ Compatible |
| **Node.js** | 18+ | 20+ | ✅ Compatible |

---

## Compatibility Testing

### Automated CI/CD

**GitHub Actions workflows test both versions:**
- ✅ `test-v15` - Runs on `main` branch
- ✅ `test-v16` - Runs on `version-16` branch
- ✅ Linter checks on all branches

**CI Status:**
- [![CI](https://github.com/norelinorth/statement_importer/actions/workflows/ci.yml/badge.svg)](https://github.com/norelinorth/statement_importer/actions/workflows/ci.yml)

### Test Coverage
- ✅ PDF extraction and parsing
- ✅ AI-powered transaction extraction
- ✅ Journal Entry creation
- ✅ Permission checks
- ✅ Database operations
- ✅ API endpoints

---

## v16 Migration Changes Applied

### 1. Python Version ✅
**Requirement:** Python 3.11+
**Status:** Updated in `pyproject.toml`

```toml
requires-python = ">=3.11"
```

### 2. Database Operations ✅
**v16 Change:** `db.get_value()` returns proper types (not strings)

**Our Code:** Already compatible
```python
# Already uses as_dict=True and checks boolean values directly
debit_account = frappe.db.get_value(
    "Account",
    txn.account_debit,
    ["name", "is_group", "company", "disabled"],
    as_dict=True
)

if debit_account.is_group:  # ✅ Works with boolean, not "0"/"1"
    frappe.throw(_("Account is a group..."))
```

### 3. Permission Checks ✅
**v16 Change:** `has_permission` hooks must return True explicitly

**Our Code:** Uses `frappe.has_permission()` (not custom hooks)
```python
# Standard Frappe permission check - compatible with v16
if not frappe.has_permission("Statement Import", "write"):
    frappe.throw(_("No permission..."))
```

### 4. Query Sorting ✅
**v16 Change:** Default sorting changed from `modified` to `creation`

**Our Code:** No implicit sorting dependencies
- All queries specify explicit fields
- No business logic depends on default sort order

### 5. Whitelisted Methods ✅
**v16 Change:** All whitelisted methods require POST

**Our Code:** Already POST-only
```python
@frappe.whitelist()  # POST requests only
def extract_pdf_preview(statement_doc_name):
    # ...
```

### 6. Translation Functions ✅
**v16 Change:** Deprecated translation methods removed

**Our Code:** Uses standard `_()`
```python
frappe.throw(_("Error message"))  # ✅ Standard pattern
```

### 7. Test Mode Flag ✅
**v16 Change:** `frappe.flags.in_test` → `frappe.in_test`

**Our Code:** No test mode checks in production code

---

## Branch Structure

### Main Branch (v15)
- **Branch:** `main`
- **Frappe:** v15.84.0+
- **ERPNext:** v15.81.0+
- **Python:** 3.11+
- **Node:** 18+

### Version 16 Branch
- **Branch:** `version-16`
- **Frappe:** v16.0.0+
- **ERPNext:** v16.0.0+
- **Python:** 3.11+
- **Node:** 20+

**Both branches share the same codebase** - no v16-specific code changes required!

---

## CI/CD Pipeline

### GitHub Actions Workflows

**`.github/workflows/ci.yml`**
```yaml
jobs:
  linter:
    # Runs on all branches
    # Python 3.11, ruff linter

  test-v15:
    # Runs on main branch
    # Frappe v15, ERPNext v15
    # Full test suite with coverage

  test-v16:
    # Runs on version-16 branch
    # Frappe v16, ERPNext v16
    # Full test suite with coverage
```

### Test Execution

**Automated tests run on:**
- ✅ Every push to `main` or `version-16`
- ✅ Every pull request
- ✅ Manual workflow dispatch

**Test suite includes:**
- Linter checks (ruff)
- Unit tests
- Integration tests
- API endpoint tests
- Permission checks
- Database operations

---

## Installation

### For Frappe v15

```bash
cd frappe-bench
bench get-app https://github.com/norelinorth/statement_importer.git --branch main
```

### For Frappe v16

```bash
cd frappe-bench
bench get-app https://github.com/norelinorth/statement_importer.git --branch version-16
```

**Note:** Both branches use the same code - branch selection determines CI test version only.

---

## Migration Guide (v15 → v16)

### If You're Upgrading Frappe/ERPNext to v16

**No app-specific changes needed!**

1. Upgrade Frappe/ERPNext to v16
2. Statement Importer continues working
3. Optional: Switch to `version-16` branch for v16-specific CI

```bash
cd frappe-bench
bench get-app https://github.com/norelinorth/statement_importer.git --branch version-16 --resolve-deps
bench migrate
```

---

## Compatibility Verification

### Automated Checks

Our CI pipeline verifies:
- ✅ Code passes ruff linting
- ✅ All tests pass on v15
- ✅ All tests pass on v16
- ✅ No regressions between versions

### Manual Verification

You can verify compatibility:

```bash
# Check Python version
python --version  # Should be 3.11+

# Run tests on your bench
bench --site [site] run-tests --app statement_importer

# Check for v16 deprecation warnings
# (None expected - we use standard patterns)
```

---

## Known Compatible Features

### ✅ Core Functionality
- PDF upload and extraction
- AI-powered parsing
- Transaction validation
- Journal Entry creation
- Multi-provider support
- Account validation
- Permission checks

### ✅ DocTypes
- Statement Import
- Statement Transaction Line
- Statement Provider
- Statement Accounting Rule

### ✅ API Endpoints
- `extract_pdf_preview()`
- `parse_transactions_with_ai()`
- `create_journal_entries()`

### ✅ Database Operations
- All queries use standard Frappe ORM
- Parameterized queries (no SQL injection)
- Type-safe field access
- Compatible with v16 query builder

---

## Future Compatibility

### Version Support Policy

We maintain compatibility with:
- ✅ **Current stable** (v16)
- ✅ **Previous stable** (v15)
- ⚠️ **Older versions** - No active testing

### Deprecation Notices

None at this time. All code uses current Frappe standards.

---

## Troubleshooting

### Issue: Tests fail on v16

**Check:**
1. Python version (must be 3.11+)
2. Node version (must be 20+ for v16)
3. Database connection
4. All dependencies installed

### Issue: Type errors in v16

**Likely cause:** Custom code expects string values from `db.get_value()`

**Solution:** Our code already handles this correctly with `as_dict=True`

### Issue: Permission errors

**Check:** User has required roles:
- Accounts Manager
- Statement Import permissions

---

## Contributing

When contributing, ensure:
- ✅ Code passes linting (`ruff check`)
- ✅ Tests pass on both v15 and v16
- ✅ No v16-specific deprecations used
- ✅ Standard Frappe patterns followed

---

## Support

For v16-specific issues:
- [GitHub Issues](https://github.com/norelinorth/statement_importer/issues)
- Label: `version-16`

---

## Certification

**Statement Importer v1.3.8** is:
- ✅ Fully compatible with Frappe v16
- ✅ Fully compatible with ERPNext v16
- ✅ Tested via automated CI/CD
- ✅ No code changes required for v16
- ✅ Ready for Frappe Marketplace

**Status:** PRODUCTION-READY for both v15 and v16

---

**Last Updated:** 2026-01-12
**Maintained by:** Noreli North
