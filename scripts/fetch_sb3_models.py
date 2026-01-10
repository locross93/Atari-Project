# scripts/fetch_sb3_models.py
import os, shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

# HF repos and filenames (as published by SB3 RL Zoo)
REPOS = {
    "BreakoutNoFrameskip-v4": ("sb3/dqn-BreakoutNoFrameskip-v4",
                               "dqn-BreakoutNoFrameskip-v4.zip"),
    "EnduroNoFrameskip-v4": ("sb3/dqn-EnduroNoFrameskip-v4",
                             "dqn-EnduroNoFrameskip-v4.zip"),
    "SpaceInvadersNoFrameskip-v4": ("sb3/dqn-SpaceInvadersNoFrameskip-v4",
                                    "dqn-SpaceInvadersNoFrameskip-v4.zip"),
}

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

def fetch_one(env_id, repo_id, filename):
    print(f"Downloading {env_id} from {repo_id} ...")
    src_path = hf_hub_download(repo_id=repo_id, filename=filename)  # local cache path
    dest_dir = MODELS / env_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_zip = dest_dir / "dqn.zip"
    shutil.copy2(src_path, dest_zip)
    print(f"Saved -> {dest_zip}")

if __name__ == "__main__":
    for env_id, (repo, fname) in REPOS.items():
        fetch_one(env_id, repo, fname)
    print("All models ready under Atari-Project/models/<ENV_ID>/dqn.zip")

