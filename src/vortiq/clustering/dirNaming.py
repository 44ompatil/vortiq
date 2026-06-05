import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
from vortiq.clustering.fileContent import FileContent

class DirNaming:
    def __init__(self, top_n_words=2):

        self.file_extractor = FileContent()
        self.top_n_words = top_n_words
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z]+\b'
        )

    def generate_names(self, cluster_to_files: dict):

        cluster_names = {}
        
        for label, files in cluster_to_files.items():

            if label == -1:
                cluster_names[label] = "Uncategorized"
                continue
            
            texts = []
            for file_path in files:
                try:
                    text = self.file_extractor.extract(Path(file_path))
                    filename_text = Path(file_path).stem.replace('-', ' ').replace('_', ' ')
                    combined = f"{text} {filename_text}" if text else filename_text
                    if combined and combined.strip():
                        texts.append(combined)
                except Exception as e:
                    print(f"Error extracting content from {file_path}: {e}")

            if not texts:
                cluster_names[label] = f"Cluster_{label}"
                continue

            combined_text = " ".join(texts)
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform([combined_text])
                feature_names = self.vectorizer.get_feature_names_out()
                
                scores = tfidf_matrix.toarray()[0]
                
                top_indices = np.argsort(scores)[::-1][:self.top_n_words]
                
                top_words = [feature_names[i].capitalize() for i in top_indices]
                folder_name = "_".join(top_words)
                
                if not folder_name:
                    folder_name = f"Cluster_{label}"
                    
                cluster_names[label] = folder_name
                
            except ValueError:
                cluster_names[label] = f"Cluster_{label}"
                
        return cluster_names
