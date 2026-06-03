import os
from pathlib import Path
from typing import Tuple

class dirTraversal:

	def __init__(self, sourceDir : Path) -> None:

		self.sourceDir = Path(sourceDir)
	
		if not self.sourceDir.exists():
			raise FileNotFoundError(f"[PATH] : {sourceDir} not found.")
			
		if not self.sourceDir.is_dir():
			raise NotADirectoryError(f"[PATH] : {sourceDir} is not a directory.")
	

	def traverseDir(self) -> Tuple[list[Path], list[Path]]:

		relPath = []
		absPath = []
		
		for root, directory, files in os.walk(self.sourceDir):
			rootPath = Path(root)
			
			for file in files:
				fPath = rootPath / file
				absPath.append(fPath.resolve())
				relPath.append(fPath.relative_to(self.sourceDir))

		return relPath, absPath