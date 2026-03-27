#!/bin/bash

# =============================================================================
# GODSCRIPT - Wireless Reconnaissance Tool
# A comprehensive, menu-driven Bash script for wireless security testing
# =============================================================================

# =============================================================================
# TERMINAL STYLING (tput)
# =============================================================================

set_color() {
    local color=$1
    case $color in
        RED)     tput setaf 1 ;;
        GREEN)   tput setaf 2 ;;
        YELLOW)  tput setaf 3 ;;
        BLUE)    tput setaf 4 ;;
        MAGENTA) tput setaf 5 ;;
        CYAN)    tput setaf 6 ;;
        WHITE)   tput setaf 7 ;;
        RESET)   tput sgr0 ;;
    esac
}

# =============================================================================
# GRINGO ASCII BANNER
# =============================================================================

show_banner() {
    echo ""
    echo "                                                                                   "
    echo "                                                                                   "
    echo "                                                                                   "
    echo "  _____ _   _ _____ _______ ____  __     ___  ___________                       "
    echo " |  ___| | | |_   _|__  __/ ___||  \   / _ \|_   _|_______|                      "
    echo " | |_  | |_| | | |    \ \/ /\___| | | | (_) | | |      __"
    echo " |  _| |  _  | | |     >  <      | | | |_| | | |    / ___|"
    echo " | |   | | | | | |    /  \\ \_____| | |\__  || | |   /_/   "
    echo " |_|   |_| |_|___|   /_/\\_\\       |_| |____||_| |____/     "
    echo ""
    echo "                                                                                   "
    echo "                    GRINGO WIRELESS RECONNAISSANCE TOOL                         "
    echo "                    Version 2.0 - Professional Red-Team Edition                  "
    echo "                                                                                   "
    echo "                                                                                   "
}

# =============================================================================
# COLOR FUNCTIONS (tput)
# =============================================================================

print_header() {
    set_color BLUE
    echo ""
    echo "================================================"
    echo "$1"
    echo "================================================"
    echo ""
    set_color RESET
}

print_success() {
    set_color GREEN
    echo "$1"
    set_color RESET
}

print_warning() {
    set_color YELLOW
    echo "$1"
    set_color RESET
}

print_error() {
    set_color RED
    echo "$1"
    set_color RESET
}

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

INTERFACE=""
MONITOR_MODE=false
SCAN_RESULTS=""
DEAUTH_TARGET=""
CLIENT_MAC=""
BSSID=""
CHANNEL=6
DURATION="30s"
OUTPUT_FILE=""
CAPTURES_DIR="./captures"
GRINGO_VERSION="2.0"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

check_root_access() {
    print_header "Checking Root Access"
    
    if [[ $EUID -eq 0 ]]; then
        print_success "Running as root - All operations permitted"
    else
        print_warning "Not running as root. Some features may be limited."
        print_error "Please run with sudo for full functionality:"
        echo ""
        echo "Example: sudo $0"
        return 1
    fi
}

check_dependencies() {
    print_header "Checking Dependencies"
    
    local deps=("airmon-ng" "airodump-ng" "aireplay-ng" "wpa_supplicant" "hostapd")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            print_warning "$dep not found. Please install:"
            echo ""
            case "$dep" in
                "airmon-ng")
                    echo "  apt-get install aircrack-ng"
                    ;;
                "airodump-ng")
                    echo "  apt-get install aircrack-ng"
                    ;;
                "aireplay-ng")
                    echo "  apt-get install aircrack-ng"
                    ;;
                *)
                    echo "  $dep package manager command"
                    ;;
            esac
            missing+=("$dep")
        else
            print_success "$dep found ✓"
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "${#missing[@]} dependency/dependencies missing:"
        echo ""
        for dep in "${missing[@]}"; do
            print_warning "  $dep"
        done
        return 1
    fi
    
    print_success "All dependencies found ✓"
}

create_captures_dir() {
    if [[ ! -d "$CAPTURES_DIR" ]]; then
        mkdir -p "$CAPTURES_DIR"
        print_success "Created captures directory: $CAPTURES_DIR"
    else
        print_warning "Captures directory already exists: $CAPTURES_DIR"
    fi
}

# =============================================================================
# INTERFACE MANAGEMENT
# =============================================================================

list_interfaces() {
    print_header "Available Network Interfaces"
    
    local interfaces=$(ip link show | grep -E '^[0-9]+:|lo:' | awk '{print $2}' | tr -d ':' | sort)
    
    if [[ -z "$interfaces" ]]; then
        print_error "No network interfaces found"
        return 1
    fi
    
    echo ""
    for iface in $interfaces; do
        local type=$(ip link show "$iface" 2>/dev/null | grep -oP 'type \K[^ ]+' || echo "unknown")
        printf "%-30s %-15s\n" "$iface" "$type"
    done
    
    echo ""
}

kill_conflicting_processes() {
    local iface=$1
    
    print_header "Checking for Conflicting Processes on $iface"
    
    # Check for existing airmon-ng processes
    if pgrep -f "airmon.*$iface" > /dev/null; then
        print_warning "Found conflicting process: airmon-ng on $iface"
        
        # Kill the process
        local pid=$(pgrep -f "airmon.*$iface")
        kill -9 "$pid" 2>/dev/null
        
        print_success "Killed conflicting process (PID: $pid)"
    fi
    
    # Check for monitor mode already enabled
    if ip link show "$iface" | grep -qP 'mode \Kmonitor'; then
        print_warning "$iface is already in monitor mode"
        
        # Stop airmon-ng if running
        local pid=$(pgrep -f "airmon.*$iface")
        kill -9 "$pid" 2>/dev/null
        
        return 0
    fi
    
    print_success "No conflicting processes found on $iface"
}

enable_monitor_mode() {
    local iface=$1
    
    print_header "Enabling Monitor Mode on $iface"
    
    # Check if interface already in monitor mode
    if ip link show "$iface" | grep -qP 'mode \Kmonitor'; then
        print_success "$iface is already in monitor mode"
        return 0
    fi
    
    # Kill conflicting processes first
    kill_conflicting_processes "$iface" || true
    
    # Try to enable monitor mode using airmon-ng
    print_warning "Attempting to enable monitor mode..."
    
    if ! airmon-ng start "$iface"; then
        print_error "Failed to enable monitor mode automatically"
        echo ""
        echo "Manual attempt:"
        echo "  $airmon-ng start $iface"
        return 1
    fi
    
    # Wait for interface to stabilize
    sleep 2
    
    local status=$(ip link show "$iface" | grep -oP 'mode \K[^ ]+')
    
    if [[ "$status" == *"monitor"* ]]; then
        print_success "Monitor mode enabled successfully on $iface"
        INTERFACE="$iface"
        MONITOR_MODE=true
        return 0
    else
        print_error "Interface is not in monitor mode: $status"
        return 1
    fi
}

disable_monitor_mode() {
    local iface=$1
    
    if [[ -z "$INTERFACE" ]]; then
        print_warning "No interface currently in monitor mode"
        return 0
    fi
    
    print_header "Disabling Monitor Mode on $INTERFACE"
    
    airmon-ng stop "$INTERFACE" || true
    
    # Clean up any remaining processes
    kill_conflicting_processes "$INTERFACE" || true
    
    print_success "Monitor mode disabled on $INTERFACE"
}

# =============================================================================
# WIFI SCANNING (airodump-ng)
# =============================================================================

run_airodump_scan() {
    local iface=$1
    local bssid=$2
    local channel=$3
    local duration=${4:-$DURATION}
    
    print_header "Starting airodump-ng Scan"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    # Build command arguments
    local args=("-w" "${OUTPUT_FILE:-scan}" "-c" "$channel")
    
    if [[ -n "$bssid" ]]; then
        args+=("--bssid" "$bssid")
    fi
    
    if [[ -n "$duration" ]]; then
        args+=("-t" "$duration")
    fi
    
    # Run airodump-ng
    print_success "Executing: airodump-ng ${args[*]}"
    
    echo ""
    echo "Press Ctrl+C to stop scan..."
    echo ""
    
    airodump-ng "${args[@]}" &
    local scan_pid=$!
    
    while kill -0 $scan_pid 2>/dev/null; do
        sleep 1
    done
    
    wait $scan_pid || true
    
    print_success "Scan completed. Results saved to: ${OUTPUT_FILE:-scan}"
}

run_wps_scan() {
    local iface=$1
    
    print_header "Starting WPS Scan"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    echo ""
    echo "Press Ctrl+C to stop scan..."
    echo ""
    
    wps_scan --channel $CHANNEL &
    local scan_pid=$!
    
    while kill -0 $scan_pid 2>/dev/null; do
        sleep 1
    done
    
    wait $scan_pid || true
    
    print_success "WPS scan completed"
}

# =============================================================================
# DEAUTH ATTACK (aireplay-ng)
# =============================================================================

run_deauth_attack() {
    local iface=$1
    local target_bssid=$2
    local target_mac=$3
    local count=${4:-50}
    
    print_header "Starting Deauthentication Attack"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    # Build command arguments
    local args=("-a" "$target_bssid" "-c" "$count")
    
    if [[ -n "$target_mac" ]]; then
        args+=("--macdst" "$target_mac")
    fi
    
    echo ""
    echo "Target BSSID: $target_bssid"
    echo "Target MAC: ${target_mac:-any}"
    echo "Deauth packets: $count"
    echo ""
    
    print_success "Executing: aireplay-ng ${args[*]}"
    
    # Run deauth attack
    aireplay-ng "${args[@]}" &
    local attack_pid=$!
    
    while kill -0 $attack_pid 2>/dev/null; do
        sleep 1
    done
    
    wait $attack_pid || true
    
    print_success "Deauthentication attack completed"
}

run_deauth_attack_all_clients() {
    local iface=$1
    
    print_header "Starting Deauthentication Attack (All Clients)"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    echo ""
    echo "Press Ctrl+C to stop attack..."
    echo ""
    
    # Run deauth attack targeting all clients
    aireplay-ng --deauthtx -a "$BSSID" &
    local attack_pid=$!
    
    while kill -0 $attack_pid 2>/dev/null; do
        sleep 1
    done
    
    wait $attack_pid || true
    
    print_success "Deauthentication attack completed (all clients)"
}

# =============================================================================
# WIFI PINEAPPLE INTEGRATION (Placeholder)
# =============================================================================

wifi_pineapple_scan() {
    local iface=$1
    
    print_header "WiFi Pineapple Integration"
    
    if [[ -z "$INTERFACE" ]]; then
        print_warning "No interface in monitor mode. Please enable monitor mode first."
    fi
    
    echo ""
    print_warning "[PLACEHOLDER] WiFi Pineapple integration not fully implemented"
    echo ""
    echo "Available commands:"
    echo "  pineapple scan <channel>"
    echo "  pineapple attack <target>"
    echo "  pineapple status"
    echo ""
    
    # Placeholder implementation would go here
    print_warning "To enable WiFi Pineapple integration, please implement:"
    echo "  - pineapple_scan function"
    echo "  - pineapple_attack function"
    echo "  - pineapple_status function"
}

wifi_pineapple_ssh() {
    local target=$1
    
    print_header "WiFi Pineapple SSH Connection"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    echo ""
    print_warning "[PLACEHOLDER] WiFi Pineapple SSH connection not fully implemented"
    echo ""
    echo "To implement, add:"
    echo "  pineapple_ssh <target_ip>"
}

# =============================================================================
# FLIPPER ZERO INTEGRATION (Placeholder)
# =============================================================================

flipper_zero_scan() {
    local iface=$1
    
    print_header "Flipper Zero Integration"
    
    if [[ -z "$INTERFACE" ]]; then
        print_warning "No interface in monitor mode. Please enable monitor mode first."
    fi
    
    echo ""
    print_warning "[PLACEHOLDER] Flipper Zero integration not fully implemented"
    echo ""
    echo "Available commands:"
    echo "  flipper scan <channel>"
    echo "  flipper attack <target>"
    echo "  flipper status"
    echo ""
    
    # Placeholder implementation would go here
    print_warning "To enable Flipper Zero integration, please implement:"
    echo "  - flipper_scan function"
    echo "  - flipper_attack function"
    echo "  - flipper_status function"
}

flipper_zero_deauth() {
    local target=$1
    
    print_header "Flipper Zero Deauthentication Attack"
    
    if [[ -z "$INTERFACE" ]]; then
        print_error "No interface in monitor mode. Please enable monitor mode first."
        return 1
    fi
    
    echo ""
    print_warning "[PLACEHOLDER] Flipper Zero deauth attack not fully implemented"
    echo ""
    echo "To implement, add:"
    echo "  flipper_deauth <target_bssid>"
}

flipper_zero_sync() {
    local device=$1
    
    print_header "Flipper Zero Sync"
    
    if [[ -z "$INTERFACE" ]]; then
        print_warning "No interface in monitor mode. Please enable monitor mode first."
    fi
    
    echo ""
    print_warning "[PLACEHOLDER] Flipper Zero sync not fully implemented"
    echo ""
    echo "To implement, add:"
    echo "  flipper_sync <device_id>"
}

# =============================================================================
# MAIN MENU SYSTEM
# =============================================================================

show_menu() {
    set_color BLUE
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
    echo "9. WiFi Pineapple Integration"
    echo "10. Flipper Zero Integration"
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
                if [[ -z "$INTERFACE" ]]; then
                    print_warning "No interface selected. Please select an interface from the list."
                else
                    enable_monitor_mode "$INTERFACE"
                fi
                ;;
                
            4)
                disable_monitor_mode "$INTERFACE"
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
                    wifi_pineapple_scan "$INTERFACE"
                fi
                ;;
                
            10)
                if [[ -z "$INTERFACE" ]]; then
                    print_warning "No interface in monitor mode. Please enable monitor mode first."
                else
                    flipper_zero_scan "$INTERFACE"
                fi
                ;;
                
            11)
                print_success "Exiting Godscript..."
                exit 0
                ;;
                
            *)
                print_error "Invalid option. Please select a number between 1 and 11."
                ;;
        esac
        
        echo ""
    done
}

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

main() {
    # Check for root access first
    check_root_access
    
    # Check dependencies
    check_dependencies || true
    
    # Create captures directory
    create_captures_dir
    
    # Start main menu loop
    main_menu
}

# Run the script if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
