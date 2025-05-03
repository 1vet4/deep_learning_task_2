from environment.database import MongoDatabase
from environment.config import CONFIG
from llama_index.core import Settings, Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from pymongo.operations import SearchIndexModel
import pymongo
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from datetime import datetime


class VectorIndex():
    def __init__(self):
        self.config = CONFIG
        self.embedding_model = self.config['EMBEDDING_MODEL']
        self.database = MongoDatabase(self.config)
        self.vector_index_name = self.config['VECTOR_INDEX_NAME']

    def setup_llm_and_embeddings(self):
        try:
            embed_model = HuggingFaceEmbedding(model_name=self.embedding_model)

            Settings.embed_model = embed_model
            Settings.node_parser = SentenceSplitter()

        except Exception as e:
            print(f"Error during LLM and embedding setup: {e}")

    def create_vector_store_and_storage_context(self):
        vector_store = MongoDBAtlasVectorSearch(
            self.database.client,
            db_name=self.database.db_name,
            collection_name=self.database.vector_index_collection_name,
            embedding_key="embedding",
            text_key="text"
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        return storage_context

    def embed_documents_in_vector_store(self, documents, storage_context):
        try:
            if not documents:
                print("No documents to index.")
                return None
            print('Embedding documents...')
            vector_index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                settings=Settings
            )
            print('Embedding done.')
            return vector_index
        except Exception as e:
            print(f"Error indexing documents: {e}")
            return None

    def create_search_index(self):
        try:
            search_index_model = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": 768,
                            "similarity": "cosine"
                        }
                    ]
                },
                name=self.vector_index_name,
                type="vectorSearch"
            )

            result = self.database.vector_index_collection.create_search_index(model=search_index_model)
            print(f"Search index created: {result}")
        except Exception as e:
            print(f"Error creating search index: {e}")

    def fetch_documents_from_collection(self):
        try:
            documents_cursor = self.database.document_collection.find()
            documents = []
            for doc in documents_cursor:
                article = doc.get("article", "")
                headline = doc.get("headline", "")
                category = doc.get("category", "")
                publication_date = doc.get("publication_date", "")
                metadata = {
                    'headline': headline,
                    'category': category,
                    'publication_date': publication_date
                }
                documents.append(Document(text=article, metadata=metadata))
            if not documents:
                print(f"No documents found in collection: {self.database.document_collection_name}")
            print(f'Documents from {self.database.document_collection_name} read successfully.')
            return documents

        except pymongo.errors.PyMongoError as e:
            print(f"MongoDB error while fetching documents: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while fetching documents: {e}")
            return []

    def read_and_save_additional_document_to_database(self, file_path):
        try:
            documents = []

            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                text = file.read()

                if not text:
                    print(f"The file at {file_path} is empty.")
                    return False

                metadata = {
                    "headline": "Papildomas failas",
                    "category": "Nežinoma",
                    "publication_date": datetime.now().strftime("%Y.%m.%d %H:%M"),
                }

                documents.append(Document(text=text, metadata=metadata))

                self.database.insert_additional_document_entry(metadata, text)

                print("Document read successfully.")

            return documents

        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return []

    def add_additional_document_to_vector_index(self, file_path):
        try:
            self.setup_llm_and_embeddings()
            documents = self.read_and_save_additional_document_to_database(file_path)
            storage_context = self.create_vector_store_and_storage_context()

            self.embed_documents_in_vector_store(documents, storage_context)

            return True
        except Exception as e:
            print(f"Error while adding document to vector index: {str(e)}")
            return False

    def initialize_vector_indexing(self):
        try:
            documents = self.fetch_documents_from_collection()

            if not documents:
                print("No documents found.")
                return None

            self.setup_llm_and_embeddings()

            storage_context = self.create_vector_store_and_storage_context()
            if not storage_context:
                return None

            vector_index = self.embed_documents_in_vector_store(documents, storage_context)
            if vector_index:
                self.create_search_index()
                print('Vector store and search index created successfully.')
            else:
                print('Error while embedding the documents.')

        except Exception as e:
            print(f"Error creating vector index storage: {e}")
            return None

