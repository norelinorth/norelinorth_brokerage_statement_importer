# Copyright (c) 2026, Noreli North and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class StatementProvider(Document):
	"""
	Statement Provider Configuration
	Defines how to parse and account for transactions from different brokerage providers

	Standard Frappe pattern: Document controller with lifecycle hooks
	"""
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from statement_importer.statement_importer.doctype.statement_accounting_rule.statement_accounting_rule import StatementAccountingRule

		accounting_rules: DF.Table[StatementAccountingRule]
		enabled: DF.Check
		prompt_template: DF.LongText | None
		provider_name: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""
		Validate document before save
		Standard Frappe pattern: Use validate hook for business logic
		"""
		# Validate provider name is unique
		if self.provider_name:
			self.provider_name = self.provider_name.strip()

		# Ensure at least one accounting rule if enabled
		if self.enabled and (not self.accounting_rules or len(self.accounting_rules) == 0):
			frappe.msgprint(
				_("Warning: Provider is enabled but has no accounting rules defined"),
				indicator="orange"
			)

		# Validate accounting rules have required fields
		if self.accounting_rules:
			for idx, rule in enumerate(self.accounting_rules, start=1):
				if not rule.transaction_type:
					frappe.throw(
						_("Accounting Rule {0}: Transaction Type is required").format(idx),
						title=_("Validation Error")
					)

	def before_save(self):
		"""
		Process before save
		Standard Frappe pattern: Pre-save processing
		"""
		# Validate prompt template has required placeholders
		if self.prompt_template and self.enabled:
			required_placeholders = ["{text}", "{tables}"]
			missing = [p for p in required_placeholders if p not in self.prompt_template]

			if missing:
				frappe.msgprint(
					_("Warning: Prompt template is missing recommended placeholders: {0}").format(", ".join(missing)),
					indicator="orange"
				)
