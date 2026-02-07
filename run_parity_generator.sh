#!/bin/bash

# Parity Generator Runner Script
# Usage: ./run_parity_generator.sh [OPTIONS]
# or: ./run_parity_generator.sh -info <path_to_info_file>

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate Python environment
if [ -d ".venv312" ]; then
    source .venv312/bin/activate
    echo -e "${GREEN}✓ Python environment activated (.venv312)${NC}"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✓ Python environment activated (.venv)${NC}"
else
    echo -e "${RED}✗ Python environment not found (.venv312 or .venv)${NC}"
    exit 1
fi

# Default values
PARITY_INSTANCE="BOS_BUS_PARITY_AXI_M"
PARITY_TYPE="SAFETY.PARITY"
GROUP_FILTER="ALL"
GEN_TOP="YES"
INFO_FILE=""

# Print usage information
show_usage() {
    cat << EOF
${BLUE}Parity Generator Runner${NC}

Usage: $0 [OPTIONS]

Options:
  -info <path>      Path to INFO file (required)
  -inst <name>      Parity instance name (default: BOS_BUS_PARITY_AXI_M)
  -type <type>      Parity scheme type (default: SAFETY.PARITY)
  -group <groups>   GROUP filter: comma-separated names or 'ALL' (default: ALL)
  -gen-top <yes|no> Generate top wrapper module (default: YES)
  -h, --help        Show this help message

Examples:
  $0 -info "[INFO]_BOS_AXICRYPT.safety.xlsx"
  $0 -info "simple_test/[INFO]_SIMPLE_TOP.safety.xlsx" -group "GROUP_A,GROUP_B"
  $0 -info "[INFO]_BOS_AXICRYPT.safety.xlsx" -inst MY_PARITY_INST -gen-top NO

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -info)
            INFO_FILE="$2"
            shift 2
            ;;
        -inst)
            PARITY_INSTANCE="$2"
            shift 2
            ;;
        -type)
            PARITY_TYPE="$2"
            shift 2
            ;;
        -group)
            GROUP_FILTER="$2"
            shift 2
            ;;
        -gen-top)
            GEN_TOP="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}✗ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$INFO_FILE" ]; then
    echo -e "${RED}✗ ERROR: -info parameter is required${NC}"
    echo ""
    show_usage
    exit 1
fi

# Check if INFO file exists
if [ ! -f "$INFO_FILE" ]; then
    echo -e "${RED}✗ ERROR: INFO file not found: $INFO_FILE${NC}"
    exit 1
fi

# Print configuration
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Parity Generator Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "INFO File:        ${GREEN}$INFO_FILE${NC}"
echo -e "Instance Name:    ${GREEN}$PARITY_INSTANCE${NC}"
echo -e "Parity Type:      ${GREEN}$PARITY_TYPE${NC}"
echo -e "Group Filter:     ${GREEN}$GROUP_FILTER${NC}"
echo -e "Generate Top:     ${GREEN}$GEN_TOP${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Run parity generator
echo -e "${YELLOW}Running parity generator...${NC}"
echo ""

python parity_generator.py \
    -info "$INFO_FILE" \
    -inst "$PARITY_INSTANCE" \
    -type "$PARITY_TYPE" \
    -group "$GROUP_FILTER" \
    -gen-top "$GEN_TOP"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Parity generation completed successfully!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
else
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo -e "${RED}✗ Parity generation failed (exit code: $EXIT_CODE)${NC}"
    echo -e "${RED}════════════════════════════════════════${NC}"
fi

exit $EXIT_CODE
