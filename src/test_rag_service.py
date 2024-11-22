import unittest
from rag import RAGService

class TestRAGService(unittest.TestCase):
    def setUp(self):
        self.rag_service = RAGService()

    def tearDown(self):
        self.rag_service.delete_all()

    def test_add_and_search_documents(self):
        documents = [
            "Artificial intelligence was founded as an academic discipline in 1956.",
            "Alan Turing was the first person to conduct substantial research in AI.",
            "Born in Maida Vale, London, Turing was raised in southern England.",
        ]
        self.rag_service.add_documents(documents)

        query = "Who is Alan Turing?"
        results = self.rag_service.search(query)
        self.assertGreater(len(results), 0)
        self.assertIn("Alan Turing", results[0]['text'])

if __name__ == "__main__":
    unittest.main()
