#!/usr/bin/env python3
import sys
import os
import time
from agent.task_executor import TaskExecutor

def main_menu():
    try:
        executor = TaskExecutor()
    except Exception as e:
        print(f"Error initializing Orchestrator: {e}")
        return 1

    # Map the ugly raw task names to Tactical UI names
    ui_map = {
        "handshake": "WPA Handshake Capture  (Muscle)",
        "audit": "Business Logic Audit   (Money)",
        "brain_sync": "OpenClaw Brain Sync    (Intelligence)"
    }

    while True:
        try:
            os.system('clear')
            print("============================================================")
            print("               SCRYPT KEEPER: BOTWAVE EMPIRE                ")
            print("                   [ HQ STATUS: ONLINE ]                    ")
            print("============================================================")
            
            task_info = executor.list_available_tasks()
            tasks = task_info.get("data", {}).get("tasks", [])
            
            for i, task in enumerate(tasks, 1):
                display_name = ui_map.get(task, task)
                print(f" {i}. {display_name}")
            
            print("============================================================")
            print(f" {len(tasks) + 1}. System Health Check    (Diagnostics)")
            print(f" {len(tasks) + 2}. Exit HQ")
            print("============================================================")

            choice = input("\n[Gringo@Empire] Select Option: ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(tasks):
                selected_task = tasks[int(choice) - 1]
                print(f"\n[!] Triggering {selected_task.upper()}...")
                result = executor.run_task(selected_task)
                
                # Format the output cleanly
                if result.get('status') == 'success':
                    print(f"\n[SUCCESS] {result.get('message')}")
                    if 'data' in result and result['data']:
                        print(f"Payload: {result['data']}")
                else:
                    print(f"\n[ERROR] {result.get('message')}")
                
                input("\nPress Enter to return...")

            elif choice == str(len(tasks) + 1):
                health = executor.health_check()
                print(f"\n[DIAGNOSTICS] {health.get('message')}")
                input("\nPress Enter to return...")
                
            elif choice == str(len(tasks) + 2):
                print("\nExiting HQ...")
                sys.exit(0)
                
            else:
                print("\nInvalid Selection.")
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"Fatal error in launcher: {e}")
        sys.exit(1)
