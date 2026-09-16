import os
from rag_motoru import load_new_documents, ask_rag, collection


def start_document_assistant():
    print("Documents are loading...")
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    DOCUMENTS_PATH = os.path.join(PROJECT_DIR, "documents")

    load_new_documents(DOCUMENTS_PATH)

    if collection.count() == 0:
        print("⚠️ No documents are available. Please add a document and run the program again.")
        return

    print("\nDocument Assistant is ready. (type 'q' to exit)\n")

    while True:
        query = input("Question: ").strip()

        if not query:
            continue

        if query.lower() in ["q", "quit", "exit"]:
            print("Goodbye!")
            break

        try:
            answer, sources = ask_rag(query, top_k=3)

            print(f"\nAnswer: {answer}")

            print("\nSources:")
            for source in sources:
                print(
                    f"  - {source['source']} "
                    f"(chunk {source['chunk_number']})"
                )

            print()

        except Exception as error:
            print(f"⚠️ An error occurred: {error}\n")


if __name__ == "__main__":
    start_document_assistant()
