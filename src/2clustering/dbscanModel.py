from qdrant_client import QdrantClient

from sklearn.cluster import DBSCAN
from sklearn import metrics

import numpy as np

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

class dbScanModel:
	def __init__(self) -> None:
		self.minPts = 5
		self.epsilon = 0.2

		self.data = dataProcessing(txtCollection="txtCollection", imgCollection="imgCollection")

		# Get text points once to avoid multiple DB calls
		txtPoints = list(self.data.getTxtPointID())
		self.XTxt = np.array([point.vector for point in txtPoints]) if txtPoints else np.array([])
		self.txtPtId = [point.id for point in txtPoints]
		
		# Get image points once to avoid multiple DB calls
		imgPoints = list(self.data.getImgPointID())
		self.Ximg = np.array([point.vector for point in imgPoints]) if imgPoints else np.array([])
		self.imgPtId = [point.id for point in imgPoints]
		

	def model(self, X):

		mlModel = DBSCAN(eps=self.epsilon, min_samples=self.minPts,metric='cosine')
		mlModel.fit_predict(X)
		labels = mlModel.labels_

		return labels

	def predict_all(self):
		
		txt_labels = self.model(self.XTxt) if self.XTxt.size > 0 else np.array([])
		img_labels = self.model(self.Ximg) if self.Ximg.size > 0 else np.array([])
		
		return {
			"text_labels": txt_labels,
			"image_labels": img_labels
		}













