from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple
import os

class DuplicateDetectorService:
    def __init__(self):
        # Create cache directory if it doesn't exist
        cache_dir = './models_cache'
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize the model
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder=cache_dir)
        
        # Store for embeddings and texts
        self.stored_embeddings: List[np.ndarray] = []
        self.stored_texts: List[str] = []
        
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        Returns normalized score between 0 and 1
        """
        cosine_sim = float(np.dot(embedding1, embedding2) / 
                          (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
        # Normalize from [-1, 1] to [0, 1] and round to 4 decimal places
        normalized_sim = min(max((cosine_sim + 1) / 2, 0.0), 1.0)
        return round(normalized_sim, 4)
    
    def check_duplicate(self, email_content: str) -> Tuple[bool, float]:
        """
        Check if email content is duplicate
        Returns: (is_duplicate: bool, confidence_score: float)
        """
        # Get embedding for new email
        new_embedding = self.model.encode([email_content])[0]
        
        max_similarity = 0.0
        
        # Compare with existing embeddings
        for stored_embedding in self.stored_embeddings:
            similarity = self.compute_similarity(new_embedding, stored_embedding)
            max_similarity = max(max_similarity, similarity)
        
        # Store the new embedding and text
        self.stored_embeddings.append(new_embedding)
        self.stored_texts.append(email_content)
        
        return max_similarity > 0.8, max_similarity 