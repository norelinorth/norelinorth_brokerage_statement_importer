# Copyright (c) 2026, Noreli North and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StatementAccountingRule(Document):
	"""
	Child table for defining accounting rules per transaction type
	Standard Frappe pattern: Simple child table, minimal logic
	"""
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		credit_account_template: DF.Data | None
		debit_account_template: DF.Data | None
		description_template: DF.Data | None
		enabled: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		transaction_type: DF.Data | None
	# end: auto-generated types

	pass
