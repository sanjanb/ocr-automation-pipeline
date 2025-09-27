# Quick Start Guide: FastAPI-Spring Boot Integration

## Overview

Your FastAPI OCR service now includes comprehensive inter-service communication capabilities. Here's how to connect it with your Spring Boot main server running on a different system.

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run Network Setup

```bash
python network_setup.py
```

This interactive script will:

- Detect your network configuration
- Generate proper configuration files
- Test connectivity between services
- Provide troubleshooting guidance

### Step 2: Start FastAPI Service

```bash
python app.py
```

The service will start on port 8000 with these new endpoints:

- `/service-info` - Network discovery and endpoint listing
- `/register-service` - Service registration for callbacks
- `/api/process/documents` - Batch URI processing

### Step 3: Configure Spring Boot

Copy the generated `spring_boot_application.yml` to your Spring Boot project and implement the Java client code from `SPRING_BOOT_INTEGRATION.md`.

## 🔧 Key Endpoints for Spring Boot Integration

### 1. Service Discovery

```
GET http://<fastapi-ip>:8000/service-info
```

Returns:

```json
{
  "service_name": "FastAPI OCR Service",
  "host": "192.168.1.100",
  "port": 8000,
  "endpoints": {
    "health": "/health",
    "process_single": "/api/process",
    "process_batch": "/api/process/documents",
    "register_service": "/register-service"
  }
}
```

### 2. Service Registration

```
POST http://<fastapi-ip>:8000/register-service
{
  "service_name": "spring-boot-main",
  "callback_url": "http://<spring-boot-ip>:8080/api/documents/callback"
}
```

### 3. Batch Document Processing

```
POST http://<fastapi-ip>:8000/api/process/documents
{
  "documents": [
    {"uri": "http://example.com/doc1.pdf", "type": "pdf"},
    {"uri": "http://example.com/doc2.jpg", "type": "image"}
  ],
  "batch_id": "batch-123",
  "callback_url": "http://<spring-boot-ip>:8080/api/documents/callback"
}
```

## 📝 Spring Boot Implementation Checklist

1. **Add Dependencies** (in pom.xml):

   ```xml
   <dependency>
       <groupId>org.springframework.boot</groupId>
       <artifactId>spring-boot-starter-web</artifactId>
   </dependency>
   ```

2. **Create Service Client** - Use the complete implementation from `SPRING_BOOT_INTEGRATION.md`

3. **Add Configuration** - Use the generated `spring_boot_application.yml`

4. **Implement Callback Handler**:
   ```java
   @PostMapping("/api/documents/callback")
   public ResponseEntity<String> handleOcrCallback(@RequestBody OcrCallbackRequest request) {
       // Handle OCR results
       return ResponseEntity.ok("Received");
   }
   ```

## 🧪 Testing Integration

Run the integration test to verify everything works:

```bash
python test_spring_boot_integration.py
```

This simulates the complete workflow:

1. Service discovery
2. Registration
3. Health checks
4. Document processing
5. Callback handling

## 🔄 Communication Flow

```
Spring Boot Server → FastAPI Service Discovery → Get Endpoints
Spring Boot Server → Register for Callbacks → Receive Registration ID
Spring Boot Server → Submit Document URIs → FastAPI Downloads & Processes
FastAPI Service → Send Results → Spring Boot Callback Endpoint
```

## ⚡ Production Deployment

1. **Network Security**: Open required ports (8000 for FastAPI, 8080 for Spring Boot)
2. **Environment Variables**: Use `.env` files for sensitive configuration
3. **Health Monitoring**: Both services expose `/health` endpoints
4. **Load Balancing**: FastAPI supports async processing for high throughput

## 🆘 Common Issues

**Connection Refused**: Services not running or firewall blocking ports
**Timeout Errors**: Check network connectivity between machines  
**JSON Parsing**: Verify request/response formats match the API specification
**Callback Issues**: Ensure Spring Boot callback endpoint is accessible from FastAPI machine

Your FastAPI OCR service is now ready for production inter-service communication! 🎉
