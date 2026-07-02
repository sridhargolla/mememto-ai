class FileValidator:
    """Validate file types using magic numbers (file signatures)."""

    # File signatures (magic numbers) for common formats
    FILE_SIGNATURES = {
        # PDF
        b"\x25\x50\x44\x46": "pdf",
        # PNG
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        # JPEG
        b"\xff\xd8\xff": "jpg",
        # JPEG (alternative start)
        b"\xff\xd8\xff\xe0": "jpg",
        b"\xff\xd8\xff\xe1": "jpg",
        # GIF
        b"\x47\x49\x46\x38": "gif",
        # TIFF (little-endian)
        b"\x49\x49\x2a\x00": "tiff",
        # TIFF (big-endian)
        b"\x4d\x4d\x00\x2a": "tiff",
        # BMP
        b"\x42\x4d": "bmp",
        # WAV
        b"\x52\x49\x46\x46": "wav",
        # MP3 (ID3v2)
        b"\x49\x44\x33": "mp3",
        # MP3 (frame sync)
        b"\xff\xfb": "mp3",
        b"\xff\xfa": "mp3",
        b"\xff\xf3": "mp3",
        b"\xff\xf2": "mp3",
        # ZIP / DOCX / XLSX / PPTX (Office Open XML are ZIP archives)
        b"\x50\x4b\x03\x04": "zip",  # PK signature
        b"\x50\x4b\x05\x06": "zip",  # Empty ZIP
        b"\x50\x4b\x07\x08": "zip",  # Spanned ZIP
    }

    @staticmethod
    def get_file_signature(file_path: str, max_bytes: int = 12) -> bytes | None:
        """
        Read file signature (magic number) from file.

        Args:
            file_path: Path to the file
            max_bytes: Maximum number of bytes to read

        Returns:
            File signature as bytes, or None if file cannot be read
        """
        try:
            with open(file_path, "rb") as f:
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
                detected = file_type
                # ZIP-based formats: docx, xlsx, pptx, odt, etc. are all ZIP archives
                if detected == "zip" and expected_extension.lower() in {
                    "docx",
                    "doc",
                    "xlsx",
                    "xls",
                    "pptx",
                    "ppt",
                    "odt",
                    "ods",
                    "odp",
                    "zip",
                }:
                    return True
                return detected == expected_extension.lower()

        # For text/code files, we can't validate by signature — accept them
        return expected_extension.lower() in {
            "txt",
            "md",
            "csv",
            "json",
            "xml",
            "html",
            "log",
            "py",
            "js",
            "ts",
            "jsx",
            "tsx",
            "java",
            "c",
            "cpp",
            "cs",
            "go",
            "rs",
            "rtf",
            "odt",
        }

    @staticmethod
    def get_detected_type(file_path: str) -> str | None:
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
