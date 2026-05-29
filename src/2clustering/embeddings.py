from typing import Union, Optional

from fastembed import TextEmbedding
from fastembed import ImageEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class embeddings:
    def __init__(self, dbPath: str = "./qdrant_db") -> None:
        self.client = QdrantClient(path=dbPath)
        self.txtEmbeddings = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.imgEmbeddings = ImageEmbedding(model_name="Qdrant/clip-ViT-B-32-vision")
        self.setupCollections()

    def setupCollections(self):
        """Initializes collections with correct vector sizes if they don't exist."""
        
        if not self.client.collection_exists("txtCollection"):
            self.client.create_collection(
                collection_name="txtCollection",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        
        
        if not self.client.collection_exists("imgCollection"):
            self.client.create_collection(
                collection_name="imgCollection",
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )

    def generate_text_embedding(self, file_content: str):
        """Generates a text embedding for a single file's content."""
        embedding = list(self.txtEmbeddings.embed(documents=[file_content]))[0]
        return embedding

    def generate_image_embedding(self, image_path: str):
        """Generates an image embedding for a single image file."""
        embedding = list(self.imgEmbeddings.embed(images=[image_path]))[0]
        return embedding

    def insert_text(self, point_id: Union[int, str], file_content: str, metadata: Optional[dict] = None):
        """Generates and inserts a text embedding into the database."""
        embedding = self.generate_text_embedding(file_content)
        
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=metadata or {}
        )
        self.client.upsert(
            collection_name="txtCollection",
            points=[point]
        )

    def insert_image(self, point_id: Union[int, str], image_path: str, metadata: Optional[dict] = None):
        """Generates and inserts an image embedding into the database."""
        embedding = self.generate_image_embedding(image_path)
        
        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=metadata or {}
        )
        self.client.upsert(
            collection_name="imgCollection",
            points=[point]
        )

