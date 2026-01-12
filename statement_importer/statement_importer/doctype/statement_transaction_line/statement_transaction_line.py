# Copyright (c) 2026, Noreli North and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StatementTransactionLine(Document):
	"""
	Child table for storing individual transactions from brokerage statement
	Standard Frappe pattern: Simple child table, minimal logic
	"""
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_credit: DF.Link | None
		account_debit: DF.Link | None
		credit_amount: DF.Currency
		currency: DF.Link | None
		debit_amount: DF.Currency
		description: DF.Data | None
		error_message: DF.Text | None
		journal_entry: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		status: DF.Literal["Pending", "Validated", "Posted", "Error"]
		transaction_date: DF.Date | None
	# end: auto-generated types

	pass
