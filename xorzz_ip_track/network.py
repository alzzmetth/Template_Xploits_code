import socket
import requests
import json
from urllib.parse import urlparse
import concurrent.futures
import dns.resolver
from utils import Loading, print_error

class NetworkTools:
    @staticmethod
    def validate_ip(ip):
        try:
            socket.inet_aton(ip)
            return True
        except:
            return False
    
    @staticmethod
    def get_public_ip():
        services = [
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://checkip.amazonaws.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=3)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        return None
    
    @staticmethod
    def resolve_domain(domain):
        try:
            if not domain.startswith(('http://', 'https://')):
                domain = 'http://' + domain
            
            parsed = urlparse(domain)
            domain_name = parsed.netloc or parsed.path
            
            ips = []
            try:
                answers = dns.resolver.resolve(domain_name, 'A')
                for rdata in answers:
                    ips.append(str(rdata))
            except:
                pass
            
            if not ips:
                ips.append(socket.gethostbyname(domain_name))
            
            return {
                'domain': domain_name,
                'ips': ips,
                'primary_ip': ips[0] if ips else None
            }
        except Exception as e:
            print_error(f"Domain resolution failed: {str(e)}")
            return None
    
    @staticmethod
    def get_geolocation(ip):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'ip': ip,
                        'country': data.get('country', 'Unknown'),
                        'country_code': data.get('countryCode', ''),
                        'region': data.get('regionName', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'zip': data.get('zip', ''),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0),
                        'timezone': data.get('timezone', ''),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'as': data.get('as', '')
                    }
        except:
            pass
        
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                loc = data.get('loc', '0,0').split(',')
                return {
                    'ip': ip,
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'loc': data.get('loc', '0,0'),
                    'org': data.get('org', 'Unknown'),
                    'postal': data.get('postal', ''),
                    'timezone': data.get('timezone', ''),
                    'lat': float(loc[0]) if len(loc) > 0 else 0,
                    'lon': float(loc[1]) if len(loc) > 1 else 0
                }
        except:
            pass
        
        return None
    
    @staticmethod
    def port_scan(ip, ports=None, timeout=1, max_workers=100):
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443]
        
        open_ports = []
        
        def check_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                return (port, result == 0)
            except:
                return (port, False)
        
        Loading.spin(f"Scanning {len(ports)} ports", 0.5)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            for future in concurrent.futures.as_completed(futures):
                port, is_open = future.result()
                if is_open:
                    open_ports.append(port)
        
        services = []
        for port in open_ports:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            services.append({'port': port, 'service': service})
        
        return services
    
    @staticmethod
    def get_dns_records(domain):
        records = {}
        
        try:
            answers = dns.resolver.resolve(domain, 'A')
            records['A'] = [str(rdata) for rdata in answers]
        except:
            records['A'] = []
        
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            records['MX'] = []
            for rdata in answers:
                records['MX'].append({
                    'preference': rdata.preference,
                    'exchange': str(rdata.exchange)
                })
        except:
            records['MX'] = []
        
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            records['TXT'] = []
            for rdata in answers:
                for txt_string in rdata.strings:
                    records['TXT'].append(txt_string.decode('utf-8'))
        except:
            records['TXT'] = []
        
        try:
            answers = dns.resolver.resolve(domain, 'NS')
            records['NS'] = [str(rdata) for rdata in answers]
        except:
            records['NS'] = []
        
        return records
    
    @staticmethod
    def reverse_dns_lookup(ip):
        try:
            hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
            return {
                'hostname': hostname,
                'aliases': aliaslist,
                'ips': ipaddrlist
            }
        except:
            return None
    
    @staticmethod
    def check_web_info(domain):
        try:
            response = requests.get(f'https://{domain}', timeout=3, verify=False)
        except:
            try:
                response = requests.get(f'http://{domain}', timeout=3)
            except:
                return None
        
        info = {
            'status_code': response.status_code,
            'server': response.headers.get('Server', 'Unknown'),
            'content_type': response.headers.get('Content-Type', 'Unknown')
        }
        
        return info
