#!/usr/bin/env python3
import sys
import argparse
import json
from datetime import datetime
from utils import Banner, Colors, print_success, print_error, print_info, Loading
from network import NetworkTools

class XORZTracker:
    def __init__(self):
        self.tools = NetworkTools()
        self.last_result = None
    
    def track(self, target):
        Banner.show()
        
        if self.tools.validate_ip(target):
            return self.track_ip(target)
        else:
            return self.track_domain(target)
    
    def track_ip(self, ip):
        print(f"{Colors.CYAN}[TARGET]{Colors.RESET} {ip}\n")
        
        results = {'ip': ip, 'timestamp': datetime.now().isoformat()}
        
        Loading.spin("Getting geolocation", 1)
        geo = self.tools.get_geolocation(ip)
        if geo:
            results['geolocation'] = geo
            self._display_geolocation(geo)
        
        Loading.spin("Reverse DNS lookup", 0.5)
        reverse = self.tools.reverse_dns_lookup(ip)
        if reverse:
            results['reverse_dns'] = reverse
            self._display_reverse_dns(reverse)
        
        print_info("Port scanning started")
        try:
            ports = self.tools.port_scan(ip)
            results['open_ports'] = ports
            self._display_ports(ports)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[~] Port scan interrupted{Colors.RESET}")
            results['open_ports'] = []
        
        self.last_result = results
        self._save_results(results)
        
        return results
    
    def track_domain(self, domain):
        print(f"{Colors.CYAN}[TARGET]{Colors.RESET} {domain}\n")
        
        Loading.spin("Resolving domain", 1)
        resolution = self.tools.resolve_domain(domain)
        
        if not resolution:
            print_error("Failed to resolve domain")
            return None
        
        results = {
            'domain': domain,
            'resolution': resolution,
            'timestamp': datetime.now().isoformat()
        }
        
        print_success(f"Resolved to: {', '.join(resolution['ips'])}")
        
        if resolution['primary_ip']:
            print(f"\n{Colors.YELLOW}[PRIMARY IP]{Colors.RESET} {resolution['primary_ip']}")
            ip_info = self.tools.get_geolocation(resolution['primary_ip'])
            if ip_info:
                results['ip_info'] = ip_info
                self._display_geolocation(ip_info)
        
        Loading.spin("Getting DNS records", 1)
        dns_records = self.tools.get_dns_records(resolution['domain'])
        results['dns_records'] = dns_records
        self._display_dns_records(dns_records)
        
        Loading.spin("Checking web server", 1)
        web_info = self.tools.check_web_info(resolution['domain'])
        if web_info:
            results['web_info'] = web_info
            self._display_web_info(web_info)
        
        self.last_result = results
        self._save_results(results)
        
        return results
    
    def show_my_ip(self):
        Banner.show()
        Loading.spin("Detecting public IP", 1)
        
        ip = self.tools.get_public_ip()
        if ip:
            print_success(f"Public IP: {ip}")
            
            geo = self.tools.get_geolocation(ip)
            if geo:
                self._display_geolocation(geo)
            
            print_info("Local network info")
            local_ips = self._get_local_ips()
            for local_ip in local_ips[:3]:
                print(f"  {local_ip}")
            
            return {'ip': ip, 'geolocation': geo, 'local_ips': local_ips}
        else:
            print_error("Could not determine public IP")
            return None
    
    def show_docs(self):
        Banner.show()
        
        docs = f"""
{Colors.CYAN}XORZ IP TRACKER - Documentation{Colors.RESET}

{Colors.GREEN}COMMANDS:{Colors.RESET}
{Colors.YELLOW}-track <target>{Colors.RESET}
    Track IP address or domain
    Example: -track 8.8.8.8
    Example: -track google.com

{Colors.YELLOW}-webtrack <domain>{Colors.RESET}
    Track domain with DNS and web info
    Example: -webtrack github.com

{Colors.YELLOW}-myip{Colors.RESET}
    Show your public IP with geolocation

{Colors.YELLOW}-docs{Colors.RESET}
    Show this documentation

{Colors.YELLOW}-h{Colors.RESET}
    Show help menu

{Colors.GREEN}FEATURES:{Colors.RESET}
• scan IP geolocation
• Port scanning
• DNS record lookup
• Reverse DNS
• Web server detection
• Local network discovery
• JSON export

{Colors.GREEN}EXAMPLES:{Colors.RESET}
{Colors.CYAN}python main.py -track 8.8.8.8{Colors.RESET}
{Colors.CYAN}python main.py -webtrack google.com{Colors.RESET}
{Colors.CYAN}python main.py -myip{Colors.RESET}
{Colors.CYAN}python main.py -docs{Colors.RESET}

{Colors.GREEN}DEVELOPER:{Colors.RESET} @alzzmaret
{Colors.GREEN}TOOL:{Colors.RESET} XORZ IP Tracker v2.0
"""
        print(docs)
    
    def show_help(self):
        Banner.show()
        
        help_text = f"""
{Colors.CYAN}Available Commands:{Colors.RESET}

{Colors.YELLOW}-track <target>{Colors.RESET}
    Track IP address or domain

{Colors.YELLOW}-webtrack <domain>{Colors.RESET}
    Track domain with full DNS analysis

{Colors.YELLOW}-myip{Colors.RESET}
    Display your public IP information

{Colors.YELLOW}-docs{Colors.RESET}
    Show full documentation

{Colors.YELLOW}-h{Colors.RESET}
    Show this help menu

{Colors.CYAN}Usage Examples:{Colors.RESET}
python main.py -track 192.168.1.1
python main.py -webtrack youtube.com
python main.py -myip
python main.py -docs
"""
        print(help_text)
    
    def _display_geolocation(self, geo):
        Banner.show_section("GEOLOCATION")
        print(f"{Colors.GREEN}IP:{Colors.RESET} {geo.get('ip', 'Unknown')}")
        print(f"{Colors.GREEN}Location:{Colors.RESET} {geo.get('city', 'Unknown')}, {geo.get('region', 'Unknown')}, {geo.get('country', 'Unknown')}")
        print(f"{Colors.GREEN}ISP:{Colors.RESET} {geo.get('isp', 'Unknown')}")
        print(f"{Colors.GREEN}Organization:{Colors.RESET} {geo.get('org', 'Unknown')}")
        print(f"{Colors.GREEN}Coordinates:{Colors.RESET} {geo.get('lat', 0)}, {geo.get('lon', 0)}")
        print(f"{Colors.GREEN}Timezone:{Colors.RESET} {geo.get('timezone', 'Unknown')}")
    
    def _display_reverse_dns(self, reverse):
        Banner.show_section("REVERSE DNS")
        print(f"{Colors.GREEN}Hostname:{Colors.RESET} {reverse['hostname']}")
        if reverse['aliases']:
            print(f"{Colors.GREEN}Aliases:{Colors.RESET} {', '.join(reverse['aliases'])}")
    
    def _display_ports(self, ports):
        Banner.show_section("OPEN PORTS")
        if ports:
            for port_info in ports:
                print(f"{Colors.GREEN}Port {port_info['port']:5}{Colors.RESET} → {port_info['service']}")
        else:
            print(f"{Colors.YELLOW}No open ports detected{Colors.RESET}")
    
    def _display_dns_records(self, records):
        Banner.show_section("DNS RECORDS")
        
        if records.get('A'):
            print(f"{Colors.GREEN}A Records:{Colors.RESET}")
            for ip in records['A']:
                print(f"  {ip}")
        
        if records.get('MX'):
            print(f"\n{Colors.GREEN}MX Records:{Colors.RESET}")
            for mx in records['MX']:
                print(f"  {mx['preference']} {mx['exchange']}")
        
        if records.get('NS'):
            print(f"\n{Colors.GREEN}NS Records:{Colors.RESET}")
            for ns in records['NS']:
                print(f"  {ns}")
    
    def _display_web_info(self, web_info):
        Banner.show_section("WEB SERVER")
        print(f"{Colors.GREEN}Status:{Colors.RESET} {web_info['status_code']}")
        print(f"{Colors.GREEN}Server:{Colors.RESET} {web_info['server']}")
        print(f"{Colors.GREEN}Content Type:{Colors.RESET} {web_info['content_type']}")
    
    def _get_local_ips(self):
        import socket
        local_ips = []
        try:
            hostname = socket.gethostname()
            local_ips.append(f"Hostname: {hostname}")
            
            addrinfo = socket.getaddrinfo(hostname, None)
            for info in addrinfo:
                ip = info[4][0]
                if ip not in local_ips and not ip.startswith('127.'):
                    local_ips.append(ip)
        except:
            pass
        
        return local_ips if local_ips else ["No local IPs found"]
    
    def _save_results(self, results):
        filename = f"xorz_track_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print_success(f"Results saved to {filename}")

def main():
    tracker = XORZTracker()
    
    if len(sys.argv) < 2:
        tracker.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "-track":
        if len(sys.argv) != 3:
            print(f"{Colors.RED}Usage: python main.py -track <IP/DOMAIN>{Colors.RESET}")
            return
        tracker.track(sys.argv[2])
    
    elif command == "-webtrack":
        if len(sys.argv) != 3:
            print(f"{Colors.RED}Usage: python main.py -webtrack <DOMAIN>{Colors.RESET}")
            return
        tracker.track_domain(sys.argv[2])
    
    elif command == "-myip":
        tracker.show_my_ip()
    
    elif command == "-docs":
        tracker.show_docs()
    
    elif command == "-h":
        tracker.show_help()
    
    else:
        print(f"{Colors.RED}[!] Unknown command: {command}{Colors.RESET}")
        print(f"{Colors.YELLOW}Use -h for help{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Interrupted{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {str(e)}{Colors.RESET}")
