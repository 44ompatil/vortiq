import os
from pathlib import Path

from typing import Dict, List, Tuple


class fileStats:
	def __init__(self) -> None:
		pass

	def getStats(self, filePath : Tuple[List[Path], List[Path]]) -> Dict[Path, int]:

		relPath = filePath[0]
		absPath = filePath[1]
		stats : Dict[Path, int] = {}

		for file in absPath:
			stat_info = os.stat(file)
			fileSize = stat_info.st_size

			stats[file] = fileSize

		return stats
