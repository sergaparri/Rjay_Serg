import os
import time
try:
    import win32file
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
import send2trash
from typing import List, Tuple, Dict
from core.file_analyzer import FileAnalyzer

class FileOperations:
    @staticmethod
    def is_onedrive_file_synced(file_path: str) -> bool:
        """Check if OneDrive file is fully synced and unlocked"""
        try:
            if "OneDrive" in file_path:
                sync_marker = file_path + ".tmp"
                if os.path.exists(sync_marker):
                    return False
            return True
        except:
            return False

    @staticmethod
    def resolve_duplicates(files: List[str], keep_pref: str, deletion_method: str, 
                          scoring_enabled: bool, score_weights: Dict[str, float]) -> Tuple[List[str], List[str]]:
        if len(files) <= 1:
            return files, []
        
        if scoring_enabled:
            # Score all files first
            scored_files = []
            for file in files:
                score = FileAnalyzer.calculate_file_score(file, score_weights)
                scored_files.append((file, score))
            
            # Sort by score (highest first)
            scored_files.sort(key=lambda x: x[1], reverse=True)
            files = [f[0] for f in scored_files]
        else:
            # Traditional sorting methods
            files.sort(key=lambda x: os.path.basename(x))
            if keep_pref == 'newest':
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            elif keep_pref == 'oldest':
                files.sort(key=lambda x: os.path.getmtime(x))
            elif keep_pref == 'largest':
                files.sort(key=lambda x: os.path.getsize(x), reverse=True)
            elif keep_pref == 'smallest':
                files.sort(key=lambda x: os.path.getsize(x))
        
        return [files[0]], files[1:]

    @staticmethod
    def safe_delete(file_path: str, method: str, max_retries: int = 5) -> bool:
        """Improved deletion with OneDrive support"""
        for attempt in range(max_retries):
            try:
                # Normalize path first
                file_path = os.path.abspath(file_path)
                
                # Check for long paths
                if len(file_path) > 240:  # Leave room for recycle bin ops
                    file_path = "\\\\?\\" + file_path
                
                # Check if file exists
                if not os.path.exists(file_path):
                    return True
                
                # Wait for OneDrive sync if needed
                if "OneDrive" in file_path:
                    if not FileOperations.is_onedrive_file_synced(file_path):
                        time.sleep(2)
                        if not FileOperations.is_onedrive_file_synced(file_path):
                            return False
                
                # Unlock file attributes
                if not os.access(file_path, os.W_OK):
                    os.chmod(file_path, 0o777)
                
                # Force close any handles (if pywin32 available)
                if HAS_WIN32:
                    try:
                        handle = win32file.CreateFile(
                            file_path,
                            win32file.GENERIC_WRITE,
                            win32file.FILE_SHARE_DELETE,
                            None,
                            win32file.OPEN_EXISTING,
                            win32file.FILE_FLAG_DELETE_ON_CLOSE,
                            None
                        )
                        win32file.CloseHandle(handle)
                    except Exception:
                        pass
                
                # Perform deletion
                if method == 'recycle':
                    send2trash.send2trash(file_path)
                else:
                    os.remove(file_path)
                
                return True
                
            except Exception as e:
                time.sleep(1 + attempt)  # Exponential backoff
                continue
        
        return False 