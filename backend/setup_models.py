"""
Setup script to download GGUF models for offline inference.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

def download_model():
    """Download a suitable GGUF model for offline inference."""
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Model configuration - using a lightweight but capable model
    # You can change this to other GGUF models from Hugging Face
    MODEL_ID = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
    MODEL_FILE = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    print(f"Downloading {MODEL_FILE} from {MODEL_ID}...")
    print("This may take a while depending on your internet connection.")
    print("The model is approximately 4.3 GB in size.")
    
    try:
        # Download the model
        model_path = hf_hub_download(
            repo_id=MODEL_ID,
            filename=MODEL_FILE,
            local_dir=models_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"\n[OK] Model downloaded successfully!")
        print(f"Location: {model_path}")
        
        # Update .env file
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r") as f:
                env_content = f.read()
            
            # Update MODEL_PATH
            if "MODEL_PATH" in env_content:
                env_content = env_content.replace(
                    f"MODEL_PATH=*",
                    f"MODEL_PATH={model_path}"
                )
            else:
                env_content += f"\nMODEL_PATH={model_path}\n"
            
            with open(env_path, "w") as f:
                f.write(env_content)
            
            print(f"[OK] Updated .env file with MODEL_PATH")
        else:
            print(f"[WARNING] Please add the following to your .env file:")
            print(f"MODEL_PATH={model_path}")
        
        print("\n[SUCCESS] Setup complete! You can now restart the backend server.")
        
    except Exception as e:
        print(f"\n[ERROR] Error downloading model: {e}")
        print("\nYou can manually download the model from:")
        print(f"https://huggingface.co/{MODEL_ID}")
        print(f"Download the file: {MODEL_FILE}")
        print(f"Place it in the 'models/' directory and update MODEL_PATH in .env")
        sys.exit(1)

if __name__ == "__main__":
    print("Memento AI - Model Setup")
    print("=" * 50)
    download_model()
