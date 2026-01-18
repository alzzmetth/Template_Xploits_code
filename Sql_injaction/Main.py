#!/usr/bin/env python3
import sys
import os
from colorama import Fore, Style, init

# Import module kita
from sql_inject import XvoidSQLScanner

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.RED}{Style.BRIGHT}
██████╗ ██╗   ██╗██╗  ██╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝██║  ██║██║  ██║
██████╔╝ ╚████╔╝ ███████║███████║
██╔═══╝   ╚██╔╝  ██╔══██║██╔══██║
██║        ██║   ██║  ██║██║  ██║
╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.RED}{'='*60}{Style.RESET_ALL}
{Fore.RED}    X-VOID SQL INJECTION SCANNER v3.0{Style.RESET_ALL}
{Fore.RED}    Professional Security Assessment Tool{Style.RESET_ALL}
{Fore.RED}{'='*60}{Style.RESET_ALL}
    """
    print(banner)

def show_menu():
    print(f"\n{Fore.RED}[MAIN MENU]{Style.RESET_ALL}")
    print(f"{Fore.RED}1. Scan single target{Style.RESET_ALL}")
    print(f"{Fore.RED}2. Scan multiple targets from file{Style.RESET_ALL}")
    print(f"{Fore.RED}3. View scan results{Style.RESET_ALL}")
    print(f"{Fore.RED}4. Update payloads/parameters{Style.RESET_ALL}")
    print(f"{Fore.RED}5. Exit{Style.RESET_ALL}")
    
    choice = input(f"\n{Fore.RED}[?] Select option: {Style.RESET_ALL}")
    return choice

def main():
    print_banner()
    
    # Inisialisasi scanner
    scanner = XvoidSQLScanner()
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            target = input(f"\n{Fore.RED}[?] Enter target URL: {Style.RESET_ALL}")
            print(f"{Fore.RED}[+] Loading payloads and parameters...{Style.RESET_ALL}")
            scanner.scan_target(target)
            
        elif choice == '2':
            file_path = input(f"\n{Fore.RED}[?] Enter targets file path: {Style.RESET_ALL}")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    targets = [line.strip() for line in f if line.strip()]
                
                print(f"{Fore.RED}[+] Found {len(targets)} targets{Style.RESET_ALL}")
                for target in targets:
                    scanner.scan_target(target)
            else:
                print(f"{Fore.RED}[!] File not found{Style.RESET_ALL}")
                
        elif choice == '3':
            scanner.view_results()
            
        elif choice == '4':
            print(f"\n{Fore.RED}[CONFIGURATION]{Style.RESET_ALL}")
            print(f"{Fore.RED}1. Edit payloads.txt{Style.RESET_ALL}")
            print(f"{Fore.RED}2. Edit params.txt{Style.RESET_ALL}")
            config_choice = input(f"\n{Fore.RED}[?] Select: {Style.RESET_ALL}")
            
            if config_choice == '1':
                os.system('nano payloads.txt' if os.name != 'nt' else 'notepad payloads.txt')
            elif config_choice == '2':
                os.system('nano params.txt' if os.name != 'nt' else 'notepad params.txt')
                
        elif choice == '5':
            print(f"\n{Fore.RED}[+] Exiting...{Style.RESET_ALL}")
            break
            
        else:
            print(f"{Fore.RED}[!] Invalid choice{Style.RESET_ALL}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        scanner = XvoidSQLScanner()
        if sys.argv[1] == '-sql' and len(sys.argv) > 2:
            print_banner()
            scanner.scan_target(sys.argv[2])
        elif sys.argv[1] == '-h':
            print_banner()
            print(f"\n{Fore.RED}[USAGE]{Style.RESET_ALL}")
            print(f"{Fore.RED}python main.py -sql <target_url>{Style.RESET_ALL}")
            print(f"{Fore.RED}python main.py              # Interactive mode{Style.RESET_ALL}")
    else:
        main()
