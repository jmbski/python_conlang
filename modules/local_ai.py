import ollama
from langchain_community.llms import Ollama
#from langchain.document_loaders import WebBaseLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def send_chat(message: str):
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': message}],
        stream=True
    )

    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        
def llama_test():
    """ silver_light = ollama.embeddings('llama3', 'Silverlight is the name of a planet in a D&D campaign setting I am working on. Silverlight is a planet with rings like Saturn. These rings are made of crytal, silver, and other shiny metals. Silver on the surface though is actually rarer than gold, and thus gold pieces and silver pieces are swapped in value. The local star is a white dwarf, which affects many things about the planet. Silverlight also has no moons orbiting it.')
    #open('./data/embeddings', 'w').write(silver_light)
    print(silver_light.keys()) """
    ollama = Ollama(
        base_url='http://localhost:6000',
        model="llama3"
    )
    loader = WebBaseLoader("https://www.gutenberg.org/files/1727/1727-h/1727-h.htm")
    data = loader.load()
    

def test_question():
    
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
        stream=True,
    )

    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)