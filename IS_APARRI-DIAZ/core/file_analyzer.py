import os
import hashlib
import math
import time
from typing import Dict, List, Set

class FileAnalyzer:
    @staticmethod
    def calculate_hash(file_path: str, chunk_size: int = 8192) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (IOError, PermissionError) as e:
            raise RuntimeError(f"Failed to hash {file_path}: {str(e)}")

    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        if os.path.islink(file1) or os.path.islink(file2):
            return os.path.realpath(file1) == os.path.realpath(file2)
        return FileAnalyzer.calculate_hash(file1) == FileAnalyzer.calculate_hash(file2)

    @staticmethod
    def find_duplicates(folder: str, filters: Dict) -> Dict[str, List[str]]:
        hashes = {}
        for root, _, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                if FileAnalyzer._passes_filters(file_path, filters):
                    try:
                        file_hash = FileAnalyzer.calculate_hash(file_path)
                        hashes.setdefault(file_hash, []).append(file_path)
                    except RuntimeError:
                        continue
        return {h: files for h, files in hashes.items() if len(files) > 1}

    @staticmethod
    def _passes_filters(file_path: str, filters: Dict) -> bool:
        if not os.path.exists(file_path) or os.path.islink(file_path):
            return False
        if filters['extensions']:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in {e.lower() for e in filters['extensions']}:
                return False
        size = os.path.getsize(file_path)
        if filters['min_size'] and size < filters['min_size']:
            return False
        if filters['max_size'] and size > filters['max_size']:
            return False
        return True

    @staticmethod
    def get_available_extensions(folder: str) -> Set[str]:
        """Scan folder and return all unique file extensions"""
        extensions = set()
        for root, _, files in os.walk(folder):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext:  # Only add if extension exists
                    extensions.add(ext)
        return extensions

    @staticmethod
    def calculate_file_score(file_path: str, weights: Dict[str, float]) -> float:
        """Calculate a score for the file based on various factors"""
        try:
            stats = os.stat(file_path)
            file_name = os.path.basename(file_path)
            dir_name = os.path.basename(os.path.dirname(file_path))
            ext = os.path.splitext(file_path)[1].lower()
            
            # Normalize factors between 0 and 1
            recency = 1 - (time.time() - stats.st_mtime) / (60 * 60 * 24 * 30)  # Last 30 days
            recency = max(0, min(1, recency))
            
            size = math.log10(stats.st_size + 1) / 12  # Log scale up to ~1TB
            size = max(0, min(1, size))
            
            # Location score (prefer certain directories)
            location = 0.5  # Default
            if 'download' in dir_name.lower():
                location = 0.3
            elif 'desktop' in dir_name.lower():
                location = 0.2
            elif 'documents' in dir_name.lower():
                location = 0.8
            elif 'pictures' in dir_name.lower():
                location = 0.7
            
            # Extension score (prefer common document formats)
            ext_score = 0.5  # Default
            if ext in ('.doc', '.docx', '.pdf', '.xls', '.xlsx'):
                ext_score = 0.9
            elif ext in ('.jpg', '.png', '.gif'):
                ext_score = 0.7
            elif ext in ('.tmp', '.bak', '.old'):
                ext_score = 0.1
            
            # Name score (prefer simpler names without special chars)
            name_chars = set(file_name.lower())
            special_chars = set('!@#$%^&*()+=[]{}|;:\'",<>?`~')
            name_score = 1 - (len(name_chars & special_chars) / 10)
            name_score = max(0.1, min(1, name_score))
            
            # Weighted sum
            score = (
                weights['recency'] * recency +
                weights['size'] * size +
                weights['location'] * location +
                weights['extension'] * ext_score +
                weights['name'] * name_score
            )
            
            return score
            
        except Exception:
            return 0.5  # Default score if anything fails 