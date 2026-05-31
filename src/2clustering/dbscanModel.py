from qdrant_client import QdrantClient


class dataProcessing:
	def __init__(self, txtCollection : str, imgCollection : str, dbPath: str = "./qdrant_db") -> None:
		self.client = QdrantClient(path=dbPath)
		self.txtCollection = txtCollection
		self.imgCollection = imgCollection
		self.PageSize = 30

	def getTxtPointID(self):
		offset = None

		while True:
			points, nextOffset = self.client.scroll(
				collection_name=self.txtCollection,
				with_vectors=True,
				with_payload=False,
				offset=offset,
				limit=self.PageSize
			)
			yield from points
			if nextOffset is None:
				break

			offset = nextOffset

	def getImgPointID(self):
		offset = None

		while True:
			points, nextOffset = self.client.scroll(
				collection_name=self.imgCollection,
				with_vectors=True,
				with_payload=False,
				offset=offset,
				limit=self.PageSize
			)
			yield from points
			if nextOffset is None:
				break

			offset = nextOffset
















# from sklearn.cluster import DBSCAN
# from sklearn import metrics

# class dbScanModel:
# 	def __init__(self) -> None:
# 		self.minPts = 5
# 		self.epsilon = 1

# 	def model(self, X):

# 		mlModel = DBSCAN(eps=self.epsilon, min_samples=self.minPts,metric='cosine')
# 		mlModel.fit_predict(X)
# 		labels = mlModel.labels_