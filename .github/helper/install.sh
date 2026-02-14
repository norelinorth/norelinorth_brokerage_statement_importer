#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing Frappe/ERPNext for CI Tests${NC}"
echo "Branch: ${BRANCH_TO_CLONE}"
echo "Database: ${DB_NAME}"

cd ~

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y \
    redis-server \
    libcups2-dev \
    libssl-dev \
    mariadb-client

# Skip wkhtmltopdf installation for CI (not needed for tests, has libssl1.1 dependency issues on Ubuntu 24.04)
echo -e "${YELLOW}Skipping wkhtmltopdf (not required for CI tests)...${NC}"

# Install bench
echo -e "${YELLOW}Installing bench...${NC}"
pip install frappe-bench

# Manually clone and patch Frappe to bypass Python 3.14 requirement in v16
echo -e "${YELLOW}Cloning and patching Frappe ${BRANCH_TO_CLONE}...${NC}"
git clone -b ${BRANCH_TO_CLONE} --depth 1 https://github.com/frappe/frappe.git frappe-repo
# Relax python requirement from >=3.14 to >=3.12
sed -i 's/^requires-python.*/requires-python = ">=3.12"/' frappe-repo/pyproject.toml
# Verify patch
echo -e "${YELLOW}Verifying pyproject.toml patch:${NC}"
grep "requires-python" frappe-repo/pyproject.toml
git -C frappe-repo add pyproject.toml

# Fix Frappe v16 type hint error (invalid syntax "Type" | None)
echo -e "${YELLOW}Checking for frappe/utils/data.py type hint error...${NC}"
if grep -q "\"UnicodeWithAttrs\" | None" frappe-repo/frappe/utils/data.py; then
    echo -e "${YELLOW}Patching frappe/utils/data.py...${NC}"
    sed -i 's/-> "UnicodeWithAttrs" | None/-> "UnicodeWithAttrs | None"/' frappe-repo/frappe/utils/data.py
    git -C frappe-repo add frappe/utils/data.py
fi

# Fix Frappe v16 type hint error in __init__.py (invalid syntax "Type" | None)
echo -e "${YELLOW}Checking for frappe/__init__.py type hint errors...${NC}"
if grep -q "cache: \"RedisWrapper\" | None = None" frappe-repo/frappe/__init__.py; then
    echo -e "${YELLOW}Patching frappe/__init__.py...${NC}"
    sed -i 's/cache: "RedisWrapper" | None = None/cache: "RedisWrapper | None" = None/' frappe-repo/frappe/__init__.py
    sed -i 's/client_cache: "ClientCache" | None = None/client_cache: "ClientCache | None" = None/' frappe-repo/frappe/__init__.py
    git -C frappe-repo add frappe/__init__.py
fi

# Commit the patch locally so bench init (which clones) picks it up
cd frappe-repo
git config user.email "ci@example.com"
git config user.name "CI"
# Determine if there are changes to commit
if ! git diff --cached --quiet; then
    echo -e "${YELLOW}Committing patches locally...${NC}"
    git commit -m "chore: relax python requirement and fix type hints"
else
    echo -e "${YELLOW}No changes to commit (patches might not have been applied or already applied).${NC}"
fi
cd ..

# Initialize bench with patched Frappe
echo -e "${YELLOW}Initializing bench with patched Frappe...${NC}"
bench init --skip-redis-config-generation --frappe-path $(pwd)/frappe-repo frappe-bench

cd frappe-bench

# Use test MariaDB
echo -e "${YELLOW}Configuring database...${NC}"
bench set-config -g db_host 127.0.0.1
bench set-config -g db_port 3306
bench set-config -g root_login root
bench set-config -g root_password root
bench set-config -g admin_password admin

# Get ERPNext
echo -e "${YELLOW}Getting ERPNext...${NC}"
bench get-app --branch ${BRANCH_TO_CLONE} erpnext

# Get statement_importer (current repo)
echo -e "${YELLOW}Getting statement_importer app...${NC}"
bench get-app statement_importer ${GITHUB_WORKSPACE}

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
./env/bin/pip install pdfplumber coverage

# Create test site
echo -e "${YELLOW}Creating test site...${NC}"
bench new-site test_site \
    --mariadb-root-password root \
    --admin-password admin \
    --install-app erpnext \
    --install-app statement_importer

# Build assets
echo -e "${YELLOW}Building assets...${NC}"
bench --site test_site build

echo -e "${GREEN}Installation complete!${NC}"
echo "Site: test_site"
echo "Admin password: admin"
