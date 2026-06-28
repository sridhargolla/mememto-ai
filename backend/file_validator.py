import os
from typing import Optional


class FileValidator:
    """Validate file types using magic numbers (file signatures)."""
    
    # File signatures (magic numbers) for common formats
    FILE_SIGNATURES = {
        # PDF
        b'\x25\x50\x44\x46': 'pdf',
        # PNG
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'png',
        # JPEG
        b'\xFF\xD8\xFF': 'jpg',
        # JPEG (alternative start)
        b'\xFF\xD8\xFF\xE0': 'jpg',
        b'\xFF\xD8\xFF\xE1': 'jpg',
        # GIF
        b'\x47\x49\x46\x38': 'gif',
        # TIFF (little-endian)
        b'\x49\x49\x2A\x00': 'tiff',
        # TIFF (big-endian)
        b'\x4D\x4D\x00\x2A': 'tiff',
        # BMP
        b'\x42\x4D': 'bmp',
        # WAV
        b'\x52\x49\x46\x46': 'wav',
        # MP3 (ID3v2)
        b'\x49\x44\x33': 'mp3',
        # MP3 (frame sync)
        b'\xFF\xFB': 'mp3',
        b'\xFF\xFA': 'mp3',
        b'\xFF\xF3': 'mp3',
        b'\xFF\xF2': 'mp3',
    }
    
    @staticmethod
    def get_file_signature(file_path: str, max_bytes: int = 12) -> Optional[bytes]:
        """
        Read file signature (magic number) from file.
        
        Args:
            file_path: Path to the file
            max_bytes: Maximum number of bytes to read
        
        Returns:
            File signature as bytes, or None if file cannot be read
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read(max_bytes)
        except Exception:
            return None
    
    @staticmethod
    def validate_file_type(file_path: str, expected_extension: str) -> bool:
        """
        Validate that the file's magic number matches its extension.
        
        Args:
            file_path: Path to the file
            expected_extension: Expected file extension (e.g., 'pdf', 'jpg')
        
        Returns:
            True if file signature matches extension, False otherwise
        """
        signature = FileValidator.get_file_signature(file_path)
        if signature is None:
            return False
        
        # Check against known signatures
        for sig, file_type in FileValidator.FILE_SIGNATURES.items():
            if signature.startswith(sig):
                return file_type == expected_extension.lower()
        
        # For text files, we can't validate by signature
        # Accept txt files without signature check
        if expected_extension.lower() == 'txt':
            return True
        
        return False
    
    @staticmethod
    def get_detected_type(file_path: str) -> Optional[str]:
        """
        Detect file type from magic number.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Detected file type, or None if unknown
        """
        signature = FileValidator.get_file_signature(file_path)
        if signature is None:
            return None
        
        for sig, file_type in FileValidator.FILE_SIGNATURES.items():
            if signature.startswith(sig):
                return file_type
        
        return None
