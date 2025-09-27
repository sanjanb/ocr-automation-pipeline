# Spring Boot Integration Guide

This guide shows how to integrate your Spring Boot server with the FastAPI OCR Document Processing service.

## 🔗 Service Discovery

### 1. Get FastAPI Service Information

First, your Spring Boot server should discover the FastAPI service:

**GET Request to FastAPI:**

```
GET http://<fastapi-host>:8000/service-info
```

This returns complete service configuration including endpoints and capabilities.

### 2. Spring Boot Configuration

Add these properties to your `application.yml` or `application.properties`:

```yaml
# application.yml
ocr-service:
  base-url: http://192.168.1.100:8000 # Replace with actual FastAPI server IP
  endpoints:
    health: /health
    single-process: /api/process
    batch-process: /api/process/documents
    service-info: /service-info
  timeout: 120 # seconds for batch processing
  retry-attempts: 3
```

OR

```properties
# application.properties
ocr.service.base-url=http://192.168.1.100:8000
ocr.service.endpoints.health=/health
ocr.service.endpoints.single-process=/api/process
ocr.service.endpoints.batch-process=/api/process/documents
ocr.service.timeout=120
ocr.service.retry-attempts=3
```

## 🚀 Spring Boot Code Examples

### 1. Service Configuration Class

```java
package com.yourapp.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "ocr.service")
public class OcrServiceConfig {
    private String baseUrl;
    private int timeout = 120;
    private int retryAttempts = 3;
    private Endpoints endpoints = new Endpoints();

    // Getters and setters
    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }

    public int getTimeout() { return timeout; }
    public void setTimeout(int timeout) { this.timeout = timeout; }

    public int getRetryAttempts() { return retryAttempts; }
    public void setRetryAttempts(int retryAttempts) { this.retryAttempts = retryAttempts; }

    public Endpoints getEndpoints() { return endpoints; }
    public void setEndpoints(Endpoints endpoints) { this.endpoints = endpoints; }

    public static class Endpoints {
        private String health = "/health";
        private String singleProcess = "/api/process";
        private String batchProcess = "/api/process/documents";
        private String serviceInfo = "/service-info";

        // Getters and setters
        public String getHealth() { return health; }
        public void setHealth(String health) { this.health = health; }

        public String getSingleProcess() { return singleProcess; }
        public void setSingleProcess(String singleProcess) { this.singleProcess = singleProcess; }

        public String getBatchProcess() { return batchProcess; }
        public void setBatchProcess(String batchProcess) { this.batchProcess = batchProcess; }

        public String getServiceInfo() { return serviceInfo; }
        public void setServiceInfo(String serviceInfo) { this.serviceInfo = serviceInfo; }
    }
}
```

### 2. OCR Service Client

```java
package com.yourapp.service;

import com.yourapp.config.OcrServiceConfig;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.retry.annotation.Retryable;
import org.springframework.retry.annotation.Backoff;

import java.util.List;
import java.util.Map;

@Service
public class OcrServiceClient {

    @Autowired
    private OcrServiceConfig config;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * Check if OCR service is healthy
     */
    public boolean isHealthy() {
        try {
            String url = config.getBaseUrl() + config.getEndpoints().getHealth();
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);

            if (response.getStatusCode() == HttpStatus.OK) {
                Map<String, Object> health = response.getBody();
                return "healthy".equals(health.get("status"));
            }
            return false;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Get service information for dynamic configuration
     */
    public Map<String, Object> getServiceInfo() {
        try {
            String url = config.getBaseUrl() + config.getEndpoints().getServiceInfo();
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);
            return response.getBody();
        } catch (Exception e) {
            throw new RuntimeException("Failed to get OCR service info", e);
        }
    }

    /**
     * Process multiple documents from URIs
     */
    @Retryable(value = {Exception.class}, maxAttempts = 3, backoff = @Backoff(delay = 1000))
    public BatchProcessingResponse processBatchDocuments(BatchProcessingRequest request) {
        try {
            String url = config.getBaseUrl() + config.getEndpoints().getBatchProcess();

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<BatchProcessingRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<BatchProcessingResponse> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                BatchProcessingResponse.class
            );

            return response.getBody();

        } catch (Exception e) {
            throw new RuntimeException("Failed to process batch documents", e);
        }
    }

    /**
     * Process single document by uploading file
     */
    public ProcessingResponse processSingleDocument(MultipartFile file, String documentType, String studentId) {
        // Implementation for single file upload
        // This would use MultipartBodyBuilder for file uploads
        throw new UnsupportedOperationException("Single file upload not implemented yet");
    }
}
```

### 3. Data Transfer Objects (DTOs)

```java
package com.yourapp.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class BatchProcessingRequest {
    @JsonProperty("document_uris")
    private List<String> documentUris;

    @JsonProperty("document_type")
    private String documentType;

    @JsonProperty("student_id")
    private String studentId;

    @JsonProperty("batch_name")
    private String batchName;

    @JsonProperty("callback_url")
    private String callbackUrl;

    // Constructors, getters, and setters
    public BatchProcessingRequest() {}

    public BatchProcessingRequest(List<String> documentUris, String studentId) {
        this.documentUris = documentUris;
        this.studentId = studentId;
    }

    // Getters and setters
    public List<String> getDocumentUris() { return documentUris; }
    public void setDocumentUris(List<String> documentUris) { this.documentUris = documentUris; }

    public String getDocumentType() { return documentType; }
    public void setDocumentType(String documentType) { this.documentType = documentType; }

    public String getStudentId() { return studentId; }
    public void setStudentId(String studentId) { this.studentId = studentId; }

    public String getBatchName() { return batchName; }
    public void setBatchName(String batchName) { this.batchName = batchName; }

    public String getCallbackUrl() { return callbackUrl; }
    public void setCallbackUrl(String callbackUrl) { this.callbackUrl = callbackUrl; }
}

public class BatchProcessingResponse {
    private boolean success;

    @JsonProperty("batch_name")
    private String batchName;

    @JsonProperty("total_documents")
    private int totalDocuments;

    @JsonProperty("processed_documents")
    private int processedDocuments;

    @JsonProperty("failed_documents")
    private int failedDocuments;

    @JsonProperty("total_processing_time")
    private double totalProcessingTime;

    private String message;
    private List<DocumentProcessingResult> results;

    // Constructors, getters, and setters
    public BatchProcessingResponse() {}

    // Getters and setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getBatchName() { return batchName; }
    public void setBatchName(String batchName) { this.batchName = batchName; }

    public int getTotalDocuments() { return totalDocuments; }
    public void setTotalDocuments(int totalDocuments) { this.totalDocuments = totalDocuments; }

    public int getProcessedDocuments() { return processedDocuments; }
    public void setProcessedDocuments(int processedDocuments) { this.processedDocuments = processedDocuments; }

    public int getFailedDocuments() { return failedDocuments; }
    public void setFailedDocuments(int failedDocuments) { this.failedDocuments = failedDocuments; }

    public double getTotalProcessingTime() { return totalProcessingTime; }
    public void setTotalProcessingTime(double totalProcessingTime) { this.totalProcessingTime = totalProcessingTime; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public List<DocumentProcessingResult> getResults() { return results; }
    public void setResults(List<DocumentProcessingResult> results) { this.results = results; }
}

public class DocumentProcessingResult {
    private String uri;
    private boolean success;

    @JsonProperty("document_type")
    private String documentType;

    @JsonProperty("extracted_data")
    private Map<String, Object> extractedData;

    @JsonProperty("processing_time")
    private double processingTime;

    @JsonProperty("confidence_score")
    private double confidenceScore;

    @JsonProperty("model_used")
    private String modelUsed;

    @JsonProperty("error_message")
    private String errorMessage;

    @JsonProperty("mongodb_stored")
    private boolean mongodbStored;

    @JsonProperty("validation_issues")
    private List<String> validationIssues;

    // Constructors, getters, and setters
    public DocumentProcessingResult() {}

    // Add all getters and setters...
}
```

### 4. REST Controller Example

```java
package com.yourapp.controller;

import com.yourapp.service.OcrServiceClient;
import com.yourapp.dto.BatchProcessingRequest;
import com.yourapp.dto.BatchProcessingResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    @Autowired
    private OcrServiceClient ocrServiceClient;

    /**
     * Submit documents for OCR processing
     */
    @PostMapping("/process")
    public ResponseEntity<BatchProcessingResponse> processDocuments(
            @RequestParam List<String> documentUrls,
            @RequestParam String studentId,
            @RequestParam(required = false) String documentType,
            @RequestParam(required = false) String batchName) {

        // Check if OCR service is healthy
        if (!ocrServiceClient.isHealthy()) {
            throw new RuntimeException("OCR service is not available");
        }

        // Create request
        BatchProcessingRequest request = new BatchProcessingRequest(documentUrls, studentId);
        request.setDocumentType(documentType);
        request.setBatchName(batchName);
        request.setCallbackUrl("http://your-spring-boot-server:8080/api/documents/callback");

        // Process documents
        BatchProcessingResponse response = ocrServiceClient.processBatchDocuments(request);

        return ResponseEntity.ok(response);
    }

    /**
     * Callback endpoint for OCR service to send results
     */
    @PostMapping("/callback")
    public ResponseEntity<String> handleOcrCallback(@RequestBody BatchProcessingResponse response) {
        // Handle the callback from OCR service
        System.out.println("Received OCR callback for batch: " + response.getBatchName());
        System.out.println("Processed: " + response.getProcessedDocuments() + "/" + response.getTotalDocuments());

        // Process the results as needed
        // Save to database, send notifications, etc.

        return ResponseEntity.ok("Callback received successfully");
    }

    /**
     * Get OCR service status
     */
    @GetMapping("/ocr-service/status")
    public ResponseEntity<Map<String, Object>> getOcrServiceStatus() {
        Map<String, Object> serviceInfo = ocrServiceClient.getServiceInfo();
        return ResponseEntity.ok(serviceInfo);
    }
}
```

### 5. Bean Configuration

```java
package com.yourapp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.retry.annotation.EnableRetry;

import java.time.Duration;

@Configuration
@EnableRetry
public class AppConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(30))
                .setReadTimeout(Duration.ofSeconds(120))  // Long timeout for batch processing
                .build();
    }
}
```

## 🌐 Network Configuration

### For Different Machines:

1. **Find FastAPI server IP:**

   ```bash
   # On FastAPI machine, run:
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

2. **Update Spring Boot configuration:**

   ```yaml
   ocr-service:
     base-url: http://192.168.1.100:8000 # Use actual IP
   ```

3. **Firewall settings:**
   - Open port 8000 on FastAPI machine
   - Ensure both machines can reach each other

### For Same Machine (Testing):

```yaml
ocr-service:
  base-url: http://localhost:8000
```

## 🧪 Testing the Integration

1. **Start FastAPI server:**

   ```bash
   python app.py
   ```

2. **Test from Spring Boot:**

   ```bash
   curl -X POST "http://localhost:8080/api/documents/process" \
     -d "documentUrls=https://example.com/doc1.jpg" \
     -d "studentId=STUDENT_123" \
     -d "batchName=test_batch"
   ```

3. **Check OCR service status:**
   ```bash
   curl "http://localhost:8080/api/documents/ocr-service/status"
   ```

## 🔧 Advanced Configuration

### Load Balancing (Multiple FastAPI Instances):

```yaml
ocr-service:
  instances:
    - http://192.168.1.100:8000
    - http://192.168.1.101:8000
  load-balancing: round-robin
```

### Security (API Keys):

Add to FastAPI headers:

```java
HttpHeaders headers = new HttpHeaders();
headers.set("X-API-Key", "your-api-key");
headers.setContentType(MediaType.APPLICATION_JSON);
```

This setup provides robust inter-service communication between your Spring Boot and FastAPI servers!
