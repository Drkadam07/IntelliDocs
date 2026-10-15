# IntelliDocs — AI-Powered PDF Q&A Assistant

An AI-powered PDF question-answering assistant that allows users to interact with documents using natural language. Built with **Retrieval-Augmented Generation (RAG)**, IntelliDocs retrieves relevant information from uploaded PDFs and uses a Large Language Model (LLM) to generate context-grounded answers.

Instead of manually searching through lengthy documents, users can upload a PDF, ask questions, and receive answers based on the document's content.

## 🚀 Features

- **PDF Upload:** Upload PDF documents and extract text using PyPDF.
- **Natural Language Q&A:** Ask questions about document content using everyday language.
- **Retrieval-Augmented Generation (RAG):** Combine semantic retrieval with LLM-based answer generation.
- **Semantic Search:** Retrieve relevant document passages using vector embeddings.
- **Vector Database:** Store and search document embeddings using ChromaDB.
- **Context Relevance Filtering:** Filter weak retrieval results using a configurable distance threshold.
- **Grounded Answers:** Instruct the LLM to answer only using the retrieved document context.
- **Fast Inference:** Generate responses using the Groq API.
- **Persistent Chat History:** Store conversations in SQLite.
- **Interactive Web Interface:** Access document Q&A through a browser-based interface.
- **Modular Architecture:** Separate document retrieval, LLM integration, API routes, and database operations.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| LLM Integration | Groq API |
| Embedding Model | FastEmbed — BAAI/bge-small-en-v1.5 |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| Chat History | SQLite |
| Templating Engine | Jinja2 |
| Architecture | Retrieval-Augmented Generation (RAG) |

## 🧠 How It Works

IntelliDocs follows a document-grounded RAG pipeline.

1. **Upload:** The user uploads a PDF, and the application extracts its text using PyPDF.
2. **Chunk:** The extracted text is split into smaller, overlapping chunks to preserve context and improve retrieval.
3. **Embed:** FastEmbed converts each chunk into a numerical vector using the BAAI/bge-small-en-v1.5 model.
4. **Store:** The embeddings and corresponding text chunks are indexed in ChromaDB.
5. **Ask:** The user's question is converted into a vector using the same embedding model.
6. **Retrieve:** ChromaDB searches for document chunks that are semantically similar to the question.
7. **Filter:** A relevance-distance threshold helps reject weakly matching results.
8. **Generate:** Relevant passages are passed to the Groq-hosted LLM with instructions to answer using only the supplied context.
9. **Respond:** The generated answer is displayed in the web interface. If sufficient context is unavailable, the application is designed to avoid unsupported answers.
10. **Persist:** Conversation history is stored in SQLite for future access.

<!-- ## 📂 Project Structure

```text
IntelliDocs/
├── app/
│   
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignored files
└── README.md            # Project documentation
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- pip package manager
- A Groq API key

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd IntelliDocs
```

Replace `<your-repository-url>` with your actual GitHub repository URL.

### 2. Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Obtain your API key from the [Groq Console](https://console.groq.com/).

Ensure your application loads environment variables and that `.env` is included in `.gitignore`. Never commit API keys or other secrets to GitHub.

### 5. Run the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Open the application in your browser:

```text
http://127.0.0.1:8000
```

The command assumes your FastAPI instance is named `app` inside `app/main.py` and that the application serves the web interface at `/`. Adjust it if your implementation uses a different entry point. -->

## 💡 Usage

1. Start the IntelliDocs application.
2. Open the application in your web browser.
3. Upload a PDF document.
4. Wait for the document text to be processed and indexed.
5. Enter a question about the uploaded document.
6. Review the answer generated from the retrieved document context.
7. Continue asking follow-up questions and use the stored conversation history if supported by your implementation.

**Example questions:**

- What is the main objective of this document?
- Summarize the key findings.
- Explain the methodology described in the PDF.
- What are the major challenges discussed?
- List the important conclusions.
- Does the document mention any limitations?

## 🔍 Key Technical Concepts

### Retrieval-Augmented Generation (RAG)

RAG combines information retrieval with language generation. Instead of relying solely on the LLM's pretrained knowledge, IntelliDocs retrieves relevant passages from the uploaded document and supplies them as context for answering questions.

### Semantic Embeddings

The BAAI/bge-small-en-v1.5 model converts text into numerical vector representations. These vectors enable semantic similarity searches, helping the application find relevant passages even when the question and document use different wording.

### ChromaDB

ChromaDB stores document embeddings and supports similarity-based retrieval. It serves as the vector search layer in the document question-answering pipeline.

### Relevance Filtering

A configurable distance threshold helps the application reject weakly matching retrieval results. This reduces the likelihood of generating answers from irrelevant passages, although the threshold must be tuned and evaluated for the chosen distance metric.

### Groq API

The Groq API provides access to a hosted language model for generating responses from retrieved document context.

### SQLite

SQLite provides lightweight relational storage for conversation history and associated application data.

## 🔐 Reliability and Security Considerations

- Answers are designed to be grounded in retrieved document content.
- Prompt instructions alone cannot guarantee hallucination-free responses.
- Retrieval thresholds should be evaluated against relevant and irrelevant questions.
- API keys should be stored in environment variables, not source code.
- Uploaded documents should be validated and handled securely.
- Document access controls and data retention policies should be considered before production deployment.

## 🔮 Future Enhancements

- Multi-PDF upload and cross-document question answering.
- Source citations with page numbers and supporting excerpts.
- Hybrid search combining semantic retrieval and keyword matching.
- Streaming LLM responses.
- Improved document management and re-indexing.
- User authentication and document-level permissions.
- Evaluation metrics for retrieval quality and answer faithfulness.
- Docker-based deployment and cloud hosting.

## 🎯 Learning Outcomes

This project demonstrates practical experience with:

- Python backend development using FastAPI.
- Building a Retrieval-Augmented Generation pipeline.
- Text extraction, preprocessing, and chunking.
- Semantic embeddings and vector similarity search.
- Integrating hosted LLM APIs.
- Designing context-grounded question-answering workflows.
- Persisting application data with SQLite.
- Developing a browser-based application using HTML, CSS, and JavaScript.

## 📜 License

This project is available under the MIT License if you choose to distribute it under those terms. Add a `LICENSE` file to the repository before describing it as officially licensed under MIT.

## 👨‍💻 Author

**Dhanraj Kadam**

Computer Engineering Graduate | Python Developer | AI/ML Engineer

- GitHub: [Drkadam07](https://github.com/Drkadam07)

---

*IntelliDocs — Making document understanding more interactive, accessible, and efficient with AI.*