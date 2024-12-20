import time
from pymilvus import MilvusClient, model
from pymilvus.milvus_client import IndexParams
from loguru import logger

class RAGService:
    def __init__(self, uri=None, token=None, collection_name="rag_collection"):
        """
        Initialize Milvus client with support for both local and server modes.
        """
        logger.info(f"Initializing RAG service with collection: {collection_name}")
        if uri and token:
            logger.info("Connecting to remote Milvus server")
            self.client = MilvusClient(uri=uri, token=token)
        else:
            logger.info("Using local Milvus database")
            self.client = MilvusClient("milvus_demo.db")
        
        self.collection_name = collection_name
        self.dimension = 768  # Model output dimension

        # Create or reset the collection
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
            
        # Create collection with proper schema
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            primary_field_name="id",
            vector_field_name="vector",
            scalar_fields=[
                {"name": "text", "type": "varchar", "max_length": 4096},
                {"name": "metadata", "type": "json"},
            ]
        )

        # Create index for vector field
        self._create_index()

        # Set up embedding function
        self.embedding_fn = model.DefaultEmbeddingFunction()
        logger.info("RAG service initialized successfully")

    def _create_index(self):
        """
        Create an index for the vector field in the collection.
        """
        logger.info("Creating index for vector field")
        try:
            # index_params = self.client.prepare_index_params()
            # index_params.add_index(
            #     field_name="vector",
            #     index_type="IVF_FLAT",
            #     metric_type="COSINE",
            #     index_name="vector_index",
            #     params={"nlist": 1024}
            # )
            # self.client.create_index(
            #     collection_name=self.collection_name,
            #     index_params=index_params
            # )
            logger.success("Index created successfully")
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise

    def add_documents(self, documents, metadata_list=None):
        """
        Add documents with optional metadata to the collection.
        """
        logger.info(f"Adding {len(documents)} documents to collection")
        try:
            vectors = self.embedding_fn.encode_documents(documents)
            if metadata_list is None:
                metadata_list = [{} for _ in documents]
                
            data = [
                { 
                    # the id will be a big number - the current nano-second timestamp
                    "id": int(time.time_ns()),
                    "vector": vectors[i],
                    "text": documents[i],
                    "metadata": metadata_list[i]
                } for i in range(len(vectors))
            ]
            
            self.client.insert(collection_name=self.collection_name, data=data)
            logger.success(f"Successfully added {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def search(self, query, filter=None, top_k=3):
        """
        Perform semantic search with optional filtering.
        """
        logger.info(f"Searching for: {query[:50]}... (top_k={top_k})")
        try:
            query_vector = self.embedding_fn.encode_queries([query])
            search_params = {
                "collection_name": self.collection_name,
                "data": query_vector,
                "limit": top_k,
                "output_fields": ["text", "metadata"],
            }
            if filter:
                search_params["filter"] = filter
                
            results = self.client.search(**search_params)
            
            logger.success(f"Search completed, found {len(results[0])} results")
            return [
                {
                    "id": item["id"],
                    "score": item["distance"],
                    "text": item["entity"].get("text"),
                    "metadata": item["entity"].get("metadata")
                }
                for item in results[0]
            ]
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise

    def get_all_documents(self, limit=100):
        """
        Retrieve a limited number of documents from the collection.
        
        :param limit: The maximum number of documents to retrieve (default is 100).
        """
        logger.info(f"Retrieving up to {limit} documents from the collection: {self.collection_name}")
        try:
            # Query the collection with an empty filter and specified limit
            res = self.client.query(
                collection_name=self.collection_name,
                filter="",  # Empty filter to retrieve all documents
                output_fields=["id", "text", "metadata", "vector"],
                limit=limit
            )
            
            logger.success(f"Successfully retrieved {len(res)} documents from the collection")
            return res
        except Exception as e:
            logger.error(f"Error retrieving documents from collection: {str(e)}")
            raise



    def delete_document(self, doc_id):
        """
        Delete a document from the collection by ID.
        """
        logger.info(f"Deleting document with ID: {doc_id}")
        try:
            # Create the boolean expression for deletion
            expr = f"id in [{doc_id}]"
            
            # Perform the delete operation
            collection = self.client.get_collection(self.collection_name)
            collection.delete(expr)
            
            logger.success(f"Document with ID {doc_id} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting document with ID {doc_id}: {str(e)}")
            raise


    def delete_all(self):
        """
        Drop the collection and clean up.
        """
        logger.warning(f"Deleting collection: {self.collection_name}")
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")