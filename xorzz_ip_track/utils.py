from colorama import init, Fore, Style, Back
import sys
import time
import os

init(autoreset=True)

class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL

class Banner:
    @staticmethod
    def show():
        banner = f"""
{Colors.RED}__  __      ___       ____      _____  
\\ \\/ /     / _ \\     |  _ \\    |__  /  
 \\  /     | | | |    | |_) |     / /   
 /  \\     | |_| |    |  _ <     / /_   
/_/\\_\\     \\___/     |_| \\_\\   /____|{Colors.RESET}
═══════════════════════════════════════
{Colors.CYAN}XORZ IP Tracker{Colors.RESET} | Developer: @alzzmaret
"""
        print(banner)
    
    @staticmethod
    def show_section(title):
        print(f"\n{Colors.CYAN}╔{'═' * (len(title) + 2)}╗")
        print(f"║ {title} ║")
        print(f"╚{'═' * (len(title) + 2)}╝{Colors.RESET}")

class Loading:
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    @staticmethod
    def spin(text="", duration=1.5):
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            frame = Loading.frames[i % len(Loading.frames)]
            sys.stdout.write(f"\r{Colors.YELLOW}{frame}{Colors.RESET} {text}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write(f"\r{Colors.GREEN}✓{Colors.RESET} {text}\n")

def print_success(msg):
    print(f"{Colors.GREEN}[+]{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[!]{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[*]{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[~]{Colors.RESET} {msg}")
