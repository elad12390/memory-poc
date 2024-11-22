from pymilvus import MilvusClient, model

class RAGService:
    def __init__(self, db_file="milvus_demo.db", collection_name="rag_collection"):
        """
        Initialize Milvus and create a collection for storing embeddings.
        """
        self.client = MilvusClient(db_file)
        self.collection_name = collection_name

        # Create or reset the collection
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=768,  # Model output dimension
        )

        # Set up embedding function
        self.embedding_fn = model.DefaultEmbeddingFunction()

    def add_documents(self, documents):
        """
        Add documents to the collection by creating embeddings.
        """
        vectors = self.embedding_fn.encode_documents(documents)
        data = [{"id": i, "vector": vectors[i], "text": documents[i]} for i in range(len(vectors))]
        self.client.insert(collection_name=self.collection_name, data=data)
        print(f"Added {len(documents)} documents to the collection.")

    def search(self, query, top_k=3):
        """
        Perform semantic search for a query and return the top results.
        """
        query_vector = self.embedding_fn.encode_queries([query])
        results = self.client.search(
            collection_name=self.collection_name,
            data=query_vector,
            limit=top_k,
            output_fields=["text"],
        )
        return [
            {
                "id": item.id,
                "score": item.distance,
                "text": item.entity.get("text"),
            }
            for item in results[0]
        ]

    def delete_all(self):
        """
        Drop the collection to delete all stored data.
        """
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
