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

# Initialize bench
echo -e "${YELLOW}Initializing bench...${NC}"
bench init --skip-redis-config-generation --frappe-branch ${BRANCH_TO_CLONE} frappe-bench

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
