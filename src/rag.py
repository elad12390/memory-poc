from pymilvus import MilvusClient, model
import os

class RAGService:
    def __init__(self, uri=None, token=None, collection_name="rag_collection"):
        """
        Initialize Milvus client with support for both local and server modes.
        """
        if uri and token:
            self.client = MilvusClient(uri=uri, token=token)
        else:
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
        self.client.create_index(
            collection_name=self.collection_name,
            field_name="vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 1024},
        )

        # Set up embedding function
        self.embedding_fn = model.DefaultEmbeddingFunction()

    def add_documents(self, documents, metadata_list=None):
        """
        Add documents with optional metadata to the collection.
        """
        vectors = self.embedding_fn.encode_documents(documents)
        if metadata_list is None:
            metadata_list = [{} for _ in documents]
            
        data = [
            {
                "id": i,
                "vector": vectors[i],
                "text": documents[i],
                "metadata": metadata_list[i]
            } for i in range(len(vectors))
        ]
        
        self.client.insert(collection_name=self.collection_name, data=data)
        print(f"Added {len(documents)} documents to the collection.")

    def search(self, query, filter=None, top_k=3):
        """
        Perform semantic search with optional filtering.
        """
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
        
        return [
            {
                "id": item.id,
                "score": item.distance,
                "text": item.entity.get("text"),
                "metadata": item.entity.get("metadata")
            }
            for item in results[0]
        ]

    def delete_all(self):
        """
        Drop the collection and clean up.
        """
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")


# Example Usage
if __name__ == "__main__":
    # Initialize RAG service
    rag_service = RAGService()

    # Add documents
    documents = [
        "Artificial intelligence was founded as an academic discipline in 1956.",
        "Alan Turing was the first person to conduct substantial research in AI.",
        "Born in Maida Vale, London, Turing was raised in southern England.",
    ]
    rag_service.add_documents(documents)

    # Perform a semantic search
    query = "Who is Alan Turing?"
    results = rag_service.search(query)
    print("Search Results:")
    for result in results:
        print(f"ID: {result['id']}, Score: {result['score']:.2f}, Text: {result['text']}")

    # Delete all data
    rag_service.delete_all()
