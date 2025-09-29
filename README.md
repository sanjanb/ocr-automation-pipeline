# Smart Document Processor - AI-Powered OCR Microservice# Smart Document Processor - AI-Powered OCR Microservice

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

[![SLM](https://img.shields.io/badge/AI-SLM%20Model-orange.svg)](https://ai.google.dev)[![SLM](https://img.shields.io/badge/AI-SLM%20Model-orange.svg)](https://ai.google.dev)

[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)](https://mongodb.com)[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)](https://mongodb.com)

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Smart Document Processor Interface](assets/Screenshot%202025-09-26%20210220.png)![Smart Document Processor Interface](assets/Screenshot%202025-09-26%20210220.png)

A **production-ready FastAPI microservice** for AI-powered document processing using Small Language Model (SLM). Extract structured data from Indian documents including Aadhaar cards, marksheets, certificates, and more.A **production-ready FastAPI microservice** for AI-powered document processing using Small Language Model (SLM). Extract structured data from Indian documents including Aadhaar cards, marksheets, certificates, and more.

## Quick Start## Quick Start **What This Does**

```bash`````bash## Quick Start

# 1. Clone the repository

git clone https://github.com/sanjanb/ocr-automation-pipeline.git# 1. Clone the repository

cd ocr-automation-pipeline

git clone https://github.com/sanjanb/ocr-automation-pipeline.git- **Direct AI Processing**: Gemini 1.5 Flash reads images and extracts structured data in one step

# 2. Set up environment

python -m venv venvcd ocr-automation-pipeline

source venv/bin/activate # Linux/macOS

# or venv\Scripts\activate # Windows````bash- **Lightning Fast**: 2-5 second processing vs traditional 30+ second OCR pipelines

# 3. Install dependencies# 2. Set up environment

pip install -r requirements.txt

python -m venv venv# 1. Clone the repository- **Smart Validation**: AI-powered completeness checking and error detection

# 4. Configure API key

cp .env.example .envsource venv/bin/activate # Linux/macOS

# Edit .env and add your SLM API key

# or venv\Scripts\activate # Windowsgit clone https://github.com/sanjanb/ocr-automation-pipeline.git- **Production Ready**: FastAPI with automatic documentation, async support, and Docker deployment

# 5. Start the service

uvicorn app:app --reload

```

# 3. Install dependenciescd ocr-automation-pipeline- **Developer Friendly**: Modern Python, comprehensive tests, and CI/CD pipeline

**Access Points:**

- **Web Interface**: http://localhost:8000pip install -r requirements.txt

- **API Documentation**: http://localhost:8000/docs

- **Health Check**: http://localhost:8000/health



## Table of Contents# 4. Configure API key



- [Architecture Overview](#architecture-overview)cp .env.example .env# 2. Set up environment## **Quick Start**

- [Key Features](#key-features)

- [Installation & Setup](#installation--setup)# Edit .env and add your GEMINI_API_KEY

- [API Integration Guide](#api-integration-guide)

- [Docker Deployment](#docker-deployment)python -m venv venv

- [Testing](#testing)

- [Supported Documents](#supported-documents)# 5. Start the service

- [Security & Configuration](#security--configuration)

- [Contributing](#contributing)uvicorn app:app --reloadsource venv/bin/activate  # Linux/macOS### **Option 1: Direct Installation**

- [Support](#support)

```

## Architecture Overview

## Table of Contentspip

`````````mermaid

graph TB- [Architecture Overview](#architecture-overview)cd ocr-automation-pipeline

    subgraph "Client Applications"

        A[Web Interface]- [Key Features](#key-features)

        B[Spring Boot App]

        C[Mobile App]- [Installation & Setup](#installation--setup)# 4. Configure API key

        D[External Services]

    end- [API Integration Guide](#api-integration-guide)



    subgraph "FastAPI Microservice"- [Docker Deployment](#docker-deployment)cp .env.example .env# 2. Install dependencies

        E[FastAPI Router]

        F[Document Processor]- [Testing](#testing)

        G[AI Processing Engine]

        H[Data Normalizer]- [Supported Documents](#supported-documents)# Edit .env and add your GEMINI_API_KEYpip install -r requirements.txt

    end

    - [Security & Configuration](#security--configuration)

    subgraph "Storage & AI"

        I[MongoDB Database]- [Contributing](#contributing)

        J[SLM Model]

        K[Cloudinary CDN]- [Support](#support)

    end

    ## Architecture Overview

    A --> E

    B --> Euvicorn app:app --reloadecho "GEMINI_API_KEY=your_api_key_here" > .env

    C --> E

    D --> E````````mermaid



    E --> Fgraph TB````

    F --> G

    G --> J    subgraph "Client Applications"

    F --> H

    H --> I        A[Web Interface]# 4. Run the application

    F --> K

            B[Spring Boot App]

    J --> G

    G --> F        C[Mobile App]**🌐 Access Points:**uvicorn app:app --reload

    F --> E

```        D[External Services]



## Key Features    end- **Web Interface**: http://localhost:8000



### AI-Powered Processing

- **SLM Model Integration**: Direct image-to-JSON extraction

- **Auto Document Detection**: Intelligent type recognition    subgraph "FastAPI Microservice"- **API Documentation**: http://localhost:8000/docs# 5. Open browser

- **High Accuracy**: Confidence scoring and validation

- **Multi-format Support**: JPEG, PNG, WebP, PDF processing        E[FastAPI Router]



### Production-Ready API        F[Document Processor]- **Health Check**: http://localhost:8000/health# Web UI: http://localhost:8000

- **FastAPI Framework**: Modern async web framework

- **OpenAPI Documentation**: Interactive Swagger UI        G[AI Processing Engine]

- **RESTful Endpoints**: Standard HTTP methods

- **CORS Support**: Cross-origin resource sharing        H[Data Normalizer]# API Docs: http://localhost:8000/docs

- **Rate Limiting**: DoS protection

    end

### Document Types Supported

- **Aadhaar Card**: Full data extraction    ## 📋 Table of Contents```

- **Academic Records**: 10th & 12th marksheets

- **Certificates**: Transfer, migration, caste, domicile    subgraph "Storage & AI"

- **Entrance Documents**: Scorecards and admit cards

- **Identity Documents**: Passport photos        I[MongoDB Database]- [🏗️ Architecture Overview](#architecture-overview)### **Option 2: Docker**



### Integration Options        J[Gemini 2.0 Flash]

- **Single Document Processing**: Upload and process immediately

- **Batch Processing**: Multiple documents from URLs        K[Cloudinary CDN]- [✨ Key Features](#key-features)

- **MongoDB Integration**: Automatic data storage

- **Webhook Callbacks**: Async result delivery    end

- **Service Registration**: External service connectivity

    - [🔧 Installation & Setup](#installation--setup)```bash

### Advanced Features

- **Data Normalization**: Consistent field formatting    A --> E

- **Validation Rules**: Document-specific checks

- **Confidence Thresholds**: Quality assurance    B --> E- [🔌 API Integration Guide](#api-integration-guide)# 1. Clone and build

- **Error Handling**: Comprehensive error responses

- **Monitoring**: Health checks and logging    C --> E



## Installation & Setup    D --> E- [🐳 Docker Deployment](#docker-deployment)git clone https://github.com/sanjanb/ocr-automation-pipeline.git



### Prerequisites

- **Python**: 3.10 or higher

- **MongoDB**: 4.4+ (optional, for data storage)    E --> F- [🧪 Testing](#testing)cd ocr-automation-pipeline

- **SLM API Key**: Required for document processing

    F --> G

### Local Development Setup

    G --> J- [📚 Supported Documents](#supported-documents)

1. **Clone Repository**

   ```bash    F --> H

   git clone https://github.com/sanjanb/ocr-automation-pipeline.git

   cd ocr-automation-pipeline    H --> I- [🔒 Security & Configuration](#security--configuration)# 2. Run with Docker Compose

`````````

    F --> K

2. **Create Virtual Environment**

   ```bash - [🤝 Contributing](#contributing)echo "GEMINI_API_KEY=your_api_key_here" > .env

   python -m venv venv

       J --> G

   # Activate (choose based on your OS)

   source venv/bin/activate      # Linux/macOS    G --> F- [📞 Support](#support)docker-compose up -d

   venv\Scripts\activate         # Windows PowerShell

   venv\Scripts\activate.bat     # Windows Command Prompt    F --> E

   ```

````## Architecture Overview# 3. Access application

3. **Install Dependencies**

   ```bash

   pip install --upgrade pip

   pip install -r requirements.txt## Key Features# Web UI: http://localhost:8000

````

4. **Environment Configuration**

   ```bash### AI-Powered Processing```````mermaid# Health Check: http://localhost:8000/health

   cp .env.example .env

   ````- **Gemini 2.0 Flash Integration**: Direct image-to-JSON extraction



   Edit `.env` file:- **Auto Document Detection**: Intelligent type recognitiongraph TB```

   ```env

   # Required: SLM model API key for document processing- **High Accuracy**: Confidence scoring and validation

   GEMINI_API_KEY=your_slm_api_key_here

   - **Multi-format Support**: JPEG, PNG, WebP, PDF processing    subgraph "Client Applications"

   # Optional: Database (remove if not using MongoDB)

   MONGODB_URL=mongodb://localhost:27017/document_processor



   # Server Configuration### Production-Ready API        A[Web Interface]### **Get Gemini API Key**

   HOST=0.0.0.0

   PORT=8000- **FastAPI Framework**: Modern async web framework

   DEBUG=false

   LOG_LEVEL=INFO- **OpenAPI Documentation**: Interactive Swagger UI        B[Spring Boot App]

   ````

- **RESTful Endpoints**: Standard HTTP methods

5. **Start the Service**

   ````bash- **CORS Support**: Cross-origin resource sharing        C[Mobile App]1. Visit: [Google AI Studio](https://makersuite.google.com/app/apikey)

   # Development mode (with auto-reload)

   uvicorn app:app --reload --host 0.0.0.0 --port 8000- **Rate Limiting**: DoS protection



   # Production mode        D[External Services]2. Create new project and API key

   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1

   ```### Document Types Supported

   ````

6. **Verify Installation**- **Aadhaar Card**: Full data extraction end3. Copy key to your `.env` file

   ````bash

   # Test health endpoint- **Academic Records**: 10th & 12th marksheets

   curl http://localhost:8000/health

   - **Certificates**: Transfer, migration, caste, domicile

   # Should return: {"status":"healthy","version":"2.0.0","slm_configured":true,...}

   ```- **Entrance Documents**: Scorecards and admit cards
   ````

### MongoDB Setup (Optional)- **Identity Documents**: Passport photos subgraph "FastAPI Microservice"## **Architecture**

If you want to store processed documents:

````bash### Integration Options        E[FastAPI Router]

# Option 1: Docker MongoDB

docker run -d -p 27017:27017 --name mongodb mongo:latest- **Single Document Processing**: Upload and process immediately



# Option 2: Install locally- **Batch Processing**: Multiple documents from URLs        F[Document Processor]```mermaid

# macOS: brew install mongodb-community

# Ubuntu: sudo apt-get install mongodb- **MongoDB Integration**: Automatic data storage

# Windows: Download from mongodb.com

- **Webhook Callbacks**: Async result delivery        G[AI Processing Engine]graph TD

# Verify MongoDB connection

curl http://localhost:8000/health- **Service Registration**: External service connectivity

# Check database_connected: true

```        H[Data Normalizer]    A[Document Upload] --> B[FastAPI Endpoint]



## API Integration Guide### Advanced Features



### REST API Endpoints- **Data Normalization**: Consistent field formatting    end    B --> C[Gemini 1.5 Flash]



#### **Single Document Processing**- **Validation Rules**: Document-specific checks

```bash

POST /api/process- **Confidence Thresholds**: Quality assurance        C --> D[JSON Extraction]

Content-Type: multipart/form-data

- **Error Handling**: Comprehensive error responses

# Form fields:

- file: [IMAGE/PDF FILE]- **Monitoring**: Health checks and logging    subgraph "Storage & AI"    D --> E[AI Validation]

- document_type: "aadhaar_card" (optional)

- student_id: "STUDENT_123" (optional, for MongoDB storage)

````

## Installation & Setup I[MongoDB Database] E --> F[Structured Response]

**Example using curl:**

```bash

curl -X POST "http://localhost:8000/api/process" \

  -F "file=@/path/to/aadhaar.jpg" \### Prerequisites        J[Gemini 2.0 Flash]

  -F "document_type=aadhaar_card" \

  -F "student_id=STUDENT_123"- **Python**: 3.10 or higher

```

- **MongoDB**: 4.4+ (optional, for data storage) K[Cloudinary CDN] G[Web Interface] --> A

**Example Response:**

`````````json- **Gemini API Key**: [Get from Google AI Studio](https://makersuite.google.com/app/apikey)

{

  "success": true,    end    H[API Client] --> A

  "document_type": "aadhaar_card",

  "confidence_score": 0.95,### Local Development Setup

  "processing_time": 2.34,

  "extracted_data": {        I[Batch Processing] --> A

    "name": "राम प्रसाद शर्मा",

    "aadhaar_number": "1234 5678 9012",1. **Clone Repository**

    "date_of_birth": "01/01/1990",

    "gender": "MALE",   ```bash    A --> E```

    "address": "123 Sample Street, City, State - 123456"

  },   git clone https://github.com/sanjanb/ocr-automation-pipeline.git

  "validation_issues": [],

  "metadata": {   cd ocr-automation-pipeline    B --> E

    "mongodb_stored": true,

    "student_id": "STUDENT_123"````````

  }

}    C --> E## **Supported Documents**

`````````

2. **Create Virtual Environment**

#### **Batch Processing from URLs**

`bash   `bash D --> E

POST /api/process/documents

Content-Type: application/json python -m venv venv

{ | Document | Required Fields | Validation Rules | Use Case |

"document_uris": [

    "https://example.com/doc1.jpg",   # Activate (choose based on your OS)

    "https://example.com/doc2.pdf"

], source venv/bin/activate # Linux/macOS E --> F| ---------------------------- | --------------------------------------- | ---------------------- | --------------------- |

"student_id": "STUDENT_123",

"document_type": "marksheet_10th", venv\Scripts\activate # Windows PowerShell

"batch_name": "admission_batch_1",

"callback_url": "https://your-app.com/callback" venv\Scripts\activate.bat # Windows Command Prompt F --> G| 🆔 **Aadhaar Card** | Name, Number, DOB, Address | 12-digit validation | Identity verification |

}

`   `

#### **MongoDB Fetch and Process** G --> J| 📜 **10th/12th Marksheet** | Student, Roll No, Board, Year, Subjects | Grade validation | Academic verification |

````bash

POST /api/fetch-and-process3. **Install Dependencies**

Content-Type: application/json

   ```bash F --> H| 📄 **Transfer Certificate**  | Student, Father, School, Class          | Date format validation | School transfers      |

{

  "collection_name": "raw_documents",   pip install --upgrade pip

  "filter_criteria": {"student_id": "STUDENT_123"},

  "uri_field_name": "cloudinary_url",   pip install -r requirements.txt    H --> I| 🎓 **Migration Certificate** | Student, University, Course             | Year validation        | University transfers  |

  "batch_size": 10

}   ```

````

F --> K| 📊 **Entrance Scorecard** | Candidate, Exam, Score, Rank | Numeric validation | Competitive exams |

### Integration Examples

4. **Environment Configuration**

#### **JavaScript/Node.js**

```javascript ````bash | 🎫 **Admit Card** | Candidate, Exam, Date, Center | Date/time validation | Exam identification |

const axios = require('axios');

const FormData = require('form-data'); cp .env.example .env

const fs = require('fs');

````J --> G| 📋 **Caste Certificate**     | Name, Father, Caste, Category           | Category validation    | Government benefits   |

// Single document processing

async function processDocument(filePath, documentType) {

const form = new FormData();

form.append('file', fs.createReadStream(filePath));   Edit `.env` file:    G --> F| 🏠 **Domicile Certificate**  | Name, State, District                   | Geographic validation  | Residence proof       |

form.append('document_type', documentType);

form.append('student_id', 'STUDENT_123');   ```env



const response = await axios.post('http://localhost:8000/api/process', form, {   # Required: Get from https://makersuite.google.com/app/apikey    F --> E

 headers: form.getHeaders()

});   GEMINI_API_KEY=your_actual_api_key_here



return response.data;   ```## 🔌 **API Usage**

}

# Optional: Database (remove if not using MongoDB)

// Batch processing

async function processBatch(documentUris, studentId) {   MONGODB_URL=mongodb://localhost:27017/document_processor

const response = await axios.post('http://localhost:8000/api/process/documents', {

 document_uris: documentUris,

 student_id: studentId,

 document_type: 'aadhaar_card'   # Server Configuration## ✨ Key Features### **Process Single Document**

});

HOST=0.0.0.0

return response.data;

}   PORT=8000

````

DEBUG=false

#### **Python Client**

`python   LOG_LEVEL=INFO### 🧠 AI-Powered Processing`python

import requests

`````````

# Single document processing

def process_document(file_path, document_type="aadhaar_card"):- **Gemini 2.0 Flash Integration**: Direct image-to-JSON extractionimport requests

 with open(file_path, 'rb') as f:

     files = {'file': f}5. **Start the Service**

     data = {

         'document_type': document_type,   ````bash- **Auto Document Detection**: Intelligent type recognition

         'student_id': 'STUDENT_123'

     }   # Development mode (with auto-reload)

     response = requests.post('http://localhost:8000/api/process',

                            files=files, data=data)   uvicorn app:app --reload --host 0.0.0.0 --port 8000- **High Accuracy**: Confidence scoring and validation# Upload and process

 return response.json()



# Batch processing

def process_batch(document_uris, student_id):   # Production mode- **Multi-format Support**: JPEG, PNG, WebP, PDF processingwith open("document.jpg", "rb") as f:

 payload = {

     'document_uris': document_uris,   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1

     'student_id': student_id,

     'document_type': 'marksheet_10th'   ```    response = requests.post(

 }

 response = requests.post('http://localhost:8000/api/process/documents',    ````

                        json=payload)

 return response.json()6. **Verify Installation**### 🌐 Production-Ready API "http://localhost:8000/api/process",

```

````bash

#### **Java/Spring Boot**

```java   # Test health endpoint- **FastAPI Framework**: Modern async web framework        files={"file": f},

@Service

public class DocumentProcessorService {   curl http://localhost:8000/health



 @Value("${ocr.service.base-url:http://localhost:8000}")   - **OpenAPI Documentation**: Interactive Swagger UI        data={"document_type": "aadhaar_card"}

 private String ocrServiceUrl;

    # Should return: {"status":"healthy","version":"2.0.0",...}

 private final WebClient webClient;

    ```- **RESTful Endpoints**: Standard HTTP methods    )

 public DocumentProcessorService(WebClient.Builder webClientBuilder) {   ````

     this.webClient = webClientBuilder

         .baseUrl(ocrServiceUrl)### MongoDB Setup (Optional)- **CORS Support**: Cross-origin resource sharing

         .build();

 }If you want to store processed documents:- **Rate Limiting**: DoS protectionresult = response.json()



 // Single document processing````bashprint(f"Confidence: {result['confidence_score']:.1%}")

 public Mono<ProcessingResult> processDocument(MultipartFile file,

                                             String documentType, # Option 1: Docker MongoDB

                                             String studentId) {

     MultiValueMap<String, HttpEntity<?>> parts = new LinkedMultiValueMap<>();docker run -d -p 27017:27017 --name mongodb mongo:latest### 📁 Document Types Supportedprint(f"Data: {result['extracted_data']}")

     parts.add("file", new FileSystemResource(file.getResource().getFile()));

     parts.add("document_type", new HttpEntity<>(documentType));

     parts.add("student_id", new HttpEntity<>(studentId));

     # Option 2: Install locally- **Aadhaar Card**: Full data extraction```

     return webClient.post()

         .uri("/api/process")# macOS: brew install mongodb-community

         .contentType(MediaType.MULTIPART_FORM_DATA)

         .body(BodyInserters.fromMultipartData(parts))# Ubuntu: sudo apt-get install mongodb- **Academic Records**: 10th & 12th marksheets

         .retrieve()

         .bodyToMono(ProcessingResult.class);# Windows: Download from mongodb.com

 }

 - **Certificates**: Transfer, migration, caste, domicile### **Batch Processing**

 // Batch processing

 public Mono<BatchProcessingResult> processBatch(BatchRequest request) {# Verify MongoDB connection

     return webClient.post()

         .uri("/api/process/documents")curl http://localhost:8000/health- **Entrance Documents**: Scorecards and admit cards

         .contentType(MediaType.APPLICATION_JSON)

         .bodyValue(request)# Check database_connected: true

         .retrieve()

         .bodyToMono(BatchProcessingResult.class);```- **Identity Documents**: Passport photos```python

 }

}

```

## API Integration Guideimport asyncio

## Docker Deployment



### Docker Build & Run

### REST API Endpoints### 🔄 Integration Optionsimport aiohttp

```bash

# Build image

docker build -t smart-document-processor .

#### **Single Document Processing**- **Single Document Processing**: Upload and process immediately

# Run container

docker run -d \```bash

--name doc-processor \

-p 8000:8000 \POST /api/process- **Batch Processing**: Multiple documents from URLsasync def process_documents(file_paths):

-e GEMINI_API_KEY=your_slm_api_key_here \

-e DEBUG=false \Content-Type: multipart/form-data

smart-document-processor

- **MongoDB Integration**: Automatic data storage    async with aiohttp.ClientSession() as session:

# Check logs

docker logs doc-processor# Form fields:



# Test health- file: [IMAGE/PDF FILE]- **Webhook Callbacks**: Async result delivery        tasks = []

curl http://localhost:8000/health

```- document_type: "aadhaar_card" (optional)



### Docker Compose (Recommended)- student_id: "STUDENT_123" (optional, for MongoDB storage)- **Service Registration**: External service connectivity        for file_path in file_paths:



Create `docker-compose.yml`:````

```yaml

version: '3.8'            task = process_single_document(session, file_path)

services:

document-processor:**Example using curl:**

 build: .

 ports:```bash### 🎯 Advanced Features            tasks.append(task)

   - "8000:8000"

 environment:curl -X POST "http://localhost:8000/api/process" \

   - GEMINI_API_KEY=${SLM_API_KEY}

   - MONGODB_URL=mongodb://mongodb:27017/document_processor  -F "file=@/path/to/aadhaar.jpg" \- **Data Normalization**: Consistent field formatting

   - DEBUG=false

 depends_on:  -F "document_type=aadhaar_card" \

   - mongodb

 restart: unless-stopped  -F "student_id=STUDENT_123"- **Validation Rules**: Document-specific checks        results = await asyncio.gather(*tasks)



mongodb:```

 image: mongo:7-jammy

 ports:- **Confidence Thresholds**: Quality assurance return results

   - "27017:27017"

 volumes:**Example Response:**

   - mongodb_data:/data/db

 restart: unless-stopped````json- **Error Handling**: Comprehensive error responses



volumes:{

mongodb_data:

```  "success": true,- **Monitoring**: Health checks and logging# Process multiple documents concurrently



Start services:  "document_type": "aadhaar_card",

```bash

# Set environment variable  "confidence_score": 0.95,results = asyncio.run(process_documents(["doc1.jpg", "doc2.jpg"]))

export SLM_API_KEY=your_slm_api_key_here

"processing_time": 2.34,

# Start all services

docker-compose up -d  "extracted_data": {## 🔧 Installation & Setup```



# View logs    "name": "राम प्रसाद शर्मा",

docker-compose logs -f

 "aadhaar_number": "1234 5678 9012",

# Stop services

docker-compose down    "date_of_birth": "01/01/1990",

```

 "gender": "MALE",### Prerequisites### **Validation Results**

### Cloud Deployment

 "address": "123 Sample Street, City, State - 123456"

#### **Azure Container Apps**

```bash  },- **Python**: 3.10 or higher

# Deploy container app

az containerapp create \  "validation_issues": [],

--name smart-doc-processor \

--resource-group ocr-service \  "metadata": {- **MongoDB**: 4.4+ (optional, for data storage)```json

--environment ocr-env \

--image your-registry/smart-document-processor:latest \    "mongodb_stored": true,

--target-port 8000 \

--ingress external \    "student_id": "STUDENT_123"- **Gemini API Key**: [Get from Google AI Studio](https://makersuite.google.com/app/apikey){

--env-vars GEMINI_API_KEY=your_slm_api_key_here

```  }



#### **Google Cloud Run**}  "success": true,

```bash

gcloud run deploy smart-document-processor \````

--image gcr.io/PROJECT-ID/smart-document-processor \

--platform managed \### 🐍 Local Development Setup "document_type": "aadhaar_card",

--region us-central1 \

--allow-unauthenticated \#### **Batch Processing from URLs**

--set-env-vars GEMINI_API_KEY=your_slm_api_key_here

```````bash "extracted_data": {



## TestingPOST /api/process/documents



### Run TestsContent-Type: application/json1. **Clone Repository**    "name": "John Doe",



```bash

# Install development dependencies

pip install -r requirements-dev.txt{   ```bash    "aadhaar_number": "1234 5678 9012",



# Run all tests  "document_uris": [

pytest

 "https://example.com/doc1.jpg",   git clone https://github.com/sanjanb/ocr-automation-pipeline.git    "date_of_birth": "15/08/1995",

# Run with coverage

pytest --cov=src --cov-report=html --cov-report=term    "https://example.com/doc2.pdf"



# Run specific test file  ],   cd ocr-automation-pipeline    "address": "123 Main Street, Bangalore, Karnataka"

pytest tests/test_api.py -v

"student_id": "STUDENT_123",

# Run specific test

pytest tests/test_core.py::test_document_processing -v  "document_type": "marksheet_10th",   ```  },

```

"batch_name": "admission_batch_1",

### API Testing

"callback_url": "https://your-app.com/callback"  "confidence_score": 0.92,

```bash

# Test health endpoint}

curl http://localhost:8000/health

```2. **Create Virtual Environment**  "validation_issues": [],

# Test with sample document

curl -X POST "http://localhost:8000/api/process" \

-F "file=@tests/fixtures/sample_aadhaar.jpg" \

-F "document_type=aadhaar_card"#### **MongoDB Fetch and Process**   ```bash  "processing_time": 2.1,



# Test batch processing```bash

curl -X POST "http://localhost:8000/api/process/documents" \

-H "Content-Type: application/json" \POST /api/fetch-and-process   python -m venv venv  "model_used": "gemini-2.0-flash-exp"

-d '{"document_uris": ["https://example.com/test.jpg"]}'

```Content-Type: application/json



## Supported Documents   }



### Government Documents{



| Document Type | Code | Fields Extracted | Confidence |  "collection_name": "raw_documents",   # Activate (choose based on your OS)```

|--------------|------|------------------|------------|

| **Aadhaar Card** | `aadhaar_card` | Name, Number, DOB, Gender, Address | 95%+ |  "filter_criteria": {"student_id": "STUDENT_123"},

| **Caste Certificate** | `caste_certificate` | Name, Caste, Issue Date, Authority | 90%+ |

| **Domicile Certificate** | `domicile_certificate` | Name, State, Issue Date, Validity | 88%+ |  "uri_field_name": "cloudinary_url",   source venv/bin/activate      # Linux/macOS



### Academic Documents  "batch_size": 10



| Document Type | Code | Fields Extracted | Confidence |}   venv\Scripts\activate         # Windows PowerShell## 🧪 **Testing**

|--------------|------|------------------|------------|

| **10th Marksheet** | `marksheet_10th` | Name, Roll No, Marks, Board, Year | 92%+ |````

| **12th Marksheet** | `marksheet_12th` | Name, Roll No, Marks, Stream, Board | 93%+ |

| **Transfer Certificate** | `transfer_certificate` | Name, Class, School, Issue Date | 89%+ |venv\Scripts\activate.bat # Windows Command Prompt

| **Migration Certificate** | `migration_certificate` | Name, Course, University, Issue Date | 87%+ |

### Integration Examples

### Entrance & Admission

````````bash

| Document Type | Code | Fields Extracted | Confidence |

|--------------|------|------------------|------------|#### **JavaScript/Node.js**

| **Entrance Scorecard** | `entrance_scorecard` | Name, Roll No, Score, Rank, Exam | 91%+ |

| **Admit Card** | `admit_card` | Name, Roll No, Exam Center, Date | 94%+ |```javascript# Run all tests

| **Passport Photo** | `passport_photo` | Face Detection, Quality Check | 96%+ |

const axios = require('axios');

## Security & Configuration

const FormData = require('form-data');3. **Install Dependencies**pytest tests/ -v

### Security Features

const fs = require('fs');

- **Input Validation**: All uploads sanitized and validated

- **Rate Limiting**: DoS protection with configurable limits```bash

- **API Key Security**: Environment-based secret management

- **File Type Validation**: Only allowed formats processed// Single document processing

- **Size Limits**: Configurable maximum file sizes

- **Error Sanitization**: No sensitive data in error responsesasync function processDocument(filePath, documentType) {   pip install --upgrade pip# Run with coverage

- **HTTPS Support**: SSL/TLS ready for production

const form = new FormData();

### Configuration Options

form.append('file', fs.createReadStream(filePath));   pip install -r requirements.txtpytest tests/ --cov=src --cov-report=html

Edit `.env` file for customization:

form.append('document_type', documentType);

```env

# AI Configurationform.append('student_id', 'STUDENT_123');```````

GEMINI_API_KEY=your_slm_api_key_here

GEMINI_MODEL=slm-model-default



# Server Configurationconst response = await axios.post('http://localhost:8000/api/process', form, {# Run specific test file

HOST=0.0.0.0

PORT=8000 headers: form.getHeaders()

DEBUG=false

LOG_LEVEL=INFO});4. **Environment Configuration**pytest tests/test_api.py -v



# Processing Configuration

MAX_FILE_SIZE=10485760        # 10MB

PROCESSING_TIMEOUT=60         # secondsreturn response.data;   ````bash

MIN_CONFIDENCE_THRESHOLD=0.5  # minimum confidence

}

# Database Configuration (optional)

MONGODB_URL=mongodb://localhost:27017/document_processorcp .env.example .env# Test with mock data



# Rate Limiting// Batch processing

RATE_LIMIT_PER_HOUR=100

RATE_LIMIT_BURST=10async function processBatch(documentUris, studentId) {   ```python -m pytest tests/test_core.py::TestDocumentProcessor::test_process_document_success



# CORS (comma-separated origins)const response = await axios.post('http://localhost:8000/api/process/documents', {

CORS_ORIGINS=http://localhost:3000,http://localhost:8080

``` document_uris: documentUris,   ````



### Production Security Checklist student_id: studentId,



- [ ] **Environment Variables**: All secrets in environment, not code document_type: 'aadhaar_card'   Edit `.env` file:

- [ ] **HTTPS**: SSL/TLS certificates configured

- [ ] **Rate Limiting**: Appropriate limits set});

- [ ] **Input Validation**: All inputs sanitized

- [ ] **Logging**: Security events logged````env## **Deployment**

- [ ] **Monitoring**: Health checks and alerts configured

- [ ] **Updates**: Dependencies regularly updatedreturn response.data;

- [ ] **Backup**: Data backup strategy implemented

}   # Required: Get from https://makersuite.google.com/app/apikey

## Performance & Scaling

```

### Benchmarks

GEMINI_API_KEY=your_actual_api_key_here### **Production Deployment**

| Metric | Value | Notes |

|--------|--------|-------|#### **Python Client**

| **Processing Time** | 2-4 seconds | Average per document |

| **Memory Usage** | <500MB | Efficient processing |```python

| **Concurrent Users** | 50-100 | Single instance |

| **Throughput** | 15-25 docs/min | Depends on document complexity |import requests

| **Docker Image Size** | ~150MB | Optimized build |

# Optional: Database (remove if not using MongoDB)```bash

### Performance Optimization

# Single document processing

#### **Single Instance Optimization**

```bashdef process_document(file_path, document_type="aadhaar_card"):   MONGODB_URL=mongodb://localhost:27017/document_processor# 1. Build production image

# Use multiple workers

uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000 with open(file_path, 'rb') as f:



# Optimize for production     files = {'file': f}   docker build -t document-processor:latest .

uvicorn app:app --workers 2 --worker-class uvicorn.workers.UvicornWorker

```     data = {



#### **Kubernetes Deployment**         'document_type': document_type,   # Server Configuration



```yaml         'student_id': 'STUDENT_123'

# deployment.yaml

apiVersion: apps/v1     }   HOST=0.0.0.0# 2. Run with production settings

kind: Deployment

metadata:     response = requests.post('http://localhost:8000/api/process',

name: document-processor

spec:                            files=files, data=data)   PORT=8000docker run -d \

replicas: 3

selector: return response.json()

 matchLabels:

   app: document-processorDEBUG=false  -p 8000:8000 \

template:

 metadata:# Batch processing

   labels:

     app: document-processordef process_batch(document_uris, student_id):   LOG_LEVEL=INFO  -e GEMINI_API_KEY=your_key \

 spec:

   containers: payload = {

   - name: document-processor

     image: smart-document-processor:latest     'document_uris': document_uris,   ```  -e DEBUG=false \

     ports:

     - containerPort: 8000     'student_id': student_id,

     env:

     - name: GEMINI_API_KEY     'document_type': 'marksheet_10th'   -e LOG_LEVEL=INFO \

       valueFrom:

         secretKeyRef: }

           name: slm-secret

           key: api-key response = requests.post('http://localhost:8000/api/process/documents',    ````

     resources:

       requests:                        json=payload)

         memory: "256Mi"

         cpu: "200m" return response.json()5. **Start the Service** --name document-processor \

       limits:

         memory: "512Mi"```

         cpu: "500m"

```````bash document-processor:latest



## Contributing#### **Java/Spring Boot**



We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.```java   # Development mode (with auto-reload)



### Development Setup@Service



1. **Fork & Clone**public class DocumentProcessorService {   uvicorn app:app --reload --host 0.0.0.0 --port 8000# 3. Check health

```bash

git clone https://github.com/your-username/ocr-automation-pipeline.git

cd ocr-automation-pipeline

``` @Value("${ocr.service.base-url:http://localhost:8000}")   curl http://localhost:8000/health



2. **Create Development Environment** private String ocrServiceUrl;

```bash

python -m venv venv    # Production mode```

source venv/bin/activate

pip install -r requirements-dev.txt private final WebClient webClient;

```

 uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1

3. **Run Tests**

```bash public DocumentProcessorService(WebClient.Builder webClientBuilder) {

pytest --cov=src

```     this.webClient = webClientBuilder   ```### **Cloud Deployment**



## Support         .baseUrl(ocrServiceUrl)



### Documentation         .build();   ````



- **[API Reference](Docs/API.md)**: Complete endpoint documentation }

- **[Setup Guide](Docs/SETUP.md)**: Detailed installation instructions

- **[Security Policy](SECURITY.md)**: Security best practices 6. **Verify Installation**- **AWS**: Deploy to ECS, Lambda, or Elastic Beanstalk

- **[Changelog](CHANGELOG.md)**: Version history

// Single document processing

### Getting Help

public Mono<ProcessingResult> processDocument(MultipartFile file,    ```bash- **Google Cloud**: Deploy to Cloud Run or App Engine

- **Issues**: [GitHub Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)

- **Discussions**: [GitHub Discussions](https://github.com/sanjanb/ocr-automation-pipeline/discussions)                                             String documentType,



### Bug Reports                                             String studentId) {   # Test health endpoint- **Azure**: Deploy to Container Instances or App Service



Please include:     MultiValueMap<String, HttpEntity<?>> parts = new LinkedMultiValueMap<>();

- Environment details (Python version, OS)

- Steps to reproduce     parts.add("file", new FileSystemResource(file.getResource().getFile()));   curl http://localhost:8000/health- **Heroku**: One-click deployment with buildpacks

- Expected vs actual behavior

- Sample document (if possible)     parts.add("document_type", new HttpEntity<>(documentType));

- Error logs

  parts.add("student_id", new HttpEntity<>(studentId));

## License



This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

  return webClient.post()   # Should return: {"status":"healthy","version":"2.0.0",...}## 📈 **Performance Benchmarks**

### Commercial Use

      .uri("/api/process")

This software is free for commercial use. Attribution is appreciated but not required.

      .contentType(MediaType.MULTIPART_FORM_DATA)   ```

## Project Status

      .body(BodyInserters.fromMultipartData(parts))

- **Active Development**: Regular updates and maintenance

- **Production Ready**: Used in real-world applications         .retrieve()| Metric | This Solution | Traditional OCR Pipeline |

- **Well Documented**: Comprehensive guides and examples

- **Community Supported**: Open to contributions         .bodyToMono(ProcessingResult.class);



**Latest Version**: 2.0.0 (FastAPI Migration Complete) }### MongoDB Setup (Optional)| ------------------- | ---------------- | ------------------------ |



---



## Acknowledgments // Batch processing| **Processing Time** | 2-5 seconds | 15-30 seconds |



- **Small Language Model (SLM)** for efficient document processing capabilities public Mono<BatchProcessingResult> processBatch(BatchRequest request) {

- **FastAPI Team** for the excellent async web framework

- **MongoDB Team** for flexible document storage     return webClient.post()If you want to store processed documents:| **Accuracy** | 85-95% | 70-85% |

- **Open Source Community** for inspiration and contributions

      .uri("/api/process/documents")

---

      .contentType(MediaType.APPLICATION_JSON)| **Setup Time** | 2 minutes | 30+ minutes |

<div align="center">

      .bodyValue(request)

**Star this repository if it helps you build better document processing solutions!**

      .retrieve()```bash| **Dependencies**    | <100MB           | 1GB+                     |

[Back to Top](#smart-document-processor---ai-powered-ocr-microservice)

      .bodyToMono(BatchProcessingResult.class);

</div>
}# Option 1: Docker MongoDB| **API Calls**       | 1 call           | 3-5 calls                |

}

```docker run -d -p 27017:27017 --name mongodb mongo:latest| **Infrastructure**  | Serverless ready | Requires GPU/CPU         |



#### **cURL Examples**

```bash

# Single document processing# Option 2: Install locally## 🛠️ **Development**

curl -X POST "http://localhost:8000/api/process" \

-F "file=@document.jpg" \# macOS: brew install mongodb-community

-F "document_type=aadhaar_card" \

-F "student_id=STUDENT_123"# Ubuntu: sudo apt-get install mongodb### **Project Structure**



# Batch processing# Windows: Download from mongodb.com

curl -X POST "http://localhost:8000/api/process/documents" \

-H "Content-Type: application/json" \```

-d '{

"document_uris": ["https://example.com/doc1.jpg"],# Verify MongoDB connectionocr-automation-pipeline/

"student_id": "STUDENT_123",

"document_type": "marksheet_10th"curl http://localhost:8000/health├── src/document_processor/ # Core processing logic

}'

# Check database_connected: true│ ├── core.py # Main processor class

# Health check

curl http://localhost:8000/health````│ ├── schemas.py             # Document schemas



# Get supported document schemas│   └── config.py              # Configuration management

curl http://localhost:8000/schemas

```## 🔌 API Integration Guide├── tests/                     # Comprehensive test suite



## Docker Deployment├── .github/workflows/         # CI/CD pipeline



### Docker Build & Run### 🌐 REST API Endpoints├── app.py                     # FastAPI application



```bash├── Dockerfile                 # Container configuration

# Build image

docker build -t smart-document-processor .#### **Single Document Processing**├── docker-compose.yml         # Local development



# Run container```bash└── requirements.txt           # Dependencies

docker run -d \

--name doc-processor \POST /api/process```

-p 8000:8000 \

-e GEMINI_API_KEY=your_api_key_here \Content-Type: multipart/form-data

-e DEBUG=false \

smart-document-processor### **Contributing**



# Check logs# Form fields:

docker logs doc-processor

- file: [IMAGE/PDF FILE]1. Fork the repository

# Test health

curl http://localhost:8000/health- document_type: "aadhaar_card" (optional)2. Create feature branch (`git checkout -b feature/amazing-feature`)

```

- student_id: "STUDENT_123" (optional, for MongoDB storage)3. Commit changes (`git commit -m 'Add amazing feature'`)

### Docker Compose (Recommended)

```4. Push to branch (`git push origin feature/amazing-feature`)

Create `docker-compose.yml`:

```yaml5. Open Pull Request

version: '3.8'

services:**Example using curl:**

document-processor:

build: .```bash### **Code Quality**

ports:

- "8000:8000"curl -X POST "http://localhost:8000/api/process" \

environment:

- GEMINI_API_KEY=${GEMINI_API_KEY}  -F "file=@/path/to/aadhaar.jpg" \- **Linting**: `flake8`, `black`, `isort`

- MONGODB_URL=mongodb://mongodb:27017/document_processor

- DEBUG=false  -F "document_type=aadhaar_card" \- **Type Checking**: `mypy`

depends_on:

- mongodb  -F "student_id=STUDENT_123"- **Testing**: `pytest` with >90% coverage

restart: unless-stopped

```- **Security**: `bandit`, `safety`

mongodb:

image: mongo:7-jammy

ports:

- "27017:27017"**Example Response:**## **Demo Features**

volumes:

- mongodb_data:/data/db```json

restart: unless-stopped

{### **Web Interface**

volumes:

mongodb_data:  "success": true,

```

"document_type": "aadhaar_card",- Modern, responsive design

Start services:

```bash  "confidence_score": 0.95,- Mobile-friendly upload

# Set environment variable

export GEMINI_API_KEY=your_api_key_here  "processing_time": 2.34,- Real-time processing updates



# Start all services  "extracted_data": {- Confidence scoring

docker-compose up -d

"name": "राम प्रसाद शर्मा",- Validation issue highlighting

# View logs

docker-compose logs -f    "aadhaar_number": "1234 5678 9012",- JSON export functionality



# Stop services    "date_of_birth": "01/01/1990",

docker-compose down

```    "gender": "MALE",### **API Documentation**



### Cloud Deployment    "address": "123 Sample Street, City, State - 123456"



#### **Azure Container Apps**  },- Interactive Swagger UI

```bash

# Login to Azure  "validation_issues": [],  ReDoc documentation

az login

"metadata": {- 🔧 Request/response schemas

# Create resource group

az group create --name ocr-service --location eastus    "mongodb_stored": true,- Try-it-out functionality



# Create container app environment    "student_id": "STUDENT_123"

az containerapp env create \

--name ocr-env \  }### **Monitoring & Debugging**

--resource-group ocr-service \

--location eastus}



# Deploy container app```- Structured logging

az containerapp create \

--name smart-doc-processor \- Health check endpoints

--resource-group ocr-service \

--environment ocr-env \#### **Batch Processing from URLs**- Processing metrics

--image your-registry/smart-document-processor:latest \

--target-port 8000 \```bash- Error tracking

--ingress external \

--env-vars GEMINI_API_KEY=your_api_key_herePOST /api/process/documents

```

Content-Type: application/json## 🏆 **Why Choose This Solution?**

#### **AWS ECS/Fargate**

```bash

# Build and push to ECR

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com{### **For Hackathons**



docker tag smart-document-processor:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-document-processor:latest  "document_uris": [



docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-document-processor:latest    "https://example.com/doc1.jpg",- **Quick Setup**: Demo ready in 2 minutes



# Create ECS service using AWS CLI or Console    "https://example.com/doc2.pdf"- **Impressive Results**: High accuracy, fast processing

```

],- **Professional UI**: Judge-ready interface

#### **Google Cloud Run**

```bash  "student_id": "STUDENT_123",- **Technical Depth**: Modern architecture, comprehensive features

# Build and deploy

gcloud builds submit --tag gcr.io/PROJECT-ID/smart-document-processor  "document_type": "marksheet_10th",



gcloud run deploy smart-document-processor \  "batch_name": "admission_batch_1",### **For Production**

--image gcr.io/PROJECT-ID/smart-document-processor \

--platform managed \  "callback_url": "https://your-app.com/callback"

--region us-central1 \

--allow-unauthenticated \}- **Scalable**: Async FastAPI, containerized

--set-env-vars GEMINI_API_KEY=your_api_key_here

``````- **Secure**: Input validation, error handling



## Testing- **Observable**: Logging, monitoring, health checks



### Run Tests#### **MongoDB Fetch and Process**- **Maintainable**: Clean code, comprehensive tests



```bash```bash

# Install development dependencies

pip install -r requirements-dev.txtPOST /api/fetch-and-process### **For Developers**



# Run all testsContent-Type: application/json

pytest

- **Modern Python**: Type hints, async/await, Pydantic

# Run with coverage

pytest --cov=src --cov-report=html --cov-report=term{- **Well Tested**: >90% coverage, CI/CD pipeline



# Run specific test file  "collection_name": "raw_documents",  **Documented**: Comprehensive docs, API specs

pytest tests/test_api.py -v

"filter_criteria": {"student_id": "STUDENT_123"},- **Extensible**: Plugin architecture, configurable

# Run specific test

pytest tests/test_core.py::test_document_processing -v  "uri_field_name": "cloudinary_url",

```

"batch_size": 10## **Support**

### Test Coverage Report

}

```bash

# Generate HTML coverage report```- 🐛 **Issues**: [GitHub Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)

pytest --cov=src --cov-report=html

- 💬 **Discussions**: [GitHub Discussions](https://github.com/sanjanb/ocr-automation-pipeline/discussions)

# Open in browser

open htmlcov/index.html  # macOS### Integration Examples- **Documentation**: [Wiki](https://github.com/sanjanb/ocr-automation-pipeline/wiki)

xdg-open htmlcov/index.html  # Linux

start htmlcov/index.html  # Windows- **Examples**: [Examples Repository](https://github.com/sanjanb/ocr-automation-pipeline/tree/main/examples)

```

#### **JavaScript/Node.js**

### API Testing

```javascript---

```bash

# Test health endpointconst axios = require('axios');

curl http://localhost:8000/health

const FormData = require('form-data');**Built with ❤️ for MIT Hackathon 2025**

# Test with sample document

curl -X POST "http://localhost:8000/api/process" \const fs = require('fs');_Transform documents, not just extract text_

-F "file=@tests/fixtures/sample_aadhaar.jpg" \

-F "document_type=aadhaar_card"

// Single document processing

# Test batch processingasync function processDocument(filePath, documentType) {

curl -X POST "http://localhost:8000/api/process/documents" \  const form = new FormData();

-H "Content-Type: application/json" \  form.append('file', fs.createReadStream(filePath));

-d '{"document_uris": ["https://example.com/test.jpg"]}'  form.append('document_type', documentType);

```  form.append('student_id', 'STUDENT_123');



## Supported Documents  const response = await axios.post('http://localhost:8000/api/process', form, {

headers: form.getHeaders()

### Government Documents  });



| Document Type | Code | Fields Extracted | Confidence |  return response.data;

|--------------|------|------------------|------------|}

| **Aadhaar Card** | `aadhaar_card` | Name, Number, DOB, Gender, Address | 95%+ |

| **Caste Certificate** | `caste_certificate` | Name, Caste, Issue Date, Authority | 90%+ |// Batch processing

| **Domicile Certificate** | `domicile_certificate` | Name, State, Issue Date, Validity | 88%+ |async function processBatch(documentUris, studentId) {

const response = await axios.post('http://localhost:8000/api/process/documents', {

### Academic Documents    document_uris: documentUris,

student_id: studentId,

| Document Type | Code | Fields Extracted | Confidence |    document_type: 'aadhaar_card'

|--------------|------|------------------|------------|  });

| **10th Marksheet** | `marksheet_10th` | Name, Roll No, Marks, Board, Year | 92%+ |

| **12th Marksheet** | `marksheet_12th` | Name, Roll No, Marks, Stream, Board | 93%+ |  return response.data;

| **Transfer Certificate** | `transfer_certificate` | Name, Class, School, Issue Date | 89%+ |}

| **Migration Certificate** | `migration_certificate` | Name, Course, University, Issue Date | 87%+ |````



### Entrance & Admission#### **Python Client**



| Document Type | Code | Fields Extracted | Confidence |```python

|--------------|------|------------------|------------|import requests

| **Entrance Scorecard** | `entrance_scorecard` | Name, Roll No, Score, Rank, Exam | 91%+ |

| **Admit Card** | `admit_card` | Name, Roll No, Exam Center, Date | 94%+ |# Single document processing

| **Passport Photo** | `passport_photo` | Face Detection, Quality Check | 96%+ |def process_document(file_path, document_type="aadhaar_card"):

with open(file_path, 'rb') as f:

### Adding New Document Types        files = {'file': f}

  data = {

To add support for new document types:            'document_type': document_type,

      'student_id': 'STUDENT_123'

1. **Define Schema** in `src/document_processor/schemas.py`:        }

```python        response = requests.post('http://localhost:8000/api/process',

DOCUMENT_SCHEMAS['new_document'] = {                               files=files, data=data)

 'description': 'New Document Type',    return response.json()

 'required_fields': ['field1', 'field2'],

 'optional_fields': ['field3'],# Batch processing

 'validation_rules': {def process_batch(document_uris, student_id):

     'field1': 'Pattern or validation rule'    payload = {

 }        'document_uris': document_uris,

}        'student_id': student_id,

```        'document_type': 'marksheet_10th'

}

2. **Update Normalizer** in `src/document_processor/normalizer.py`:    response = requests.post('http://localhost:8000/api/process/documents',

```python                           json=payload)

def normalize_new_document(data: dict) -> dict:    return response.json()

 return {```

     'field1': normalize_text(data.get('field1')),

     'field2': normalize_date(data.get('field2'))#### **Java/Spring Boot**

 }

``````java

@Service

3. **Add Tests** in `tests/test_new_document.py`public class DocumentProcessorService {



4. **Update Documentation**    @Value("${ocr.service.base-url:http://localhost:8000}")

private String ocrServiceUrl;

## Security & Configuration

private final WebClient webClient;

### Security Features

public DocumentProcessorService(WebClient.Builder webClientBuilder) {

- **Input Validation**: All uploads sanitized and validated        this.webClient = webClientBuilder

- **Rate Limiting**: DoS protection with configurable limits            .baseUrl(ocrServiceUrl)

- **API Key Security**: Environment-based secret management            .build();

- **File Type Validation**: Only allowed formats processed    }

- **Size Limits**: Configurable maximum file sizes

- **Error Sanitization**: No sensitive data in error responses    // Single document processing

- **HTTPS Support**: SSL/TLS ready for production    public Mono<ProcessingResult> processDocument(MultipartFile file,

                                          String documentType,

### Configuration Options                                                String studentId) {

  MultiValueMap<String, HttpEntity<?>> parts = new LinkedMultiValueMap<>();

Edit `.env` file for customization:        parts.add("file", new FileSystemResource(file.getResource().getFile()));

  parts.add("document_type", new HttpEntity<>(documentType));

```env        parts.add("student_id", new HttpEntity<>(studentId));

# AI Configuration

GEMINI_API_KEY=your_api_key_here        return webClient.post()

GEMINI_MODEL=gemini-2.0-flash-exp            .uri("/api/process")

      .contentType(MediaType.MULTIPART_FORM_DATA)

# Server Configuration            .body(BodyInserters.fromMultipartData(parts))

HOST=0.0.0.0            .retrieve()

PORT=8000            .bodyToMono(ProcessingResult.class);

DEBUG=false    }

LOG_LEVEL=INFO

// Batch processing

# Processing Configuration    public Mono<BatchProcessingResult> processBatch(BatchRequest request) {

MAX_FILE_SIZE=10485760        # 10MB        return webClient.post()

PROCESSING_TIMEOUT=60         # seconds            .uri("/api/process/documents")

MIN_CONFIDENCE_THRESHOLD=0.5  # minimum confidence            .contentType(MediaType.APPLICATION_JSON)

      .bodyValue(request)

# Database Configuration (optional)            .retrieve()

MONGODB_URL=mongodb://localhost:27017/document_processor            .bodyToMono(BatchProcessingResult.class);

}

# Rate Limiting}

RATE_LIMIT_PER_HOUR=100```

RATE_LIMIT_BURST=10

#### **cURL Examples**

# CORS (comma-separated origins)

CORS_ORIGINS=http://localhost:3000,http://localhost:8080```bash

```# Single document processing

curl -X POST "http://localhost:8000/api/process" \

### Production Security Checklist  -F "file=@document.jpg" \

-F "document_type=aadhaar_card" \

- [ ] **Environment Variables**: All secrets in environment, not code  -F "student_id=STUDENT_123"

- [ ] **HTTPS**: SSL/TLS certificates configured

- [ ] **Rate Limiting**: Appropriate limits set# Batch processing

- [ ] **Input Validation**: All inputs sanitizedcurl -X POST "http://localhost:8000/api/process/documents" \

- [ ] **Logging**: Security events logged  -H "Content-Type: application/json" \

- [ ] **Monitoring**: Health checks and alerts configured  -d '{

- [ ] **Updates**: Dependencies regularly updated    "document_uris": ["https://example.com/doc1.jpg"],

- [ ] **Backup**: Data backup strategy implemented    "student_id": "STUDENT_123",

"document_type": "marksheet_10th"

## Performance & Scaling  }'



### Benchmarks# Health check

curl http://localhost:8000/health

| Metric | Value | Notes |

|--------|--------|-------|# Get supported document schemas

| **Processing Time** | 2-4 seconds | Average per document |curl http://localhost:8000/schemas

| **Memory Usage** | <500MB | Efficient processing |```

| **Concurrent Users** | 50-100 | Single instance |

| **Throughput** | 15-25 docs/min | Depends on document complexity |## Docker Deployment

| **Docker Image Size** | ~150MB | Optimized build |

### Docker Build & Run

### Performance Optimization

```bash

#### **Single Instance Optimization**# Build image

```bashdocker build -t smart-document-processor .

# Use multiple workers

uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000# Run container

docker run -d \

# Optimize for production  --name doc-processor \

uvicorn app:app --workers 2 --worker-class uvicorn.workers.UvicornWorker  -p 8000:8000 \

```  -e GEMINI_API_KEY=your_api_key_here \

-e DEBUG=false \

#### **Load Balancing Setup**  smart-document-processor



**nginx.conf example:**# Check logs

```nginxdocker logs doc-processor

upstream document_processor {

server 127.0.0.1:8000;# Test health

server 127.0.0.1:8001;curl http://localhost:8000/health

server 127.0.0.1:8002;```

}

### Docker Compose (Recommended)

server {

listen 80;Create `docker-compose.yml`:

server_name your-domain.com;

```yaml

location / {version: "3.8"

  proxy_pass http://document_processor;services:

  proxy_set_header Host $host;  document-processor:

  proxy_set_header X-Real-IP $remote_addr;    build: .

}    ports:

}      - "8000:8000"

```    environment:

- GEMINI_API_KEY=${GEMINI_API_KEY}

#### **Kubernetes Deployment**      - MONGODB_URL=mongodb://mongodb:27017/document_processor

- DEBUG=false

```yaml    depends_on:

# deployment.yaml      - mongodb

apiVersion: apps/v1    restart: unless-stopped

kind: Deployment

metadata:  mongodb:

name: document-processor    image: mongo:7-jammy

spec:    ports:

replicas: 3      - "27017:27017"

selector:    volumes:

matchLabels:      - mongodb_data:/data/db

app: document-processor    restart: unless-stopped

template:

metadata:volumes:

labels:  mongodb_data:

  app: document-processor```

spec:

containers:Start services:

- name: document-processor

  image: smart-document-processor:latest```bash

  ports:# Set environment variable

  - containerPort: 8000export GEMINI_API_KEY=your_api_key_here

  env:

  - name: GEMINI_API_KEY# Start all services

    valueFrom:docker-compose up -d

      secretKeyRef:

        name: gemini-secret# View logs

        key: api-keydocker-compose logs -f

  resources:

    requests:# Stop services

      memory: "256Mi"docker-compose down

      cpu: "200m"```

    limits:

      memory: "512Mi"### Cloud Deployment

      cpu: "500m"

---#### **Azure Container Apps**

apiVersion: v1

kind: Service```bash

metadata:# Login to Azure

name: document-processor-serviceaz login

spec:

selector:# Create resource group

app: document-processoraz group create --name ocr-service --location eastus

ports:

- protocol: TCP# Create container app environment

port: 80az containerapp env create \

targetPort: 8000  --name ocr-env \

type: LoadBalancer  --resource-group ocr-service \

```  --location eastus



## Contributing# Deploy container app

az containerapp create \

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.  --name smart-doc-processor \

--resource-group ocr-service \

### Development Setup  --environment ocr-env \

--image your-registry/smart-document-processor:latest \

1. **Fork & Clone**  --target-port 8000 \

```bash  --ingress external \

git clone https://github.com/your-username/ocr-automation-pipeline.git  --env-vars GEMINI_API_KEY=your_api_key_here

cd ocr-automation-pipeline```

```

#### **AWS ECS/Fargate**

2. **Create Development Environment**

```bash```bash

python -m venv venv# Build and push to ECR

source venv/bin/activateaws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

pip install -r requirements-dev.txt

```docker tag smart-document-processor:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-document-processor:latest



3. **Install Pre-commit Hooks**docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/smart-document-processor:latest

```bash

pre-commit install# Create ECS service using AWS CLI or Console

`````````

4. **Run Tests**#### **Google Cloud Run**

   ````bash

   pytest --cov=src```bash

   ```# Build and deploy
   ````

gcloud builds submit --tag gcr.io/PROJECT-ID/smart-document-processor

5. **Create Pull Request**

   - Follow conventional commit messagesgcloud run deploy smart-document-processor \

   - Add tests for new features --image gcr.io/PROJECT-ID/smart-document-processor \

   - Update documentation --platform managed \

   --region us-central1 \

### Contribution Types --allow-unauthenticated \

--set-env-vars GEMINI_API_KEY=your_api_key_here

- **Bug Fixes**: Fix issues and improve reliability```

- **Features**: Add new document types or capabilities

- **Documentation**: Improve guides and examples## Testing

- **Performance**: Optimize processing speed

- **Security**: Enhance security measures### Run Tests

- **Testing**: Improve test coverage

```bash

## Support# Install development dependencies

pip install -r requirements-dev.txt

### Documentation

# Run all tests

- **[API Reference](Docs/API.md)**: Complete endpoint documentationpytest

- **[Setup Guide](Docs/SETUP.md)**: Detailed installation instructions

- **[Security Policy](SECURITY.md)**: Security best practices# Run with coverage

- **[Changelog](CHANGELOG.md)**: Version historypytest --cov=src --cov-report=html --cov-report=term



### Getting Help# Run specific test file

pytest tests/test_api.py -v

- **Issues**: [GitHub Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)

- **Discussions**: [GitHub Discussions](https://github.com/sanjanb/ocr-automation-pipeline/discussions)# Run specific test

- **Email**: [Contact the maintainers](mailto:support@example.com)pytest tests/test_core.py::test_document_processing -v

```

### Bug Reports

### Test Coverage Report

Please include:

- Environment details (Python version, OS)```bash

- Steps to reproduce# Generate HTML coverage report

- Expected vs actual behaviorpytest --cov=src --cov-report=html

- Sample document (if possible)

- Error logs# Open in browser

open htmlcov/index.html # macOS

### Feature Requestsxdg-open htmlcov/index.html # Linux

start htmlcov/index.html # Windows

Please include:```

- Use case description

- Expected behavior### API Testing

- Implementation suggestions

- Priority level```bash

# Test health endpoint

## Licensecurl http://localhost:8000/health

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.# Test with sample document

curl -X POST "http://localhost:8000/api/process" \

### Commercial Use -F "file=@tests/fixtures/sample_aadhaar.jpg" \

-F "document_type=aadhaar_card"

This software is free for commercial use. Attribution is appreciated but not required.

# Test batch processing

## Project Statuscurl -X POST "http://localhost:8000/api/process/documents" \

-H "Content-Type: application/json" \

- **Active Development**: Regular updates and maintenance -d '{"document_uris": ["https://example.com/test.jpg"]}'

- **Production Ready**: Used in real-world applications```

- **Well Documented**: Comprehensive guides and examples

- **Community Supported**: Open to contributions## Supported Documents

**Latest Version**: 2.0.0 (FastAPI Migration Complete)### Government Documents

---| Document Type | Code | Fields Extracted | Confidence |

| ------------------------ | ---------------------- | ---------------------------------- | ---------- |

## Acknowledgments| **Aadhaar Card** | `aadhaar_card` | Name, Number, DOB, Gender, Address | 95%+ |

| **Caste Certificate** | `caste_certificate` | Name, Caste, Issue Date, Authority | 90%+ |

- **Google Gemini AI** for powerful document processing capabilities| **Domicile Certificate** | `domicile_certificate` | Name, State, Issue Date, Validity | 88%+ |

- **FastAPI Team** for the excellent async web framework

- **MongoDB Team** for flexible document storage### Academic Documents

- **Open Source Community** for inspiration and contributions

| Document Type | Code | Fields Extracted | Confidence |

---| ------------------------- | ----------------------- | ------------------------------------ | ---------- |

| **10th Marksheet** | `marksheet_10th` | Name, Roll No, Marks, Board, Year | 92%+ |

<div align="center">| **12th Marksheet**        | `marksheet_12th`        | Name, Roll No, Marks, Stream, Board  | 93%+       |

| **Transfer Certificate** | `transfer_certificate` | Name, Class, School, Issue Date | 89%+ |

**Star this repository if it helps you build better document processing solutions!**| **Migration Certificate** | `migration_certificate` | Name, Course, University, Issue Date | 87%+ |

[Back to Top](#smart-document-processor---ai-powered-ocr-microservice)### Entrance & Admission

</div>| Document Type          | Code                 | Fields Extracted                 | Confidence |
| ---------------------- | -------------------- | -------------------------------- | ---------- |
| **Entrance Scorecard** | `entrance_scorecard` | Name, Roll No, Score, Rank, Exam | 91%+       |
| **Admit Card**         | `admit_card`         | Name, Roll No, Exam Center, Date | 94%+       |
| **Passport Photo**     | `passport_photo`     | Face Detection, Quality Check    | 96%+       |

### Adding New Document Types

To add support for new document types:

1. **Define Schema** in `src/document_processor/schemas.py`:

   ```python
   DOCUMENT_SCHEMAS['new_document'] = {
       'description': 'New Document Type',
       'required_fields': ['field1', 'field2'],
       'optional_fields': ['field3'],
       'validation_rules': {
           'field1': 'Pattern or validation rule'
       }
   }
   ```

2. **Update Normalizer** in `src/document_processor/normalizer.py`:

   ```python
   def normalize_new_document(data: dict) -> dict:
       return {
           'field1': normalize_text(data.get('field1')),
           'field2': normalize_date(data.get('field2'))
       }
   ```

3. **Add Tests** in `tests/test_new_document.py`

4. **Update Documentation**

## Security & Configuration

### Security Features

- **Input Validation**: All uploads sanitized and validated
- **Rate Limiting**: DoS protection with configurable limits
- **API Key Security**: Environment-based secret management
- **File Type Validation**: Only allowed formats processed
- **Size Limits**: Configurable maximum file sizes
- **Error Sanitization**: No sensitive data in error responses
- **HTTPS Support**: SSL/TLS ready for production

### Configuration Options

Edit `.env` file for customization:

```env
# AI Configuration
GEMINI_API_KEY=your_slm_api_key_here
GEMINI_MODEL=slm-model-default

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Processing Configuration
MAX_FILE_SIZE=10485760        # 10MB
PROCESSING_TIMEOUT=60         # seconds
MIN_CONFIDENCE_THRESHOLD=0.5  # minimum confidence

# Database Configuration (optional)
MONGODB_URL=mongodb://localhost:27017/document_processor

# Rate Limiting
RATE_LIMIT_PER_HOUR=100
RATE_LIMIT_BURST=10

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Production Security Checklist

- [ ] **Environment Variables**: All secrets in environment, not code
- [ ] **HTTPS**: SSL/TLS certificates configured
- [ ] **Rate Limiting**: Appropriate limits set
- [ ] **Input Validation**: All inputs sanitized
- [ ] **Logging**: Security events logged
- [ ] **Monitoring**: Health checks and alerts configured
- [ ] **Updates**: Dependencies regularly updated
- [ ] **Backup**: Data backup strategy implemented

## Performance & Scaling

### Benchmarks

| Metric                | Value          | Notes                          |
| --------------------- | -------------- | ------------------------------ |
| **Processing Time**   | 2-4 seconds    | Average per document           |
| **Memory Usage**      | <500MB         | Efficient processing           |
| **Concurrent Users**  | 50-100         | Single instance                |
| **Throughput**        | 15-25 docs/min | Depends on document complexity |
| **Docker Image Size** | ~150MB         | Optimized build                |

### Performance Optimization

#### **Single Instance Optimization**

```bash
# Use multiple workers
uvicorn app:app --workers 4 --host 0.0.0.0 --port 8000

# Optimize for production
uvicorn app:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

#### **Load Balancing Setup**

**nginx.conf example:**

```nginx
upstream document_processor {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://document_processor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **Kubernetes Deployment**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: document-processor
  template:
    metadata:
      labels:
        app: document-processor
    spec:
      containers:
        - name: document-processor
          image: smart-document-processor:latest
          ports:
            - containerPort: 8000
          env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-secret
                  key: api-key
          resources:
            requests:
              memory: "256Mi"
              cpu: "200m"
            limits:
              memory: "512Mi"
              cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: document-processor-service
spec:
  selector:
    app: document-processor
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork & Clone**

   ```bash
   git clone https://github.com/your-username/ocr-automation-pipeline.git
   cd ocr-automation-pipeline
   ```

2. **Create Development Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **Install Pre-commit Hooks**

   ```bash
   pre-commit install
   ```

4. **Run Tests**

   ```bash
   pytest --cov=src
   ```

5. **Create Pull Request**
   - Follow conventional commit messages
   - Add tests for new features
   - Update documentation

### Contribution Types

- **Bug Fixes**: Fix issues and improve reliability
- **Features**: Add new document types or capabilities
- **Documentation**: Improve guides and examples
- **Performance**: Optimize processing speed
- **Security**: Enhance security measures
- **Testing**: Improve test coverage

## Support

### Documentation

- **[API Reference](Docs/API.md)**: Complete endpoint documentation
- **[Setup Guide](Docs/SETUP.md)**: Detailed installation instructions
- **[Security Policy](SECURITY.md)**: Security best practices
- **[Changelog](CHANGELOG.md)**: Version history

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/sanjanb/ocr-automation-pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sanjanb/ocr-automation-pipeline/discussions)
- **Email**: [Contact the maintainers](mailto:support@example.com)

### Bug Reports

Please include:

- Environment details (Python version, OS)
- Steps to reproduce
- Expected vs actual behavior
- Sample document (if possible)
- Error logs

### Feature Requests

Please include:

- Use case description
- Expected behavior
- Implementation suggestions
- Priority level

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Commercial Use

This software is free for commercial use. Attribution is appreciated but not required.

## Project Status

- **Active Development**: Regular updates and maintenance
- **Production Ready**: Used in real-world applications
- **Well Documented**: Comprehensive guides and examples
- **Community Supported**: Open to contributions

**Latest Version**: 2.0.0 (FastAPI Migration Complete)

---

## Acknowledgments

- **Small Language Model (SLM)** for efficient document processing capabilities
- **FastAPI Team** for the excellent async web framework
- **MongoDB Team** for flexible document storage
- **Open Source Community** for inspiration and contributions

---

<div align="center">

**Star this repository if it helps you build better document processing solutions!**

[⬆️ Back to Top](#smart-document-processor---ai-powered-ocr-microservice)

</div>
