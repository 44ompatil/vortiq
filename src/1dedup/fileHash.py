import hashlib
from pathlib import Path
from typing import List, Tuple, Dict


class fileHash:
	def __init__(self) -> None:
		self.chunkSize = 4194304

	def hashFiles(self, filePaths : Tuple[List[Path], List[Path]]) -> Dict[str, List[Path]]:

		relPath = filePaths[0]
		absPath = filePaths[1]

		fileHashes: Dict[str, List[Path]] = {}

		for path in absPath:
			hasher = hashlib.sha256()
			with open(path, 'rb') as f:
				while content := f.read(self.chunkSize):
					hasher.update(content)
				
			file_hash = hasher.hexdigest()
			if file_hash not in fileHashes:
				fileHashes[file_hash] = []
			fileHashes[file_hash].append(path)

		return fileHashes
	