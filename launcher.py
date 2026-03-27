#!/usr/bin/env python3
import sys
import os
import time
from agent.task_executor import TaskExecutor

def main_menu():
    # Initialize the Spinal Cord
    executor = None
    
    try:
        executor = TaskExecutor()
    except Exception as e:
        print(f"Error initializing Orchestrator: {e}")
        return 1

    while True:
        try:
            os.system('clear')
            
            # Display header
            print("=" * 60)
            print("     SCRYPT KEEPER: BOTWAVE EMPIRE")
            print("          [ HQ STATUS: ONLINE ]")
            print("=" * 60)
            
            # List available tasks
            task_info = executor.list_available_tasks()
            if task_info.get("status") == "success":
                tasks = task_info["data"]["tasks"]
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task}")
                
                print("=" * 60)
            
            # Get user input
            choice = input("\n[Gringo@Empire] Select Option: ").strip()
            
            try:
                if choice == '1':
                    result = executor.run_task("handshake")
                    print(f"\nResult: {result}")
                    input("\nPress Enter to return...")
                
                elif choice == '2':
                    result = executor.run_task("audit")
                    print(f"\nResult: {result}")
                    input("\nPress Enter to return...")
                
                elif choice == '3':
                    result = executor.run_task("brain_sync")
                    print(f"\nResult: {result}")
                    input("\nPress Enter to return...")
                
                elif choice == '4':
                    # Health check option
                    health_result = executor.health_check()
                    if health_result.get("status") == "success":
                        data = health_result["data"]
                        print(f"\nHealth Check: {data['healthy_modules']}/{data['total_modules']} modules healthy.")
                    else:
                        print(f"\nHealth Check Failed: {health_result}")
                    input("\nPress Enter to return...")
                
                elif choice == '5':
                    # Exit option
                    shutdown_result = executor.shutdown()
                    if shutdown_result.get("status") == "success":
                        print("\nExiting HQ...")
                        sys.exit(0)
                    else:
                        print(f"\nShutdown warning: {shutdown_result}")
                
                elif choice == '6':
                    # Reload registry option
                    reload_result = executor.reload_registry()
                    if reload_result.get("status") == "success":
                        tasks = reload_result["data"]["tasks"]
                        print(f"Registry reloaded. Available tasks: {', '.join(tasks)}")
                    else:
                        print(f"\nReload failed: {reload_result}")
                
                elif choice == '7':
                    # Status option
                    status_result = executor.get_task_info("status")
                    if status_result.get("status") == "success":
                        data = status_result["data"]
                        print(f"Task Info: {data['name']} ({data['module']})")
                
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
