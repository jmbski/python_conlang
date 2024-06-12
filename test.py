from langchain_community.llms import _import_ollama
from langchain_community.document_loaders import JSONLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


""" ollama = _import_ollama()
silverlight = './data/silverlight.txt'
text_loader = TextLoader(silverlight)
data = text_loader.load()
oembed = OllamaEmbeddings(base_url="http://localhost:6000", model="llama3")
vectorstore = Chroma.from_documents(documents=data, embedding=oembed)

question = 'How many moons does Silverlight have?'

qachain = create_retrieval_chain(vectorstore.as_retriever(), ollama )
qachain.invoke({"query": question}) """

