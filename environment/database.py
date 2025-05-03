import pymongo
from .config import CONFIG


class MongoDatabase:
    def __init__(self, config: CONFIG):
        self.config = config
        self.client = self._connect()
        self.db_name = self.config['MONGO_DB_NAME']
        self.db = self.client[self.config['MONGO_DB_NAME']]
        self.document_collection_name = self.config['DOCUMENTS_COLLECTION_NAME']
        self.vector_index_collection_name = self.config['VECTOR_INDEX_COLLECTION_NAME']
        self.document_collection = self.db[self.config['DOCUMENTS_COLLECTION_NAME']]
        self.additional_document_collection = self.db[self.config['ADDITIONAL_DOCUMENTS_COLLECTION_NAME']]
        self.vector_index_collection = self.db[self.config['VECTOR_INDEX_COLLECTION_NAME']]

    def _connect(self):
        try:
            client = pymongo.MongoClient(self.config['MONGO_DB_URI'])
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            raise e

    def insert_document_entry(self, metadata: dict, article: str):
        entry = {
            **metadata,
            "article": article
        }
        try:
            self.document_collection.insert_one(entry)
            print('Article inserted successfully')
        except pymongo.errors.DuplicateKeyError:
            print("Duplicate entry detected. Skipping insertion.")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred while inserting the article: {e}")

    def insert_additional_document_entry(self, metadata, text):
        try:
            entry = {
                **metadata,
                "text": text
            }
            self.additional_document_collection.insert_one(entry)
            print('Document inserted successfully')
        except pymongo.errors.DuplicateKeyError:
            print("Duplicate entry detected. Skipping insertion.")
        except pymongo.errors.PyMongoError as e:
            print(f"An error occurred while inserting the article: {e}")