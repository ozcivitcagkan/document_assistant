# Document Assistant

A small RAG application that lets you ask questions about your own PDF, TXT, and DOCX files.

## Tech Stack

- Python
- Voyage AI
- ChromaDB
- Anthropic Claude

## How It Works

The app reads documents, splits them into smaller chunks, creates embeddings, stores them in ChromaDB, and retrieves relevant content for each question.

Claude then uses the retrieved content to generate the answer.

## Project Structure

```text
document_assistant/
├── documents/
├── dosya_okuma.py
├── rag_motoru.py
├── main.py
├── requirements.txt
├── README.md
└── README_TR.md
```

## Setup

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file and add your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

## Usage

Put your PDF, TXT, or DOCX files into the `documents` folder.

Then run:

```bash
python main.py
```

You can ask questions about your documents directly from the terminal.

Example:

```text
Question: How many annual leave days do employees receive?

Answer: Employees receive 14 days of annual leave per year.
```

The application also shows which document and chunk were used for the answer.

## Notes

The project checks which documents have already been added to ChromaDB, so they are not embedded again every time the program starts.

This is a learning and portfolio project. The current version uses a simple command-line interface and does not include a web upload page or conversation memory.

## Next Steps

- Web interface
- File upload
- Conversation memory
- Document update and delete
- AI agents and tool calling
