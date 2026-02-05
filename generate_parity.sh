#!/bin/bash

# Script to generate parity for [INFO]_SIMPLE_TOP.safety.xlsx
# Usage: bash generate_parity.sh [options]

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
INFO_FILE="simple_test/[INFO]_SIMPLE_TOP.safety.xlsx"
INSTANCE_NAME="BOS_BUS_PARITY_AXI_M"
PARITY_TYPE="SAFETY.PARITY"
GROUP_FILTER="ALL"
GEN_TOP="YES"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Generate parity for SIMPLE_TOP module"
            echo ""
            echo "Usage: bash generate_parity.sh [options]"
            echo ""
            echo "Options:"
            echo "  -i, --info FILE         INFO file path (default: simple_test/[INFO]_SIMPLE_TOP.safety.xlsx)"
            echo "  -inst NAME              Parity instance name (default: BOS_BUS_PARITY_AXI_M)"
            echo "  -type TYPE              Parity scheme type (default: SAFETY.PARITY)"
            echo "  -group GROUPS           Group filter: comma-separated or 'ALL' (default: ALL)"
            echo "  --no-top                Don't generate top wrapper module"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  bash generate_parity.sh"
            echo "  bash generate_parity.sh -type SAFETY.REGISTER"
            echo "  bash generate_parity.sh -group GROUP_A,GROUP_B"
            exit 0
            ;;
        -i|--info)
            INFO_FILE="$2"
            shift 2
            ;;
        -inst)
            INSTANCE_NAME="$2"
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
        --no-top)
            GEN_TOP="NO"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Parity Generator for SIMPLE_TOP${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Print configuration
echo -e "${YELLOW}Configuration:${NC}"
echo "  INFO File: $INFO_FILE"
echo "  Instance Name: $INSTANCE_NAME"
echo "  Parity Type: $PARITY_TYPE"
echo "  Group Filter: $GROUP_FILTER"
echo "  Generate Top: $GEN_TOP"
echo ""

# Check if INFO file exists
if [ ! -f "$SCRIPT_DIR/$INFO_FILE" ]; then
    echo -e "${RED}Error: INFO file not found at $SCRIPT_DIR/$INFO_FILE${NC}"
    exit 1
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run parity generator
echo -e "${BLUE}Generating parity...${NC}"
echo ""

python3 parity_generator.py \
    -inst "$INSTANCE_NAME" \
    -type "$PARITY_TYPE" \
    -info "$INFO_FILE" \
    -group "$GROUP_FILTER" \
    -gen-top "$GEN_TOP"

# Print success message
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Parity generation completed successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Generated files:${NC}"
echo "  📄 simple_test/RTL/SAFETY/SIMPLE_TOP_NEW.v"
echo "  📄 simple_test/RTL/SAFETY/SIMPLE_TOP_PARITY_NEW.v"
echo ""
