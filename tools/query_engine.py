from environment.database import MongoDatabase
from environment.config import CONFIG
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from huggingface_hub import login
import torch
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.llms.openai import OpenAI


class QueryEngine:
    def __init__(self):
        self.config = CONFIG
        self.database = MongoDatabase(self.config)
        self.query_engine = None
        self.embedding_model = self.config['EMBEDDING_MODEL']
        self.vector_index = None
        self.vector_store = None
        self.llm_model = self.config['LLM_MODEL']
        self.api_key = self.config['API_KEY']

        self._initialize()

    def _initialize(self):
        self._initialize_models()
        self._initialize_vector_store()

    def _initialize_models(self):
        openai_key = self.api_key
        llm = OpenAI(
            model="gpt-4.1-nano",
            api_key=openai_key,
            system_prompt=self.config['SYSTEM_PROMPT']
        )
        embed_model = HuggingFaceEmbedding(model_name=self.embedding_model)

        Settings.llm = llm
        Settings.embed_model = embed_model

    def _initialize_vector_store(self):
        self.vector_store = MongoDBAtlasVectorSearch(
            self.database.client,
            db_name=self.database.db_name,
            collection_name=self.database.vector_index_collection_name,
            vector_index_name=self.config['VECTOR_INDEX_NAME'],
            embedding_key="embedding",
            text_key="text"
        )
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        return storage_context

    def get_query_engine(self):
        self.vector_index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            settings=Settings
        )
        self.query_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=self.vector_index.as_retriever(similarity_top_k=3),
            use_system_prompt=True,
            llm=Settings.llm
        )

        return self.query_engine
