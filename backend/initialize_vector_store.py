from langchain_community.document_loaders import PyMuPDFLoader
import os

def load_pdfs(pdf_paths):
    documents = []
    for path in pdf_paths:
        loader = PyMuPDFLoader(path)
        docs = loader.load()
        documents.extend(docs)
    return documents

pdf_paths = []
for file in os.listdir("pdfs"):
    if file.endswith(".pdf"):
        pdf_paths.append("pdfs/" + file)

print(f"PDF files found: {len(pdf_paths)}")

documents = load_pdfs(pdf_paths)
print(f"Number of documents loaded: {len(documents)}")

from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_docs = []
    for doc in documents:
        splits = text_splitter.split_documents([doc])
        split_docs.extend(splits)
    return split_docs

split_docs = split_documents(documents)
print(f"Number of chunks: {len(split_docs)}")

# Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Vector Store
from langchain_postgres import PGVector
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="vector_store",
    connection=os.getenv("DATABASE_URL")
)

from langchain_core.documents import Document
for doc in split_docs:
    print("Processing document", doc.metadata["source"], "page", doc.metadata["page"])
    vector_store.add_documents([Document(page_content=doc.page_content, metadata=doc.metadata)])

print("Documents added to vector store.")