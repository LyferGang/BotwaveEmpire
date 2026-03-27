#!/usr/bin/env python3
import sys
import os
import time
from agent.task_executor import TaskExecutor

def main_menu():
    # Initialize the Spinal Cord
    try:
        executor = TaskExecutor()
    except Exception as e:
        print(f"Error initializing Orchestrator: {e}")
        return

    while True:
        os.system('clear')
        print("==========================================")
        print("     SCRYPT KEEPER: BOTWAVE EMPIRE        ")
        print("          [ HQ STATUS: ONLINE ]           ")
        print("==========================================")
        print("1. WPA Handshake Capture  (Muscle)")
        print("2. Business Logic Audit   (Money)")
        print("3. OpenClaw Brain Sync    (Intelligence)")
        print("4. Network Recon Scan     (Eyes)")
        print("5. Exit")
        print("==========================================")
        
        choice = input("\n[Gringo@Empire] Select Option: ")
        
        if choice == '1':
            print("\n[!] Triggering Handshake Capture...")
            print(executor.run_task("handshake"))
            input("\nPress Enter to return...")
        elif choice == '2':
            print("\n[!] Triggering Business Audit...")
            print(executor.run_task("audit"))
            input("\nPress Enter to return...")
        elif choice == '4':
            print("\n[!] Triggering Recon Scan...")
            print(executor.run_task("network_recon"))
            input("\nPress Enter to return...")
        elif choice == '5':
            print("Exiting HQ...")
            sys.exit()
        else:
            print("Invalid Selection.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
