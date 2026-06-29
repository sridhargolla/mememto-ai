#!/usr/bin/env python3
"""
Model Setup Script for Memento AI

This script helps download and set up the required AI models for offline operation.
Run this script from the project root directory.
"""

import os
import sys
import urllib.request
import hashlib
from pathlib import Path


# Model configurations
MODELS = {
    "llm": {
        "name": "Qwen2.5-3B-Instruct-GGUF",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        "size_mb": 1900,
        "sha256": None,  # Add SHA256 checksum when available
        "description": "3B parameter LLM with 4-bit quantization (~1.9GB)"
    },
    "whisper": {
        "name": "Whisper Base English",
        "filename": "ggml-base.en.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
        "size_mb": 140,
        "sha256": None,
        "description": "English-only Whisper model for audio transcription (~140MB)"
    }
}


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text: str):
    """Print success message."""
    print(f"[SUCCESS] {text}")


def print_error(text: str):
    """Print error message."""
    print(f"[ERROR] {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"[WARNING] {text}")


def get_models_dir() -> Path:
    """Get the models directory path."""
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def download_file(url: str, destination: Path, description: str) -> bool:
    """Download a file with progress indicator."""
    try:
        print(f"\nDownloading {description}...")
        print(f"From: {url}")
        print(f"To: {destination}")
        
        def progress_hook(block_num, block_size, total_size):
            """Display download progress."""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded / total_size) * 100)
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total_size / (1024 * 1024)
                sys.stdout.write(f"\r  Progress: {percent:.1f}% ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print()  # New line after progress
        print_success(f"Downloaded: {destination.name}")
        return True
        
    except Exception as e:
        print_error(f"Failed to download: {e}")
        return False


def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """Verify file SHA256 checksum."""
    if not expected_sha256:
        print_warning("No checksum provided, skipping verification")
        return True
    
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        calculated_hash = sha256_hash.hexdigest()
        if calculated_hash == expected_sha256:
            print_success("Checksum verified")
            return True
        else:
            print_error(f"Checksum mismatch: expected {expected_sha256}, got {calculated_hash}")
            return False
            
    except Exception as e:
        print_error(f"Checksum verification failed: {e}")
        return False


def check_model_exists(model_key: str, models_dir: Path) -> bool:
    """Check if a model file already exists."""
    model_config = MODELS[model_key]
    model_path = models_dir / model_config["filename"]
    return model_path.exists()


def setup_model(model_key: str, force: bool = False) -> bool:
    """Setup a specific model."""
    if model_key not in MODELS:
        print_error(f"Unknown model: {model_key}")
        return False
    
    model_config = MODELS[model_key]
    models_dir = get_models_dir()
    model_path = models_dir / model_config["filename"]
    
    print_header(f"Setting up {model_config['name']}")
    print(f"Description: {model_config['description']}")
    print(f"Size: ~{model_config['size_mb']}MB")
    
    # Check if model already exists
    if model_path.exists() and not force:
        print_warning(f"Model already exists: {model_path}")
        response = input("  Re-download? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping...")
            return True
    
    # Download model
    if not download_file(model_config["url"], model_path, model_config["description"]):
        return False
    
    # Verify checksum if available
    if model_config["sha256"]:
        if not verify_checksum(model_path, model_config["sha256"]):
            print_error("Checksum verification failed. Please download manually.")
            return False
    
    print_success(f"Model setup complete: {model_path}")
    return True


def setup_all_models(force: bool = False) -> bool:
    """Setup all required models."""
    print_header("Memento AI - Model Setup")
    
    models_dir = get_models_dir()
    print(f"Models directory: {models_dir}")
    try:
        free_space = models_dir.stat().st_volume_free / (1024**3)
        print(f"Available space: {free_space:.2f}GB")
    except AttributeError:
        import shutil
        try:
            total, used, free = shutil.disk_usage(models_dir)
            print(f"Available space: {free / (1024**3):.2f}GB")
        except Exception:
            print("Available space: Unknown")
    
    success = True
    for model_key in MODELS:
        if not setup_model(model_key, force):
            success = False
    
    print_header("Setup Summary")
    if success:
        print_success("All models setup successfully!")
        print("\nNext steps:")
        print("1. Update your .env file with MODEL_PATH")
        print(f"   MODEL_PATH=models/{MODELS['llm']['filename']}")
        print(f"   WHISPER_MODEL=models/{MODELS['whisper']['filename']}")
        print("2. Start the backend server")
        print("3. Enjoy offline AI!")
    else:
        print_error("Some models failed to setup. Please check the errors above.")
        print("\nManual download links:")
        for model_key, config in MODELS.items():
            print(f"  {config['name']}: {config['url']}")
    
    return success


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup AI models for Memento AI")
    parser.add_argument("--model", choices=list(MODELS.keys()), help="Specific model to setup")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    parser.add_argument("--all", action="store_true", help="Setup all models")
    
    args = parser.parse_args()
    
    if args.all:
        success = setup_all_models(args.force)
    elif args.model:
        success = setup_model(args.model, args.force)
    else:
        # Interactive mode
        print_header("Memento AI - Model Setup")
        print("This script will download AI models for offline operation.")
        print("\nAvailable models:")
        for key, config in MODELS.items():
            print(f"  {key}: {config['name']} (~{config['size_mb']}MB)")
        
        print("\nOptions:")
        print("  1. Download all models")
        print("  2. Download specific model")
        print("  3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            success = setup_all_models(args.force)
        elif choice == "2":
            model_choice = input(f"Enter model key ({'/'.join(MODELS.keys())}): ").strip()
            success = setup_model(model_choice, args.force)
        else:
            print("Exiting...")
            return
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
