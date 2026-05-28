from typing import List
import os

from fastembed import TextEmbedding
from fastembed import ImageEmbedding
from qdrant_client import QdrantClient

class embeddings:
    def __init__(self, dbPath : str = "./qdrant_db") -> None:
        self.client = QdrantClient(path=dbPath)
        self.txtEmbeddings = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.imgEmbeddings = ImageEmbedding(model_name="Qdrant/clip-ViT-B-32-vision")

    def generate_text_embedding(self, file_content: str):
        """Generates a text embedding for a single file's content."""
        embedding = list(self.txtEmbeddings.embed(documents=[file_content]))[0]
        return embedding

    def generate_image_embedding(self, image_path: str):
        """Generates an image embedding for a single image file."""
        embedding = list(self.imgEmbeddings.embed(images=[image_path]))[0]
        return embedding
