from pinecone import Pinecone, ServerlessSpec
import os
from sentence_transformers import SentenceTransformer
import uuid
from dotenv import load_dotenv
from objects import *

load_dotenv('_.env')

class PineconeController:
    def __init__(self):
        self._pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self._index_name = "books-index"
        self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        if self._index_name not in self._pc.list_indexes().names():
            self._pc.create_index(
                name=self._index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        self._index = self._pc.Index(self._index_name)

    def _chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 40) -> list:
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            chunk = words[i:i + chunk_size]
            chunks.append(" ".join(chunk))
            i += chunk_size - overlap

        return chunks

    def _get_embedding(self, text: str):
        embedding = self._embedding_model.encode(text)
        return embedding.tolist()

    def add_book(self, book_text: str, book_name: str, author_name: str):

        chunks = self._chunk_text(book_text)

        vectors = []

        for chunk in chunks:
            embedding = self._get_embedding(chunk)

            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "book": book_name,
                    "author": author_name
                }
            })

        self._index.upsert(vectors)

    def search_similar_chunks(self, question: str, top_k: int = 3, book_name: str = None, author_name: str = None) -> \
            list[Chunk]:
        """
        Ищет топ-K наиболее похожих chunk'ов на вопрос.
        Можно ограничить поиск конкретной книгой или автором.

        :param question: строка вопроса
        :param top_k: сколько топ совпадений вернуть
        :param book_name: (опционально) искать только в книге с этим названием
        :param author_name: (опционально) искать только у указанного автора
        """
        query_vector = self._get_embedding(question)

        # Формируем фильтр
        filter_dict = {}
        if book_name:
            filter_dict["book"] = book_name
        if author_name:
            filter_dict["author"] = author_name

        search_results = self._index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )

        result = []

        for match in search_results["matches"]:
            result.append(Chunk(
                author=match["metadata"].get("author", "Автор не указан"),
                book=match["metadata"]["book"],
                text=match["metadata"]["text"]
            ))

        return result

    def list_all_books(self) -> dict[str, list[str]]:
        """
        Выводит список всех книг, которые есть в индексе Pinecone.
        """
        # Получаем все векторы (по ID)
        all_ids = []
        for batch in self._index.list():
            all_ids.extend(batch)

        # Получаем данные по ID
        vectors = self._index.fetch(ids=all_ids)

        result: dict[str, list[str]] = {}  # {"Автор": ["Названия", "книг"]}

        for vid, data in vectors["vectors"].items():
            book_author = data["metadata"].get("author")
            if book_author not in result.keys():
                result[book_author] = [data["metadata"].get("book")]
            else:
                book_title = data["metadata"].get("book")
                if book_title not in result[book_author]:
                    result[book_author].append(book_title)

        return result

    def get_amount_of_books(self) -> int:
        all_ids = []
        for batch in self._index.list():
            all_ids.extend(batch)

        vectors = self._index.fetch(ids=all_ids)

        # Извлекаем уникальные книги
        books = set()
        for vid, data in vectors["vectors"].items():
            book_name = data["metadata"].get("book")
            if book_name:
                books.add(book_name)
        return len(books)
