from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Step 1 - Load the document
print("Loading document...")
loader = TextLoader("company_policy.txt")
documents = loader.load()

# Step 2 - Split into chunks
print("Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# Step 3 - Create vector store
print("Creating vector store...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever()

# Step 4 - Connect to Ollama
print("Connecting to Ollama...")
llm = Ollama(model="llama3.2:1b")

# Step 5 - Basic prompt template (no hardening)
prompt = ChatPromptTemplate.from_template("""
Answer the question based on the following context:
{context}

Question: {question}
""")

# Step 6 - Build the RAG chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Step 7 - Ask questions
print("\nRAG system ready! Ask questions about the company policy.")
print("Type 'quit' to exit\n")

while True:
    question = input("Your question: ")
    if question.lower() == "quit":
        break
    answer = rag_chain.invoke(question)
    print(f"\nAnswer: {answer}\n")