# src/core/document_processor.py

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from llama_index.core import Document
from llama_index.readers.file import PDFReader

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handle document processing and validation"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self):
        self.pdf_reader = PDFReader()
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate if file is supported and within size limits"""
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
            
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file type: {file_path.suffix}")
            return False
            
        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            logger.error(f"File too large: {file_path.name} ({file_path.stat().st_size} bytes)")
            return False
            
        return True
    
    def process_file(self, file_path: Path) -> List[Document]:
        """Process a single file and return documents"""
        if not self.validate_file(file_path):
            return []
            
        try:
            if file_path.suffix.lower() == '.pdf':
                return self.pdf_reader.load_data(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._process_text_file(file_path)
            else:
                logger.warning(f"Unsupported file type for processing: {file_path}")
                return []
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    def _process_text_file(self, file_path: Path) -> List[Document]:
        """Process a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            metadata = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_type": "text"
            }
            
            return [Document(text=text, metadata=metadata)]
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return []
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a file"""
        if not file_path.exists():
            return {"error": "File not found"}
            
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "extension": file_path.suffix.lower(),
            "is_valid": self.validate_file(file_path)
        }