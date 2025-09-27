"""
Network Setup Helper for FastAPI-Spring Boot Integration
This script helps configure networking between FastAPI and Spring Boot servers
"""

import socket
import subprocess
import platform
import os

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_port_available(port, host="0.0.0.0"):
    """Check if a port is available"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.close()
        return True
    except:
        return False

def get_network_interfaces():
    """Get network interface information"""
    interfaces = []
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["ipconfig"], capture_output=True, text=True, shell=True)
            output = result.stdout
        else:
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            output = result.stdout
        
        # Parse basic info (simplified)
        lines = output.split('\n')
        current_interface = None
        
        for line in lines:
            if platform.system() == "Windows":
                if "adapter" in line.lower():
                    current_interface = line.strip()
                elif "IPv4 Address" in line and current_interface:
                    ip = line.split(":")[-1].strip()
                    if ip and ip != "127.0.0.1":
                        interfaces.append({
                            "name": current_interface,
                            "ip": ip
                        })
            else:
                if line and not line.startswith(' ') and ':' in line:
                    current_interface = line.split(':')[0]
                elif "inet " in line and current_interface:
                    ip = line.strip().split()[1]
                    if ip and ip != "127.0.0.1":
                        interfaces.append({
                            "name": current_interface,
                            "ip": ip
                        })
    except:
        pass
    
    return interfaces

def test_connectivity(host, port, timeout=5):
    """Test if we can connect to a host:port"""
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def generate_config_files(fastapi_ip, fastapi_port, spring_boot_ip, spring_boot_port):
    """Generate configuration files for both services"""
    
    # Spring Boot application.yml
    spring_boot_config = f"""# Spring Boot Configuration for OCR Integration
server:
  port: {spring_boot_port}

# OCR Service Configuration
ocr-service:
  base-url: http://{fastapi_ip}:{fastapi_port}
  endpoints:
    health: /health
    single-process: /api/process
    batch-process: /api/process/documents
    service-info: /service-info
  timeout: 120  # seconds for batch processing
  retry-attempts: 3

# Logging
logging:
  level:
    com.yourapp.service.OcrServiceClient: DEBUG
    org.springframework.web.client.RestTemplate: DEBUG

# Callback configuration
app:
  callback-base-url: http://{spring_boot_ip}:{spring_boot_port}
  callback-endpoint: /api/documents/callback
"""
    
    # FastAPI environment configuration
    fastapi_env = f"""# FastAPI OCR Service Environment Configuration
SERVER_PORT={fastapi_port}
HOST=0.0.0.0

# MongoDB Configuration  
MONGODB_URL=mongodb://localhost:27017/document_processor

# Gemini API (if using)
# GEMINI_API_KEY=your_gemini_api_key_here

# CORS Settings (for cross-origin requests)
CORS_ORIGINS=http://{spring_boot_ip}:{spring_boot_port},http://localhost:{spring_boot_port}

# Service Registration
SPRING_BOOT_SERVICE_URL=http://{spring_boot_ip}:{spring_boot_port}
"""
    
    return spring_boot_config, fastapi_env

def main():
    print("🌐 **FASTAPI-SPRING BOOT NETWORK SETUP**")
    print("=" * 60)
    print()
    
    # Get local network information
    local_ip = get_local_ip()
    interfaces = get_network_interfaces()
    
    print("🔍 **NETWORK DISCOVERY**")
    print("=" * 30)
    print(f"Primary Local IP: {local_ip}")
    
    if interfaces:
        print("\nAvailable Network Interfaces:")
        for i, interface in enumerate(interfaces, 1):
            print(f"  {i}. {interface['name']}")
            print(f"     IP: {interface['ip']}")
    
    print()
    
    # Check port availability
    print("🔌 **PORT CHECK**")
    print("=" * 30)
    
    fastapi_port = 8000
    spring_boot_port = 8080
    
    fastapi_available = check_port_available(fastapi_port)
    spring_boot_available = check_port_available(spring_boot_port)
    
    print(f"FastAPI Port {fastapi_port}: {'✅ Available' if fastapi_available else '❌ In Use'}")
    print(f"Spring Boot Port {spring_boot_port}: {'✅ Available' if spring_boot_available else '❌ In Use'}")
    
    if not fastapi_available:
        print(f"   → FastAPI might already be running on port {fastapi_port}")
    if not spring_boot_available:
        print(f"   → Spring Boot might already be running on port {spring_boot_port}")
    
    print()
    
    # Configuration setup
    print("⚙️ **CONFIGURATION SETUP**")
    print("=" * 30)
    
    print("Choose your deployment scenario:")
    print("1. Both services on same machine (localhost)")
    print("2. Services on different machines")
    print("3. Custom configuration")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        fastapi_ip = "localhost"
        spring_boot_ip = "localhost"
        scenario = "Same Machine"
    elif choice == "2":
        print(f"\nCurrent machine IP: {local_ip}")
        fastapi_ip = input(f"FastAPI server IP (default: {local_ip}): ").strip() or local_ip
        spring_boot_ip = input("Spring Boot server IP: ").strip()
        scenario = "Different Machines"
    else:
        fastapi_ip = input(f"FastAPI server IP (default: {local_ip}): ").strip() or local_ip
        fastapi_port = int(input(f"FastAPI port (default: 8000): ").strip() or "8000")
        spring_boot_ip = input("Spring Boot server IP: ").strip()
        spring_boot_port = int(input(f"Spring Boot port (default: 8080): ").strip() or "8080")
        scenario = "Custom"
    
    print(f"\n📋 **CONFIGURATION SUMMARY**")
    print("=" * 30)
    print(f"Scenario: {scenario}")
    print(f"FastAPI Service: http://{fastapi_ip}:{fastapi_port}")
    print(f"Spring Boot Service: http://{spring_boot_ip}:{spring_boot_port}")
    print()
    
    # Test connectivity (if different machines)
    if choice == "2" and spring_boot_ip != "localhost":
        print("🧪 **CONNECTIVITY TEST**")
        print("=" * 30)
        
        print("Testing connectivity...")
        # This is just a basic ping test - actual service might not be running yet
        can_reach = test_connectivity(spring_boot_ip, spring_boot_port, timeout=3)
        print(f"Can reach Spring Boot server: {'✅' if can_reach else '❌'}")
        
        if not can_reach:
            print("⚠️  Note: This might be normal if Spring Boot isn't running yet")
        print()
    
    # Generate configuration files
    spring_config, fastapi_env = generate_config_files(fastapi_ip, fastapi_port, spring_boot_ip, spring_boot_port)
    
    # Save configuration files
    try:
        with open("spring_boot_application.yml", "w") as f:
            f.write(spring_config)
        print("✅ Created: spring_boot_application.yml")
        
        with open("fastapi_service.env", "w") as f:
            f.write(fastapi_env)
        print("✅ Created: fastapi_service.env")
        
    except Exception as e:
        print(f"❌ Error creating config files: {e}")
    
    print()
    print("📚 **NEXT STEPS**")
    print("=" * 30)
    print("1. Copy spring_boot_application.yml to your Spring Boot project")
    print("2. Use fastapi_service.env to configure FastAPI environment")
    print("3. Update firewall settings if using different machines:")
    
    if choice == "2":
        print(f"   • Open port {fastapi_port} on FastAPI machine")
        print(f"   • Open port {spring_boot_port} on Spring Boot machine")
    
    print("4. Start both services:")
    print(f"   • FastAPI: python app.py")
    print(f"   • Spring Boot: ./mvnw spring-boot:run")
    print("5. Test integration:")
    print("   • Run: python test_spring_boot_integration.py")
    
    print()
    print("🔗 **TESTING URLS**")
    print("=" * 30)
    print(f"FastAPI Health: http://{fastapi_ip}:{fastapi_port}/health")
    print(f"FastAPI Docs: http://{fastapi_ip}:{fastapi_port}/docs")
    print(f"FastAPI Service Info: http://{fastapi_ip}:{fastapi_port}/service-info")
    print(f"Spring Boot Health: http://{spring_boot_ip}:{spring_boot_port}/actuator/health")
    
    print()
    print("🛠️ **TROUBLESHOOTING**")
    print("=" * 30)
    print("• Connection refused: Check if services are running")
    print("• Timeout errors: Check firewall settings")
    print("• DNS issues: Use IP addresses instead of hostnames")
    print("• Port conflicts: Use netstat to check port usage")

if __name__ == "__main__":
    main()