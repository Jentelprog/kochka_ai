import chromadb  # type: ignore
import pypdf  # type: ignore
from langchain_community.document_loaders import PyPDFDirectoryLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore

chroma_client = chromadb.PersistentClient(
    path=r"C:\Users\yassi\Downloads\ieee ai\content\chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="tutorial", metadata={"hnsw:space": "cosine"}
)

loader = PyPDFDirectoryLoader(r"C:\Users\yassi\Downloads\ieee ai\content\data")

raw_documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)


chunks = text_splitter.split_documents(raw_documents)

documents = []
metadata = []
ids = []

i = 0

for chunk in chunks:
    documents.append(chunk.page_content)
    ids.append("ID" + str(i))
    metadata.append(chunk.metadata)

    i += 1

collection.upsert(documents=documents, metadatas=metadata, ids=ids)

# change this part so you have your api key here
with open(r"C:\Users\ilyes\OneDrive\Desktop\api.txt", "r") as f:
    api_key = f.readlines()[0]


class LLMManager:
    def _init_(self) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
        )

    def invoke(self, prompt, **kwargs) -> str:
        return self.llm.invoke(prompt).content


llm = LLMManager()

while True:

    querry = input("query: ")

    results = collection.query(query_texts=[querry], n_results=3)

    print(results["documents"])

    system_prompt = (
        """
    You are a mascot of the IEEE ISI student branch. You answer questions on this sb and talk about it to promote it.
    But you only answer based on knowledge I'm providing you. You don't use your internal
    knowledge and you don't make thins up.
    If you don't know the answer, just say: I don't know
    --------------------
    The data:
    """
        + str(results["documents"])
        + """
    --------------------
    the question : """
        + str(querry)
        + """
    """
    )

    response = llm.invoke(system_prompt)
    print("----------------------")
    print(response)
