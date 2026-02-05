import frappe
from statement_importer.statement_importer.api import (
    extract_pdf_preview, 
    parse_transactions_with_ai, 
    create_journal_entries
)

def run_e2e_test(doc_name):
    print(f"Starting E2E Test for {doc_name}")
    
    # 1. Extract PDF
    print("\n[Step 1] Extracting PDF Data...")
    res1 = extract_pdf_preview(doc_name)
    print(f"Extraction Result: {res1.get('success')}")
    print(f"Tables Found: {res1.get('tables_found')}")
    
    # 2. Parse with AI
    print("\n[Step 2] Parsing transactions with AI...")
    res2 = parse_transactions_with_ai(doc_name)
    print(f"AI Parsing Result: {res2.get('success')}")
    print(f"Transactions Parsed: {res2.get('transactions_parsed')}")
    
    # 3. Create Journal Entries
    print("\n[Step 3] Creating Journal Entries...")
    res3 = create_journal_entries(doc_name)
    print(f"JE Creation Result: {res3.get('success')}")
    print(f"Journal Entries Created: {res3.get('journal_entries_created')}")
    if res3.get('journal_entry_names'):
        print(f"Created JEs: {', '.join(res3.get('journal_entry_names'))}")
    if res3.get('errors'):
        print("\nErrors encountered:")
        for err in res3.get('errors'):
            print(f"  - {err['transaction']}: {err['error']}")

if __name__ == "__main__":
    frappe.init(site="erpnext.local")
    frappe.connect()
    try:
        run_e2e_test("STMT-IMP-2026-14535")
    finally:
        frappe.destroy()
