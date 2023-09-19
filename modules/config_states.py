"""
Supports saving and restoring wet and extensions from a known working set of commits
"""

import os
import json
import time
import tqdm

from datetime import datetime
import git

from modules import shared, extensions, errors
from modules.paths_internal import script_path, config_states_dir

all_config_states = {}


def list_config_states():
    global all_config_states

    all_config_states.clear()
    os.makedirs(config_states_dir, exist_ok=True)

    config_states = []
    for filename in os.listdir(config_states_dir):
        if filename.endswith(".json"):
            path = os.path.join(config_states_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    j = json.load(f)
                    assert "created_at" in j, '"created_at" does not exist'
                    j["filepath"] = path
                    config_states.append(j)
            except Exception as e:
                print(f'[ERROR]: Config states {path}, {e}')

    config_states = sorted(config_states, key=lambda cs: cs["created_at"], reverse=True)

    for cs in config_states:
        timestamp = time.asctime(time.gmtime(cs["created_at"]))
        name = cs.get("name", "Config")
        full_name = f"{name}: {timestamp}"
        all_config_states[full_name] = cs

    return all_config_states


def get_wet_config():
    wet_repo = None

    try:
        if os.path.exists(os.path.join(script_path, ".git")):
            wet_repo = git.Repo(script_path)
    except Exception:
        errors.report(f"Error reading wet git info from {script_path}", exc_info=True)

    wet_remote = None
    wet_commit_hash = None
    wet_commit_date = None
    wet_branch = None
    if wet_repo and not wet_repo.bare:
        try:
            wet_remote = next(wet_repo.remote().urls, None)
            head = wet_repo.head.commit
            wet_commit_date = wet_repo.head.commit.committed_date
            wet_commit_hash = head.hexsha
            wet_branch = wet_repo.active_branch.name

        except Exception:
            wet_remote = None

    return {
        "remote": wet_remote,
        "commit_hash": wet_commit_hash,
        "commit_date": wet_commit_date,
        "branch": wet_branch,
    }


def get_extension_config():
    ext_config = {}

    for ext in extensions.extensions:
        ext.read_info_from_repo()

        entry = {
            "name": ext.name,
            "path": ext.path,
            "enabled": ext.enabled,
            "is_builtin": ext.is_builtin,
            "remote": ext.remote,
            "commit_hash": ext.commit_hash,
            "commit_date": ext.commit_date,
            "branch": ext.branch,
            "have_info_from_repo": ext.have_info_from_repo
        }

        ext_config[ext.name] = entry

    return ext_config


def get_config():
    creation_time = datetime.now().timestamp()
    wet_config = get_wet_config()
    ext_config = get_extension_config()

    return {
        "created_at": creation_time,
        "wet": wet_config,
        "extensions": ext_config
    }


def restore_wet_config(config):
    print("* Restoring wet state...")

    if "wet" not in config:
        print("Error: No wet data saved to config")
        return

    wet_config = config["wet"]

    if "commit_hash" not in wet_config:
        print("Error: No commit saved to wet config")
        return

    wet_commit_hash = wet_config.get("commit_hash", None)
    wet_repo = None

    try:
        if os.path.exists(os.path.join(script_path, ".git")):
            wet_repo = git.Repo(script_path)
    except Exception:
        errors.report(f"Error reading wet git info from {script_path}", exc_info=True)
        return

    try:
        wet_repo.git.fetch(all=True)
        wet_repo.git.reset(wet_commit_hash, hard=True)
        print(f"* Restored wet to commit {wet_commit_hash}.")
    except Exception:
        errors.report(f"Error restoring wet to commit{wet_commit_hash}")


def restore_extension_config(config):
    print("* Restoring extension state...")

    if "extensions" not in config:
        print("Error: No extension data saved to config")
        return

    ext_config = config["extensions"]

    results = []
    disabled = []

    for ext in tqdm.tqdm(extensions.extensions):
        if ext.is_builtin:
            continue

        ext.read_info_from_repo()
        current_commit = ext.commit_hash

        if ext.name not in ext_config:
            ext.disabled = True
            disabled.append(ext.name)
            results.append((ext, current_commit[:8], False, "Saved extension state not found in config, marking as disabled"))
            continue

        entry = ext_config[ext.name]

        if "commit_hash" in entry and entry["commit_hash"]:
            try:
                ext.fetch_and_reset_hard(entry["commit_hash"])
                ext.read_info_from_repo()
                if current_commit != entry["commit_hash"]:
                    results.append((ext, current_commit[:8], True, entry["commit_hash"][:8]))
            except Exception as ex:
                results.append((ext, current_commit[:8], False, ex))
        else:
            results.append((ext, current_commit[:8], False, "No commit hash found in config"))

        if not entry.get("enabled", False):
            ext.disabled = True
            disabled.append(ext.name)
        else:
            ext.disabled = False

    shared.opts.disabled_extensions = disabled
    shared.opts.save(shared.config_filename)

    print("* Finished restoring extensions. Results:")
    for ext, prev_commit, success, result in results:
        if success:
            print(f"  + {ext.name}: {prev_commit} -> {result}")
        else:
            print(f"  ! {ext.name}: FAILURE ({result})")
