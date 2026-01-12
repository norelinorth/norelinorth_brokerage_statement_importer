# Copyright (c) 2026, Noreli North and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StatementImport(Document):
	"""
	Brokerage Statement Import
	Handles PDF upload, parsing, and Journal Entry creation for various brokerage providers

	Standard Frappe pattern: Document controller with lifecycle hooks
	"""
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from statement_importer.statement_importer.doctype.statement_transaction_line.statement_transaction_line import StatementTransactionLine

		company: DF.Link | None
		error_log: DF.TextEditor | None
		import_date: DF.Date | None
		journal_entries_created: DF.Int
		preview_data: DF.TextEditor | None
		statement_file: DF.Attach | None
		statement_period: DF.Data | None
		statement_provider: DF.Link | None
		status: DF.Literal["Draft", "Processing", "Completed", "Failed"]
		transactions: DF.Table[StatementTransactionLine]
		transactions_found: DF.Int
	# end: auto-generated types

	def validate(self):
		"""
		Validate document before save
		Standard Frappe pattern: Use validate hook for business logic
		"""
		# Set default values
		if not self.status:
			self.status = "Draft"

		if not self.import_date:
			self.import_date = frappe.utils.today()

		# Note: Statement Provider validation is done in parse_transactions_with_ai() API method
		# Users should be able to save documents in Draft status without a provider

	def before_save(self):
		"""
		Update counters before save
		Standard Frappe pattern: Update calculated fields
		"""
		# Count transactions
		self.transactions_found = len(self.transactions) if self.transactions else 0

		# Count posted journal entries
		if self.transactions:
			self.journal_entries_created = sum(
				1 for txn in self.transactions
				if txn.status == "Posted" and txn.journal_entry
			)
