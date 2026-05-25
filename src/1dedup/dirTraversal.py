from pathlib import Path


class dirTraversal:

	def __init__(self, sourceDir : Path) -> None:

		self.sourceDir = sourceDir
	
		if not self.sourceDir.is_dir():
			raise NotADirectoryError(f"[PATH] : {sourceDir} is not a directory.")
	
		if not self.sourceDir.exists():
			raise FileNotFoundError(f"[PATH] : {sourceDir} not found.")
		