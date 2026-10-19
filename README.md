# IntelliDocs — AI-Powered PDF Q&A Assistant

An enterprise-ready, AI-powered PDF question-answering assistant that lets users interact with their documents using natural language. IntelliDocs uses a production-oriented **Retrieval-Augmented Generation (RAG)** pipeline to extract, index, retrieve, and analyze PDF content, delivering context-grounded answers powered by Groq's high-throughput LLM inference.

The application combines FastAPI, ChromaDB, BAAI embeddings, cloud object storage, and PostgreSQL to provide secure, multi-user document management and conversational AI.

---

## 🚀 Key Features

- **Multi-Tenant Architecture:** JWT-based authentication and user-scoped document access.
- **Email OTP Verification:** Six-digit one-time passwords for account verification.
- **In-Memory PDF Processing:** Extract and process PDF content using PyPDF without temporary local files.
- **Retrieval-Augmented Generation (RAG):** Semantic document retrieval combined with LLM-generated answers.
- **Semantic Embeddings:** FastEmbed with `BAAI/bge-small-en-v1.5`.
- **Vector Search:** ChromaDB indexing with user and document metadata filtering.
- **Relevance Filtering:** Distance-threshold filtering to reduce responses based on irrelevant context.
- **Cloud Object Storage:** S3-compatible storage using Neon Object Storage, Cloudflare R2, or AWS S3.
- **Presigned Download URLs:** Temporary links for secure document downloads.
- **Persistent Chat History:** Multiple chat sessions with saved messages and conversation titles.
- **Adaptive LLM Fallback:** Configurable Groq model fallback to improve resilience.
- **Relational Database:** PostgreSQL or SQLite support through SQLAlchemy 2.0.
- **RESTful API:** Endpoints for authentication, user profiles, documents, and conversations.
- **Interactive API Documentation:** Built-in Swagger UI and ReDoc.
- **Docker Support:** Containerized application deployment.
- **PDF Upload:** Upload PDF documents and extract text using PyPDF.
- **Natural Language Q&A:** Ask questions about document content using everyday language.
---

## 🛠️ Technology Stack

| Component | Technology |
| --- | --- |
| Backend Framework | Python 3.10+, FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL / SQLite |
| ORM | SQLAlchemy 2.0 |
| Request Validation | Pydantic |
| Object Storage | Neon Object Storage / Cloudflare R2 / AWS S3 |
| Storage SDK | Boto3 |
| Vector Database | ChromaDB |
| Embedding Library | FastEmbed |
| Embedding Model | `BAAI/bge-small-en-v1.5` |
| LLM Inference | Groq API |
| LLM Models | Configurable Groq-supported chat models |
| Authentication | JWT using PyJWT |
| Password Hashing | Argon2 using `pwdlib` |
| Email Verification | `aiosmtplib` |
| PDF Processing | PyPDF |
| Frontend | HTML5, CSS3, JavaScript |
| Templates | Jinja2 |
| Deployment | Docker |

---

## 🧠 System Architecture

```
                         ┌──────────────────────┐
                         │      User / UI       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Backend    │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │ JWT Authentication   │
                         │ & User Authorization │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │   PDF Ingestion     │           │    Chat / Query     │
        └──────────┬──────────┘           └──────────┬──────────┘
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │ In-Memory PDF       │           │ FastEmbed Query     │
        │ Extraction (PyPDF)  │           │ Embedding           │
        └──────────┬──────────┘           └──────────┬──────────┘
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │ Text Chunking       │           │ ChromaDB Semantic   │
        │ 250 Words / 30      │           │ Search              │
        │ Words Overlap       │           └──────────┬──────────┘
        └──────────┬──────────┘                      │
                   │                                 ▼
                   ▼                      ┌─────────────────────┐
        ┌─────────────────────┐           │ User-Scoped Context │
        │ BAAI Embeddings     │           │ & Relevance Filter  │
        └──────────┬──────────┘           └──────────┬──────────┘
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │ ChromaDB Index      │◄──────────│ Groq LLM Inference  │
        └─────────────────────┘           └──────────┬──────────┘
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │ Grounded Answer     │
                                          │ & Chat Persistence  │
                                          └──────────┬──────────┘
                                                     │
                                                     ▼
                                          ┌─────────────────────┐
                                          │    User / UI        │
                                          └─────────────────────┘

        Supporting Services:
        ├── PostgreSQL / SQLite: Users, documents, chats, messages
        ├── S3-Compatible Storage: Original PDF files
        ├── SMTP: Email OTP delivery
        └── Groq: LLM inference and model fallback
```

### How It Works

1. **Authentication:** Users register, verify their email using a six-digit OTP, and authenticate using a JWT bearer token.
2. **Document Upload:** PDF files are uploaded to S3-compatible object storage.
3. **Text Extraction:** PyPDF extracts document text in memory.
4. **Chunking:** Extracted text is divided into overlapping chunks of approximately 250 words, with a 30-word overlap.
5. **Embedding Generation:** FastEmbed converts each chunk into a semantic vector using `BAAI/bge-small-en-v1.5`.
6. **Vector Indexing:** ChromaDB stores vectors alongside document and user metadata.
7. **Query Processing:** A user's question is embedded and compared with the relevant document vectors.
8. **Context Filtering:** Retrieved chunks are filtered by relevance and user access.
9. **Answer Generation:** Relevant context and the question are sent to a configured Groq model.
10. **Chat Persistence:** User prompts and assistant responses are saved to the relational database.

---

## 📂 Project Structure

```
IntelliDocs/
├── app/
│   ├── core/
│   │   ├── dependencies.py       # Authentication guards
│   │   ├── email.py              # Async SMTP OTP dispatcher
│   │   └── security.py           # Password hashing and JWT utilities
│   │
│   ├── db/
│   │   ├── models.py             # SQLAlchemy database models
│   │   └── session.py            # Database engine and sessions
│   │
│   ├── routers/
│   │   ├── auth.py               # Registration, OTP, login
│   │   ├── chats.py              # Chat sessions and RAG orchestration
│   │   ├── documents.py          # PDF upload and management
│   │   └── users.py              # User profile management
│   │
│   ├── schemas/
│   │   └── __init__.py           # Pydantic schemas
│   │
│   ├── services/
│   │   ├── llm.py                # Groq integration and model fallback
│   │   ├── rag.py                # Embeddings and vector retrieval
│   │   └── storage.py            # S3-compatible object storage
│   │
│   ├── config.py                 # Environment-based configuration
│   └── main.py                   # FastAPI application entry point
│
│
├── .dockerignore
├── .env                          # Local environment configuration
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation and Local Setup

### 1\. Prerequisites

Ensure the following are available:

- Python 3.10 or later
- Git
- A Groq API key
- SMTP credentials for email verification
- PostgreSQL or SQLite
- An S3-compatible storage account, or a supported local development configuration

External service references:

- [Groq Console](<https://console.groq.com/>)
- [Neon](<https://neon.tech/>)
- [Cloudflare R2](<https://developers.cloudflare.com/r2/>)
- [AWS S3](<https://aws.amazon.com/s3/>)

### 2\. Clone the Repository

```
git clone https://github.com/Drkadam07/IntelliDocs.git
cd IntelliDocs
```

### 3\. Create a Virtual Environment

**Linux / macOS**

```
python -m venv .venv
source .venv/bin/activate
```

**Windows — Command Prompt**

```
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows — PowerShell**

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4\. Install Dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5\. Configure Environment Variables

Create a `.env` file in the project root and configure the following values. Adapt variable names to match those defined in `app/config.py`.

```
# Application
PROJECT_NAME=IntelliDocs
SECRET_KEY=replace-with-a-cryptographically-secure-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database: PostgreSQL
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require

# Alternatively, use SQLite if supported by your configuration
# DATABASE_URL=sqlite:///./intellidocs.db

# S3-Compatible Object Storage
NEON_STORAGE_ENDPOINT=https://YOUR_STORAGE_ENDPOINT
NEON_STORAGE_REGION=us-east-2
NEON_STORAGE_ACCESS_KEY_ID=YOUR_ACCESS_KEY_ID
NEON_STORAGE_SECRET_ACCESS_KEY=YOUR_SECRET_ACCESS_KEY
NEON_STORAGE_BUCKET_NAME=intellidocs

# Groq LLM
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=

# Embedding Model
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Email / SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=YOUR_EMAIL_APP_PASSWORD
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=IntelliDocs Support
```

**Important configuration notes:**

- Replace every placeholder with valid credentials for your environment.
- Use a cryptographically secure secret for `SECRET_KEY`.
- For Gmail, use an App Password when your account configuration supports it.
- Configure the object storage endpoint, region, bucket, and credentials according to your provider.
- Confirm that the configured Groq model is currently available to your API account.
- Ensure the database schema is initialized using the migration or initialization process implemented by the project.
- Never commit `.env` or production credentials to version control.

### 6\. Run the Application

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application should now be accessible at the following local URLs, assuming it starts successfully:

| Resource | URL |
| --- | --- |
| Application | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | [http://localhost:8000/redoc](<http://localhost:8000/redoc>) |
| Health Check | http://localhost:8000/health |

The `/health` endpoint is available if implemented and registered as described in the API reference below.

---

## 🔐 Authentication

IntelliDocs uses JWT bearer authentication for protected endpoints.

### Authentication Flow

1. Register a user using `POST /auth/register`.
2. Retrieve the verification code from the registered email address.
3. Verify the account using `POST /auth/verify-otp`.
4. Save the returned access token.
5. Include the token in subsequent protected API requests.

Example authorization header:

```
Authorization: Bearer YOUR_JWT_ACCESS_TOKEN
```

Tokens should be treated as secrets and must not be exposed in public repositories, logs, or client-side source code.

---

## 🧠 RAG Pipeline Details

### Document Ingestion

PDF files are processed using PyPDF, with extracted text divided into overlapping chunks.

| Setting | Value |
| --- | --- |
| PDF extraction | PyPDF |
| Chunk size | Approximately 250 words |
| Chunk overlap | Approximately 30 words |
| Embedding model | `BAAI/bge-small-en-v1.5` |
| Vector database | ChromaDB |

### Semantic Retrieval

The retrieval service embeds incoming questions and searches for semantically related chunks.

Document metadata can include:

- `user_id` — identifies the document owner.
- `doc_id` — identifies the source document.
- Additional chunk or source metadata as required by the implementation.

User-scoped retrieval helps prevent one user from retrieving another user's document content. Database authorization and vector filtering must both be enforced correctly.

### Grounded Answer Generation

The retrieved context is passed to the configured Groq model along with the user's question and instructions to answer from the available evidence.

A relevance threshold can reject weak matches. This helps reduce unsupported answers, although it does not guarantee perfect factual accuracy.

**Citation note:** If source-accurate citations are required, the application should retain page numbers and source metadata during extraction and chunking, then include those references in the answer-generation and response-formatting steps.

### LLM Fallback

The LLM service can be configured to try alternative supported Groq models when the primary model fails. The fallback list, error handling, retry behavior, and model availability should be verified against the implementation.

---

## 🗄️ Data Storage

IntelliDocs uses separate storage layers for different types of data.

| Storage Layer | Purpose |
| --- | --- |
| PostgreSQL / SQLite | User accounts, document metadata, chat sessions, and messages |
| S3-Compatible Storage | Original PDF files |
| ChromaDB | Semantic vectors and retrieval metadata |
| Application Memory | Temporary PDF extraction and chunk-processing data |

The document metadata, original object, and vector index should be kept consistent during document deletion and re-indexing operations.

---

## 🐳 Docker Deployment

### 1\. Build the Image

```
docker build -t intellidocs:latest .
```

### 2\. Run the Container

```
docker run -d \
  --name intellidocs-api \
  -p 8000:8000 \
  --env-file .env \
  intellidocs:latest
```

### 3\. Inspect Container Logs

```
docker logs -f intellidocs-api
```

### 4\. Stop the Container

```
docker stop intellidocs-api
```

### 5\. Remove the Container

```
docker rm intellidocs-api
```

**Production deployment considerations:**

- Use a production-grade ASGI configuration and disable development reload mode.
- Configure persistent storage for any local ChromaDB data.
- Use managed PostgreSQL and object storage for durable production data.
- Configure HTTPS through a trusted reverse proxy or platform ingress.
- Restrict CORS to trusted frontend origins.
- Apply request-size limits, upload validation, and rate limiting.
- Configure health checks, structured logging, monitoring, and backup policies.
- Run database migrations as part of the deployment process.

---

## 🔒 Security Considerations

IntelliDocs is designed around user-scoped access, but production security depends on the implementation and deployment configuration.

Recommended controls include:

- Hash passwords with Argon2 rather than storing plaintext passwords.
- Use cryptographically secure, expiring OTPs and enforce attempt limits.
- Keep JWT signing keys, API keys, database passwords, and SMTP credentials secret.
- Validate PDF file types, file sizes, and extracted content.
- Enforce ownership checks for every document and chat operation.
- Apply user filtering to every vector retrieval request.
- Use short-lived presigned URLs and avoid logging sensitive query parameters.
- Protect destructive endpoints such as `POST /clear`.
- Use TLS for external service connections.
- Add rate limiting, audit logging, and appropriate error handling.
- Treat retrieved document content as untrusted input when constructing LLM prompts.

---

## 🖼️ Application Preview

Add screenshots or a GIF of the running application here to demonstrate the interface.

Suggested assets:

```
intellidocs-frontend/Assets/
    ├── images/
```

![Project Screenshot](intellidocs-frontend/Assets/img1.png)
![Project Screenshot](intellidocs-frontend/Assets/img2.png)
![Project Screenshot](intellidocs-frontend/Assets/img3.png)
![Project Screenshot](intellidocs-frontend/Assets/img4.png)
![Project Screenshot](intellidocs-frontend/Assets/img7.png)
![Project Screenshot](intellidocs-frontend/Assets/img5.png)
![Project Screenshot](intellidocs-frontend/Assets/img6.png)
---

## 🛣️ Future Enhancements

Potential improvements for future versions include:

- Page-level citations with clickable source references.
- Streaming LLM responses.
- Support for additional document formats.
- Hybrid semantic and keyword retrieval.
- Reranking for more accurate context selection.
- Background ingestion jobs for large PDFs.
- Document-level access controls and sharing.
- Automated tests and continuous integration.
- Usage analytics, observability, and configurable rate limits.

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request describing the changes.

For significant changes, open an issue first to discuss the proposed implementation.

---

## 📜 License

This project is distributed under the **MIT License**.

If the repository does not already contain a `LICENSE` file, add the MIT license text before distributing the project under that license.

---

## 👨‍💻 Author

**Dhanraj Kadam**

Computer Engineering Graduate | Python Developer | AI/ML Engineer

- GitHub: [@Drkadam07](<https://github.com/Drkadam07>)
- Repository: IntelliDocs

---
