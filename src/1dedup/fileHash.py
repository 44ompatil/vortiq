import hashlib
from pathlib import Path
from typing import List, Tuple


class fileHash:
	def __init__(self) -> None:
		self.chunkSize = 4194304

	def hashFiles(self, filePaths : Tuple[List[Path], List[Path]]):

		relPath = filePaths[0]
		# absPath = filePaths[1]

		fileHashes = []

		for file in relPath:
			path = Path(file)
			hasher = hashlib.sha256()
			with open(path, 'rb') as f:
				while content := f.read(self.chunkSize):
					hasher.update(content)
				
			fileHashes.append(hasher.hexdigest())

		return fileHashes
	