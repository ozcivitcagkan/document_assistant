import os
import voyageai
import chromadb
import anthropic
import glob
from dotenv import load_dotenv

from dosya_okuma import read_document


load_dotenv()

MODEL = "claude-haiku-4-5"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PATH = os.path.join(
    PROJECT_DIR,
    "chroma_db"
)

database_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = database_client.get_or_create_collection(name="documents")

voyage_client = voyageai.Client()
anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def create_paragraph_chunks(text, max_size=500):
    """Group paragraphs into chunks up to the target character size."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if not paragraph.strip():
            continue

        if len(current_chunk) + len(paragraph) <= max_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def create_document_embeddings(texts):
    """Create embeddings for document chunks."""
    result = voyage_client.embed(
        texts,
        model="voyage-4",
        input_type="document"
    )
    return result.embeddings


def create_query_embedding(query):
    """Create an embedding for a user query."""
    result = voyage_client.embed(
        [query],
        model="voyage-4",
        input_type="query"
    )
    return result.embeddings[0]


def add_document_to_collection(file_path):
    """Read, chunk, embed and store one document in Chroma."""
    text = read_document(file_path)
    chunks = create_paragraph_chunks(text)

    if not chunks:
        print(f"No text found: {file_path}")
        return 0

    embeddings = create_document_embeddings(chunks)

    file_name = os.path.basename(file_path)

    ids = [
        f"{file_name}_{index}"
        for index in range(len(chunks))
    ]

    metadata = [
        {
            "source": file_name,
            "chunk_number": index
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadata
    )

    return len(chunks)


def find_relevant_chunks(query, top_k=3):
    """Retrieve the most relevant document chunks for a query."""
    query_embedding = create_query_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    relevant_chunks = []

    for index, document in enumerate(results["documents"][0]):
        relevant_chunks.append({
            "text": document,
            "source": results["metadatas"][0][index]["source"],
            "chunk_number": results["metadatas"][0][index]["chunk_number"]
        })

    return relevant_chunks


def build_rag_prompt(query, chunks):
    """Build a grounded prompt using retrieved document chunks."""
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    sources = "\n".join(
        f"- {chunk['source']} / chunk {chunk['chunk_number']}"
        for chunk in chunks
    )

    prompt = f"""Use the following context to answer the question.

Only use information from the context.
If the answer is not in the context, say "I don't have that information."
Do not make up information.
If the user has an incorrect assumption, correct it using the information in the context.

Context:
{context}

Question:
{query}

Sources:
{sources}

Answer:
"""

    return prompt


def ask_rag(query, top_k=3):
    """Retrieve relevant chunks and generate an answer with Claude."""
    relevant_chunks = find_relevant_chunks(query, top_k=top_k)
    prompt = build_rag_prompt(query, relevant_chunks)

    message = anthropic_client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = message.content[0].text

    return answer, relevant_chunks


def load_new_documents(folder_path):
    """Load only documents that are not already stored in Chroma."""
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        os.makedirs(folder_path)
        print(
            f"Created an empty '{folder_path}' folder. "
            "Add your documents and run the program again."
        )
        return 0

    file_paths = []

    for extension in ["*.txt", "*.pdf", "*.docx"]:
        file_paths.extend(
        glob.glob(os.path.join(folder_path, extension))
    )

    existing_sources = set()

    if collection.count() > 0:
        stored_data = collection.get()

        for metadata in stored_data["metadatas"]:
            existing_sources.add(metadata["source"])

    new_file_count = 0
    new_chunk_count = 0

    for file_path in file_paths:
        file_name = os.path.basename(file_path)

        if file_name in existing_sources:
            continue

        chunk_count = add_document_to_collection(file_path)

        if chunk_count > 0:
            new_file_count += 1
            new_chunk_count += chunk_count

    print(
        f"✅ {new_file_count} new document(s) loaded. "
        f"Total chunks: {collection.count()}"
    )

    return new_chunk_count
