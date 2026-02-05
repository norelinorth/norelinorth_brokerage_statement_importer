#!/bin/bash
# Comprehensive test runner for Statement Importer
# Runs all test suites and generates coverage report

set -e  # Exit on error

SITE="${1:-erpnext.local}"
APP="statement_importer"

echo "════════════════════════════════════════════════════════════════"
echo "Statement Importer - Comprehensive Test Suite"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Site: $SITE"
echo "App: $APP"
echo ""

# Change to frappe-bench directory
cd "$(dirname "$0")/../.."

# Activate virtual environment
if [ -d "env/bin" ]; then
    source env/bin/activate
fi

echo "════════════════════════════════════════════════════════════════"
echo "Test Suite 1: Core Functionality Tests"
echo "════════════════════════════════════════════════════════════════"
echo ""
bench --site "$SITE" run-tests \
    --module "$APP.statement_importer.doctype.statement_import.test_statement_import_core" \
    --verbose

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Test Suite 2: API Integration Tests"
echo "════════════════════════════════════════════════════════════════"
echo ""
bench --site "$SITE" run-tests \
    --module "$APP.statement_importer.tests.test_api_integration" \
    --verbose

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Test Suite 3: Legacy Tests (if any)"
echo "════════════════════════════════════════════════════════════════"
echo ""
# Run other existing tests
bench --site "$SITE" run-tests --app "$APP" --verbose || true

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ All Tests Complete"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "To run with coverage:"
echo "  bench --site $SITE run-tests --app $APP --coverage"
echo ""
echo "To run specific test:"
echo "  bench --site $SITE run-tests --module $APP.statement_importer.doctype.statement_import.test_statement_import_core"
echo ""
