import os
try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("Vui lòng cài đặt thư viện: pip install huggingface_hub")
    exit(1)

model_id = "capleaf/viXTTS"
local_dir = os.path.join(os.getcwd(), "models_cache", "viXTTS")

print(f"Downloading model {model_id} to {local_dir}...")
print("This may take a few minutes depending on your connection.")

try:
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
    print("\nDONE! You can now start the server.")
except Exception as e:
    print(f"\nError downloading: {e}")
