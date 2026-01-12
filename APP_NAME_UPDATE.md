# App Name Update for Frappe Marketplace
**Date:** 2026-01-12
**Version:** 1.3.8
**Status:** ✅ COMPLETE

---

## Official App Name

**Frappe Marketplace Display Name:**
```
Noreli North Brokerage Statement Importer
```

**Technical App Name (unchanged):**
```
statement_importer
```

---

## Rationale

### Why This Name?

1. **Brand Identity** ✅
   - Includes publisher name "Noreli North"
   - Establishes brand recognition in marketplace

2. **Clear Purpose** ✅
   - "Brokerage Statement" - Immediately clear it's for investment accounts
   - Not misleading (users won't expect general PDF import)

3. **Target Audience** ✅
   - Targets users with brokerage accounts (IB, Schwab, Fidelity)
   - Filters out users looking for invoice/receipt processing

4. **SEO-Friendly** ✅
   - Keywords: Noreli North, Brokerage, Statement, Importer
   - Easy to find in Frappe Marketplace search

---

## What Was Updated

### Core Configuration ✅

**File:** `statement_importer/hooks.py`
```python
app_title = "Noreli North Brokerage Statement Importer"  # ✅ UPDATED
app_name = "statement_importer"  # Unchanged (technical identifier)
app_publisher = "Noreli North"
```

### Documentation ✅

**Updated Files:**
1. ✅ `README.md` - Main title and overview
2. ✅ `USER_GUIDE.md` - Document title
3. ✅ `API_DOCUMENTATION.md` - Document title

**Changes:**
```markdown
# Noreli North Brokerage Statement Importer

**Automatic Journal Entry creation from brokerage statement PDFs for ERPNext**

**Designed specifically for investment brokerage statements** - extracts
buy/sell trades, dividends, interest, and fees to create accurate accounting entries.
```

---

## Marketplace Display

### How It Appears

**Frappe Marketplace:**
```
╔════════════════════════════════════════════════════════════╗
║  Noreli North Brokerage Statement Importer                ║
║  by Noreli North                                          ║
║                                                           ║
║  Automatic Journal Entry creation from brokerage         ║
║  statement PDFs (Interactive Brokers, Charles Schwab,    ║
║  Fidelity, etc.)                                         ║
║                                                           ║
║  ⭐⭐⭐⭐⭐  Version 1.3.8  MIT License                    ║
╚════════════════════════════════════════════════════════════╝
```

### Search Terms That Find This App

Users searching for:
- ✅ "Noreli North" (brand)
- ✅ "Brokerage Statement" (category)
- ✅ "Interactive Brokers" (provider)
- ✅ "Investment Import" (use case)
- ✅ "Trading Statement" (synonym)

Users searching for (won't be misled):
- ❌ "PDF Importer" (too generic - they'll see it's brokerage-specific)
- ❌ "Invoice Import" (wrong category)
- ❌ "Receipt Scanner" (wrong use case)

---

## Technical Identifier (Unchanged)

### Why `app_name` Stays `statement_importer`

**Technical identifier** used in:
- Bench commands: `bench --site [site] install-app statement_importer`
- Python imports: `import statement_importer`
- File structure: `apps/statement_importer/`
- Git repository: `github.com/norelinorth/statement_importer`

**Changing this would break:**
- ❌ Existing installations
- ❌ Import statements
- ❌ Database references
- ❌ Git history

**Therefore:** `app_name` remains `statement_importer` (technical), while `app_title` is customer-facing.

---

## User-Facing References

### In ERPNext UI

**Workspace:**
- Title: "Statement Importer" (from DocType/Workspace definition)
- Can be customized by users

**Menu:**
```
Desk → Statement Importer → Statement Import
```

**About Page:**
```
App Title: Noreli North Brokerage Statement Importer
Version: 1.3.8
Publisher: Noreli North
```

---

## Branding Consistency

### All Public References ✅

| Location | Name |
|----------|------|
| **Marketplace Listing** | Noreli North Brokerage Statement Importer |
| **README.md** | Noreli North Brokerage Statement Importer |
| **USER_GUIDE.md** | Noreli North Brokerage Statement Importer |
| **API_DOCUMENTATION.md** | Noreli North Brokerage Statement Importer |
| **hooks.py (app_title)** | Noreli North Brokerage Statement Importer |
| **GitHub Repository** | statement_importer |
| **Bench CLI** | statement_importer |

---

## Competitive Positioning

### Similar Apps (Hypothetical)

| App Name | Clarity | Specificity |
|----------|---------|-------------|
| **Noreli North Brokerage Statement Importer** | ✅ Clear | ✅ Specific |
| "Statement Importer" | ⚠️ Vague | ❌ Generic |
| "PDF Parser" | ❌ Unclear | ❌ Too broad |
| "Investment Import" | ⚠️ Okay | ⚠️ Missing detail |

### Advantages

✅ **Brand Recognition** - "Noreli North" establishes trust
✅ **Clear Category** - "Brokerage Statement" defines scope
✅ **Accurate Expectations** - Users know exactly what they get
✅ **Professional** - Sounds enterprise-ready

---

## Migration Notes

### For Existing Users

**No action required!**

- Technical identifier (`statement_importer`) unchanged
- Existing installations continue working
- Only display name changed (cosmetic)

### For New Users

- See "Noreli North Brokerage Statement Importer" in marketplace
- Install with: `bench get-app statement_importer`
- Technical name used for installation (standard Frappe pattern)

---

## SEO & Discovery

### Frappe Marketplace Search

**Primary Keywords:**
- Noreli North ✅
- Brokerage ✅
- Statement ✅
- Importer ✅

**Secondary Keywords (in description):**
- Interactive Brokers ✅
- Charles Schwab ✅
- Fidelity ✅
- Journal Entry ✅
- Investment ✅
- Trading ✅

### Google Search

**Likely queries that find this:**
- "ERPNext brokerage statement import"
- "Interactive Brokers ERPNext integration"
- "Investment accounting ERPNext"
- "Noreli North ERPNext apps"

---

## Verification

### Check App Title

```bash
# In bench console
>>> import frappe
>>> frappe.get_hooks("app_title", app_name="statement_importer")
['Noreli North Brokerage Statement Importer']
```

### Check About Page

```
ERPNext → Help → About → Installed Apps
→ Noreli North Brokerage Statement Importer (1.3.8)
```

---

## Final Status

✅ **App Name Updated**
✅ **Documentation Consistent**
✅ **Technical Identifier Preserved**
✅ **Marketplace-Ready**
✅ **Brand Recognition Established**

**Official Name:**
```
Noreli North Brokerage Statement Importer
```

---

**Updated:** 2026-01-12
**Status:** COMPLETE
**Ready for Marketplace Submission:** ✅ YES
