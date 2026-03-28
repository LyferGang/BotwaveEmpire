#!/bin/bash

# =============================================================================
# GRINGO WIRELESS RECONNAISSANCE TOOL - MAIN ENTRY POINT
# The "Brain" of the operation. Handles user interaction and menu navigation.
# =============================================================================

GRINGO_VERSION="2.0.1"
GRINGO_AUTHOR="Gringo"
GRINGO_DESCRIPTION="Wireless Reconnaissance & Business Logic Audit Suite"

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

# Default configuration values
INTERFACE=""
CHANNEL="6"
DURATION="10"
SELECTED_IFACE=""
BSSID=""

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

print_header() {
    local title=$1
    
    echo ""
    set_color BLUE
    set_bold
    echo "================================================"
    echo "$title"
    echo "================================================"
    set_color RESET
}

print_success() {
    local msg=$1
    echo -e "${GREEN}[SUCCESS]${RESET} $msg"
}

print_warning() {
    local msg=$1
    echo -e "${YELLOW}[WARNING]${RESET} $msg"
}

print_error() {
    local msg=$1
    echo -e "${RED}[ERROR]${RESET} $msg"
}

set_color() {
    local color=$1
    case $color in
        BLUE)   COLOR_CODE=$BLUE;;
        GREEN)  COLOR_CODE=$GREEN;;
        YELLOW) COLOR_CODE=$YELLOW;;
        RED)    COLOR_CODE=$RED;;
        MAGENTA)COLOR_CODE=$MAGENTA;;
        CYAN)   COLOR_CODE=$CYAN;;
        WHITE)  COLOR_CODE=$WHITE;;
    esac
}

set_bold() {
    BOLD_MODE=1
}

reset_bold() {
    BOLD_MODE=0
}

# =============================================================================
# BANNER & GREETING FUNCTIONS
# =============================================================================

show_banner() {
    echo ""
    set_color MAGENTA
    set_bold
    
    # Main greeting - now more casual!
    echo "================================================"
    echo "       WELCOME TO GRINGO WIRELESS TOOL v$GRINGO_VERSION"
    echo "================================================"
    echo ""
    echo "Hey there! Ready to get some wireless recon done?"
    echo "This tool helps you:"
    echo "  • Capture WPA handshakes (muscle mode)"
    echo "  • Audit business logic (money mode)"
    echo "  • Sync with OpenClaw brain (intelligence mode)"
    echo ""
    echo "I'm your friendly neighborhood recon bot."
    echo "Let's get this party started!"
    echo ""
    
    set_color RESET
}

show_menu() {
    set_color BLUE
    set_bold
    
    echo ""
    echo "================================================"
    echo "GRINGO WIRELESS RECONNAISSANCE TOOL v$GRINGO_VERSION"
    echo "================================================"
    echo ""
    
    echo "1. Check System Requirements (Root & Dependencies)"
    echo "2. List Available Interfaces"
    echo "3. Enable Monitor Mode"
    echo "4. Disable Monitor Mode"
    echo "5. WiFi Scan (airodump-ng)"
    echo "6. WPS Scan"
    echo "7. Deauth Attack (Single Target)"
    echo "8. Deauth Attack (All Clients)"
    echo "9. Handshake Capture"
    echo "10. Tools Menu"
    echo "11. Exit"
    echo ""
    
    set_color RESET
}

main_menu() {
    while true; do
        show_menu
        
        read -p "Select an option [1-11]: " choice
        
        case $choice in
            1)
                check_root_access
                check_dependencies
                ;;
                
            2)
                list_interfaces
                ;;
                
            3)
                # Check if interface is selected, if not prompt user to select one
                if [[ -z "$SELECTED_IFACE" ]]; then
                    print_warning "No interface currently selected. Please select an interface first."
                    
                    # Call select_target_interface to properly capture and validate user input
                    select_target_interface || true
                    
                    # Verify interface was successfully selected before proceeding
                    if [[ -n "$SELECTED_IFACE" && "$SELECTED_IFACE" != *"mon"* ]]; then
                        print_success "Interface $SELECTED_IFACE ready for monitor mode activation."
                    else
                        print_error "Failed to select valid interface. Please try again."
                        continue
                    fi
                fi
                
                # Enable monitor mode on the selected interface
                enable_monitor_mode "$SELECTED_IFACE"
                
            4)
                # Fixed: Use SELECTED_IFACE for consistency with case 3
                disable_monitor_mode "$SELECTED_IFACE"
                ;;
                
            5)
                if [[ -z "$INTERFACE" ]]; then
                    print_error "No interface in monitor mode. Please enable monitor mode first."
                else
                    read -p "Enter BSSID (leave empty for all): " bssid
                    read -p "Enter channel [default: $CHANNEL]: " ch
                    ch=${ch:-$CHANNEL}
                    read -p "Scan duration [default: 10s]: " dur
                    dur=${dur:-$DURATION}
                    
                    run_airodump_scan "$INTERFACE" "$bssid" "$ch" "$dur"
                fi
                ;;
                
            6)
                if [[ -z "$INTERFACE" ]]; then
                    print_error "No interface in monitor mode. Please enable monitor mode first."
                else
                    read -p "Enter channel [default: $CHANNEL]: " ch
                    ch=${ch:-$CHANNEL}
                    
                    run_wps_scan "$INTERFACE"
                fi
                ;;
                
            7)
                if [[ -z "$INTERFACE" ]]; then
                    print_error "No interface in monitor mode. Please enable monitor mode first."
                else
                    read -p "Enter BSSID: " bssid
                    read -p "Enter target MAC address (leave empty for any): " mac
                    read -p "Number of deauth packets [default: 50]: " cnt
                    cnt=${cnt:-50}
                    
                    run_deauth_attack "$INTERFACE" "$bssid" "$mac" "$cnt"
                fi
                ;;
                
            8)
                if [[ -z "$INTERFACE" ]]; then
                    print_error "No interface in monitor mode. Please enable monitor mode first."
                else
                    read -p "Enter BSSID: " bssid
                    
                    run_deauth_attack_all_clients "$INTERFACE"
                fi
                ;;
                
            9)
                if [[ -z "$INTERFACE" ]]; then
                    print_warning "No interface in monitor mode. Please enable monitor mode first."
                else
                    read -p "Enter BSSID (leave empty for all): " bssid
                    read -p "Scan duration [default: $DURATION]: " dur
                    dur=${dur:-$DURATION}
                    
                    capture_handshake "$INTERFACE" "$bssid" "$CHANNEL" "$dur"
                fi
                ;;
                
            10)
                if [[ -z "$INTERFACE" ]]; then
                    print_warning "No interface in monitor mode. Please enable monitor mode first."
                else
                    echo ""
                    set_color MAGENTA
                    set_bold
                    echo ""
                    echo "================================================"
                    echo "TOOLS MENU"
                    echo "================================================"
                    echo ""
                    echo "10a. WiFi Pineapple SSH Connection"
                    echo "10b. Flipper Zero Sync"
                    echo "10c. Exit Tools Menu"
                    echo ""
                    
                    read -p "Select tool [10a-10c]: " tool_choice
                    
                    case $tool_choice in
                        10a)
                            wifi_pineapple_ssh "$BSSID"
                            ;;
                        10b)
                            flipper_zero_sync "$INTERFACE"
                            ;;
                        10c)
                            echo ""
                            set_color RESET
                            reset_bold
                            break
                            ;;
                    esac
                    
                fi
                ;;
                
            11)
                print_success "Exiting GODSCRIPT..."
                exit 0
                ;;
                
            *)
                print_error "Invalid option. Please select a number between 1 and 11."
                ;;
        esac
        
    done
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

main() {
    echo ""
    show_banner
    
    # Check for root access first
    check_root_access || exit 1
    
    # Create captures directory if it doesn't exist
    create_captures_dir
    
    # Start main menu loop
    main_menu
}

# Run the script
main "$@"
