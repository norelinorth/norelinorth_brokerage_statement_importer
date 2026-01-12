// Copyright (c) 2026, Noreli North and contributors
// For license information, please see license.txt

frappe.ui.form.on("Statement Import", {
	refresh(frm) {
		// Add "Extract PDF" button if document is saved and has a file
		if (!frm.is_new() && frm.doc.statement_file) {
			frm.add_custom_button(__("Extract PDF Data"), function() {
				extract_pdf_data(frm);
			}, __("Actions"));
		}

		// Add "Parse with AI" button if PDF has been extracted
		if (!frm.is_new() && frm.doc.preview_data && frm.doc.status !== "Processing") {
			frm.add_custom_button(__("Parse with AI"), function() {
				parse_with_ai(frm);
			}, __("Actions")).addClass("btn-primary");
		}

		// Add "Create Journal Entries" button if transactions have been parsed
		if (!frm.is_new() && frm.doc.transactions_found > 0) {
			frm.add_custom_button(__("Create Journal Entries"), function() {
				create_journal_entries(frm);
			}, __("Actions")).addClass("btn-primary");
		}
	},

	statement_file(frm) {
		// When file is attached, suggest extracting it
		if (frm.doc.statement_file && !frm.is_new()) {
			frappe.show_alert({
				message: __("PDF attached! Click 'Extract PDF Data' to process it."),
				indicator: "blue"
			}, 5);
		}
	}
});

function extract_pdf_data(frm) {
	// Show progress dialog
	frappe.show_alert({
		message: __("Extracting PDF data..."),
		indicator: "blue"
	});

	// Call API to extract PDF
	frappe.call({
		method: "statement_importer.statement_importer.api.extract_pdf_preview",
		args: {
			statement_doc_name: frm.doc.name
		},
		freeze: true,
		freeze_message: __("Extracting PDF data..."),
		callback: function(r) {
			if (r.message && r.message.success) {
				// Reload form to show updated preview
				frm.reload_doc();

				// Show success message with summary
				frappe.msgprint({
					title: __("PDF Extraction Successful"),
					message: __("Found {0} tables in {1} pages", [
						r.message.tables_found,
						r.message.page_count || "?"
					]),
					indicator: "green"
				});

				// Show extracted data in dialog
				show_extraction_preview(r.message);
			}
		},
		error: function(r) {
			frappe.msgprint({
				title: __("Extraction Failed"),
				message: __("Failed to extract PDF data. Please check the error log."),
				indicator: "red"
			});
		}
	});
}

function parse_with_ai(frm) {
	// Confirm before proceeding (AI processing can take time)
	frappe.confirm(
		__("This will use AI to parse transactions from the extracted PDF data. This may take a few moments. Continue?"),
		function() {
			// Show progress indicator
			frappe.show_alert({
				message: __("Parsing transactions with AI..."),
				indicator: "blue"
			});

			// Call API to parse with AI
			frappe.call({
				method: "statement_importer.statement_importer.api.parse_transactions_with_ai",
				args: {
					statement_doc_name: frm.doc.name
				},
				freeze: true,
				freeze_message: __("AI is analyzing the statement... This may take 30-60 seconds..."),
				callback: function(r) {
					if (r.message && r.message.success) {
						// Reload form to show parsed transactions
						frm.reload_doc();

						// Show success message with count
						frappe.msgprint({
							title: __("AI Parsing Successful"),
							message: __("Successfully parsed {0} transactions. Review them in the Transactions table below.", [
								r.message.transactions_parsed
							]),
							indicator: "green"
						});

						// Show parsing results dialog
						show_parsing_results(r.message);
					}
				},
				error: function(r) {
					frappe.msgprint({
						title: __("AI Parsing Failed"),
						message: __("Failed to parse transactions with AI. Please check the error log for details."),
						indicator: "red"
					});
				}
			});
		}
	);
}

function create_journal_entries(frm) {
	// Confirm before creating Journal Entries
	frappe.confirm(
		__("This will create Journal Entries for all Validated and Pending transactions. Continue?"),
		function() {
			// Show progress indicator
			frappe.show_alert({
				message: __("Creating Journal Entries..."),
				indicator: "blue"
			});

			// Call API to create Journal Entries
			frappe.call({
				method: "statement_importer.statement_importer.api.create_journal_entries",
				args: {
					statement_doc_name: frm.doc.name
				},
				freeze: true,
				freeze_message: __("Creating Journal Entries... This may take a moment..."),
				callback: function(r) {
					// FIX Issue #2: Handle all response types (success, partial success, failure)
					if (r.message) {
						// Always reload to show updated transaction statuses
						frm.reload_doc();

						if (r.message.success || r.message.journal_entries_created > 0) {
							// Show results (even if partial success with some errors)
							show_je_creation_results(r.message);
						} else {
							// All transactions failed - show error message
							frappe.msgprint({
								title: __("No Journal Entries Created"),
								message: __("Failed to create any Journal Entries. Please check transaction statuses and error messages in the Transactions table below."),
								indicator: "red"
							});
						}
					}
				},
				error: function(r) {
					// FIX Issue #4: Show actual error message instead of generic message
					let error_msg = __("Failed to create Journal Entries. Please check the error log for details.");

					// Try to extract actual error message from server response
					if (r._server_messages) {
						try {
							let server_msgs = JSON.parse(r._server_messages);
							if (server_msgs && server_msgs.length > 0) {
								let msg = JSON.parse(server_msgs[0]);
								if (msg.message) {
									error_msg = msg.message;
								}
							}
						} catch (e) {
							// Fallback to generic message if parsing fails
							console.error("Failed to parse server error:", e);
						}
					}

					frappe.msgprint({
						title: __("Journal Entry Creation Failed"),
						message: error_msg,
						indicator: "red"
					});
				}
			});
		}
	);
}

function show_je_creation_results(data) {
	// Build results HTML
	let html = `
		<div class="je-creation-results">
			<h4>Journal Entry Creation Summary</h4>
			<ul>
				<li><strong>Journal Entries Created:</strong> ${data.journal_entries_created}</li>
				<li><strong>Transactions Posted:</strong> ${data.transactions_posted}</li>
				${data.errors && data.errors.length > 0 ? `<li><strong>Errors:</strong> ${data.errors.length}</li>` : ''}
			</ul>

			${data.journal_entry_names && data.journal_entry_names.length > 0 ? `
				<h4>Created Journal Entries</h4>
				<ul>
					${data.journal_entry_names.map(name => `
						<li><a href="/app/journal-entry/${name}" target="_blank">${name}</a></li>
					`).join('')}
				</ul>
			` : ''}

			${data.errors && data.errors.length > 0 ? `
				<h4 class="text-danger">Errors</h4>
				<ul class="text-danger">
					${data.errors.map(err => `
						<li><strong>${frappe.utils.escape_html(err.transaction)}:</strong> ${frappe.utils.escape_html(err.error)}</li>
					`).join('')}
				</ul>
			` : ''}

			<hr>
			<p class="text-muted">
				<strong>Next Steps:</strong>
				<ol>
					<li>Review the created Journal Entries (links above)</li>
					<li>Verify the accounting entries are correct</li>
					<li>Submit the Journal Entries to post to General Ledger</li>
				</ol>
			</p>
		</div>
	`;

	// Show results dialog
	frappe.msgprint({
		title: __("Journal Entries Created"),
		message: html,
		indicator: data.errors && data.errors.length > 0 ? "orange" : "green",
		wide: true
	});
}

function show_parsing_results(data) {
	// Show results dialog
	let dialog = new frappe.ui.Dialog({
		title: __("AI Parsing Results"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "results_html"
			}
		],
		size: "large",
		primary_action_label: __("Close"),
		primary_action: function() {
			dialog.hide();
		}
	});

	// Build results HTML
	let html = `
		<div class="parsing-results">
			<h4>Parsing Summary</h4>
			<ul>
				<li><strong>Transactions Parsed:</strong> ${data.transactions_parsed}</li>
				<li><strong>Status:</strong> <span class="text-success">Completed</span></li>
			</ul>

			<hr>
			<p class="text-muted">
				<strong>Next Steps:</strong>
				<ol>
					<li>Review the parsed transactions in the "Transactions" table below</li>
					<li>Verify the account mappings are correct</li>
					<li>Check that debit/credit amounts are balanced</li>
					<li>Click "Create Journal Entries" when ready (Phase 3)</li>
				</ol>
			</p>

			<div class="alert alert-info">
				<strong>Note:</strong> AI-parsed data should be reviewed before posting.
				The system uses brokerage statement patterns configured for your provider, but manual verification
				is recommended for accuracy.
			</div>
		</div>
	`;

	dialog.fields_dict.results_html.$wrapper.html(html);
	dialog.show();
}

function show_extraction_preview(data) {
	// Show preview dialog with extracted data
	let dialog = new frappe.ui.Dialog({
		title: __("PDF Extraction Preview"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "preview_html"
			}
		],
		size: "large",
		primary_action_label: __("Close"),
		primary_action: function() {
			dialog.hide();
		}
	});

	// Build preview HTML
	let html = `
		<div class="extraction-preview">
			<h4>Extraction Summary</h4>
			<ul>
				<li><strong>Tables Found:</strong> ${data.tables_found}</li>
				<li><strong>Text Preview:</strong> ${data.text_preview.length} characters extracted</li>
			</ul>

			<h4>Text Preview (first 1000 characters)</h4>
			<pre style="background: #f5f5f5; padding: 10px; max-height: 200px; overflow: auto; white-space: pre-wrap;">${frappe.utils.escape_html(data.text_preview)}</pre>

			${data.tables_found > 0 ? `
				<h4>First Table Preview</h4>
				<div style="max-height: 300px; overflow: auto;">
					${format_table_html(data.tables_preview[0])}
				</div>
			` : '<p class="text-muted">No tables found</p>'}

			<hr>
			<p class="text-muted">
				<strong>Next Steps:</strong> Full preview is available in the "Preview Data" field below.
				<br>Click "Parse with AI" to automatically extract transactions using AI.
			</p>
		</div>
	`;

	dialog.fields_dict.preview_html.$wrapper.html(html);
	dialog.show();
}

function format_table_html(table) {
	if (!table || table.length === 0) {
		return '<p class="text-muted">No table data</p>';
	}

	let html = '<table class="table table-bordered table-sm" style="font-size: 12px;">';

	// Add rows
	for (let i = 0; i < Math.min(table.length, 10); i++) {
		html += '<tr>';
		for (let cell of table[i]) {
			let tag = i === 0 ? 'th' : 'td';
			let content = cell !== null ? frappe.utils.escape_html(String(cell)) : '';
			html += `<${tag}>${content}</${tag}>`;
		}
		html += '</tr>';
	}

	if (table.length > 10) {
		html += `<tr><td colspan="${table[0].length}" class="text-muted text-center">... ${table.length - 10} more rows</td></tr>`;
	}

	html += '</table>';
	return html;
}
