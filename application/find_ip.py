#!/usr/bin/env python3
import socket
import subprocess
import platform
import re

def get_ip_methods():
    """Try multiple methods to get the local IP address"""
    methods = []
    
    # Method 1: Socket connection (most reliable)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            methods.append(("Socket connection", ip))
    except Exception as e:
        methods.append(("Socket connection", f"Failed: {e}"))
    
    # Method 2: hostname resolution
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip != "127.0.0.1":
            methods.append(("Hostname resolution", ip))
        else:
            methods.append(("Hostname resolution", "Returned localhost"))
    except Exception as e:
        methods.append(("Hostname resolution", f"Failed: {e}"))
    
    # Method 3: Platform-specific commands
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        try:
            # Try different interfaces
            interfaces = ['en1', 'en2', 'en3', 'wlan0', 'wifi0']
            for interface in interfaces:
                try:
                    result = subprocess.run(['ifconfig', interface], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if match:
                            ip = match.group(1)
                            if not ip.startswith('127.'):
                                methods.append((f"macOS ifconfig {interface}", ip))
                except:
                    continue
            
            # Try route command
            try:
                result = subprocess.run(['route', 'get', 'default'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    interface_match = re.search(r'interface: (\w+)', result.stdout)
                    if interface_match:
                        interface = interface_match.group(1)
                        result2 = subprocess.run(['ifconfig', interface], 
                                               capture_output=True, text=True, timeout=5)
                        if result2.returncode == 0:
                            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result2.stdout)
                            if match:
                                ip = match.group(1)
                                if not ip.startswith('127.'):
                                    methods.append((f"macOS route+ifconfig {interface}", ip))
            except:
                pass
                
        except Exception as e:
            methods.append(("macOS commands", f"Failed: {e}"))
    
    elif system == "linux":
        try:
            # Try ip command
            result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', result.stdout)
                if match:
                    ip = match.group(1)
                    methods.append(("Linux ip route", ip))
        except:
            pass
        
        try:
            # Try hostname command
            result = subprocess.run(['hostname', '-I'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ips = result.stdout.strip().split()
                for ip in ips:
                    if not ip.startswith('127.') and '.' in ip:
                        methods.append(("Linux hostname -I", ip))
                        break
        except:
            pass
    
    elif system == "windows":
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                matches = re.findall(r'IPv4 Address.*?:\s*(\d+\.\d+\.\d+\.\d+)', result.stdout)
                for ip in matches:
                    if not ip.startswith('127.') and not ip.startswith('169.254'):
                        methods.append(("Windows ipconfig", ip))
        except Exception as e:
            methods.append(("Windows ipconfig", f"Failed: {e}"))
    
    return methods

def get_network_interfaces():
    """Get all network interfaces"""
    try:
        import netifaces
        interfaces = []
        for interface in netifaces.interfaces():
            try:
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for addr in addresses[netifaces.AF_INET]:
                        ip = addr['addr']
                        if not ip.startswith('127.'):
                            interfaces.append((interface, ip))
            except:
                continue
        return interfaces
    except ImportError:
        return [("netifaces", "Not installed - pip install netifaces")]

def main():
    print("🔍 Finding your IP address using multiple methods...\n")
    print("=" * 60)
    
    # Try built-in methods
    methods = get_ip_methods()
    
    print("📍 IP Address Detection Results:")
    print("-" * 40)
    
    found_ips = set()
    for method, result in methods:
        print(f"{method:25}: {result}")
        if result and not result.startswith("Failed") and not result.startswith("Returned"):
            # Validate IP format
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', result):
                found_ips.add(result)
    
    print("\n" + "=" * 60)
    
    # Try netifaces if available
    interfaces = get_network_interfaces()
    if interfaces and not any("Not installed" in str(i) for i in interfaces):
        print("\n🌐 Network Interfaces:")
        print("-" * 40)
        for interface, ip in interfaces:
            print(f"{interface:15}: {ip}")
            found_ips.add(ip)
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("-" * 40)
    
    if found_ips:
        print("✅ Found IP addresses:")
        for ip in sorted(found_ips):
            print(f"   • {ip}")
        
        # Get the most likely IP (not 192.168.x.x if others exist)
        likely_ip = None
        for ip in found_ips:
            if not ip.startswith('192.168.'):
                likely_ip = ip
                break
        if not likely_ip:
            likely_ip = list(found_ips)[0]
        
        print(f"\n🚀 Most likely IP for external access: {likely_ip}")
        print(f"📱 Use this URL from your mobile: http://{likely_ip}:8000")
        
    else:
        print("❌ No valid IP addresses found")
        print("💡 Try these manual commands:")
        system = platform.system().lower()
        if system == "darwin":
            print("   ifconfig | grep 'inet ' | grep -v 127.0.0.1")
        elif system == "linux":
            print("   ip addr show | grep 'inet ' | grep -v 127.0.0.1")
        elif system == "windows":
            print("   ipconfig | findstr IPv4")
    
    print("\n" + "=" * 60)
    print("💡 Tips:")
    print("• If connected via mobile hotspot, look for 192.168.43.x or 192.168.x.x")
    print("• If connected via Wi-Fi router, look for 192.168.1.x or 10.x.x.x")
    print("• Make sure your server binds to 0.0.0.0, not localhost")

if __name__ == "__main__":
    main()