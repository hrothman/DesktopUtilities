#!/usr/bin/env python3
import os
import hashlib
import argparse
import shutil
from collections import defaultdict
import csv
import difflib
import json
import mimetypes
from datetime import datetime

# -----------------------------
# Helpers: general file scanning
# -----------------------------

def get_file_metadata(path):
    """Get comprehensive metadata for a file."""
    try:
        stat = os.stat(path)
        mime_type, _ = mimetypes.guess_type(path)
        
        return {
            "full_path": os.path.abspath(path),
            "size_bytes": stat.st_size,
            "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
            "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
            "file_mime_type": mime_type or "application/octet-stream"
        }
    except (OSError, ValueError) as e:
        # Return minimal metadata if we can't get full info
        return {
            "full_path": os.path.abspath(path),
            "size_bytes": 0,
            "created_date": "unknown",
            "modified_date": "unknown", 
            "file_mime_type": "unknown"
        }

def hash_file(path, block_size=1024 * 1024):
    """Return SHA-256 hash of the file contents."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def find_files(root):
    """Yield full paths to all files under root (recursively)."""
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            if os.path.isfile(full_path):
                yield full_path


def group_by_size(files, min_size=1):
    """Group files by exact size, skipping smaller than min_size bytes."""
    size_map = defaultdict(list)
    for p in files:
        try:
            size = os.path.getsize(p)
        except OSError:
            continue
        if size >= min_size:
            size_map[size].append(p)
    return size_map


def group_by_hash(size_map):
    """
    For each size group with >1 file, compute content hash and group by hash.
    Returns a dict: {hash: [paths...]} but only for real duplicate groups (len > 1).
    """
    hash_map = defaultdict(list)
    for size, paths in size_map.items():
        if len(paths) < 2:
            continue  # unique by size
        for p in paths:
            try:
                h = hash_file(p)
                hash_map[h].append(p)
            except (OSError, PermissionError):
                continue

    # keep only groups with real duplicates
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def write_exact_report(dupe_groups, report_path):
    """
    Write a CSV report with columns:
    group_id, hash, role (original/duplicate), path
    """
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["group_id", "hash", "role", "path"])

        for group_id, (file_hash, paths) in enumerate(dupe_groups.items(), start=1):
            # first file is treated as original
            for idx, p in enumerate(paths):
                role = "original" if idx == 0 else "duplicate"
                writer.writerow([group_id, file_hash, role, p])


def move_duplicates(dupe_groups, dest_root):
    """
    Move duplicates (all but the first file in each group) into dest_root.
    Returns list of (src, dst).
    """
    moved = []

    if not os.path.exists(dest_root):
        os.makedirs(dest_root)

    for file_hash, paths in dupe_groups.items():
        if len(paths) < 2:
            continue

        original = paths[0]
        duplicates = paths[1:]

        for i, dup in enumerate(duplicates, start=1):
            base = os.path.basename(dup)
            name, ext = os.path.splitext(base)
            hash_prefix = file_hash[:8]

            new_name = f"{name}_DUP_{hash_prefix}_{i}{ext}"
            dest_path = os.path.join(dest_root, new_name)

            counter = 1
            final_dest = dest_path
            while os.path.exists(final_dest):
                final_dest = os.path.join(
                    dest_root, f"{name}_DUP_{hash_prefix}_{i}_{counter}{ext}"
                )
                counter += 1

            try:
                shutil.move(dup, final_dest)
                moved.append((dup, final_dest))
            except (OSError, PermissionError) as e:
                print(f"[WARN] Failed to move {dup}: {e}")

    return moved

# ------------------------------------------
# Near-duplicate text detection (v1 vs v2)
# ------------------------------------------

DEFAULT_TEXT_EXTENSIONS = [
    ".txt", ".md", ".py", ".js", ".ts",
    ".json", ".csv", ".html", ".htm",
    ".css", ".java", ".c", ".cpp", ".cs"
]


def is_text_candidate(path, allowed_exts):
    """Return True if file extension is in allowed_exts."""
    _, ext = os.path.splitext(path)
    return ext.lower() in allowed_exts


def text_similarity(path1, path2):
    """
    Return a similarity ratio between 0 and 1 for two text files.
    Uses difflib.SequenceMatcher on full contents.
    """
    try:
        with open(path1, "r", encoding="utf-8", errors="ignore") as f1:
            text1 = f1.read()
        with open(path2, "r", encoding="utf-8", errors="ignore") as f2:
            text2 = f2.read()
    except OSError:
        return 0.0

    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def find_near_duplicate_texts(files, allowed_exts, similarity_threshold=0.9):
    """
    Find pairs of text files that are very similar (ratio >= similarity_threshold).

    Heuristics to keep it reasonable:
      - Only compare files with extensions in allowed_exts.
      - Bucket by (directory, extension).
      - Within each bucket, only compare files with similar sizes
        (difference <= max(10% of size, 4096 bytes)).
    """
    # Collect candidates
    candidates = [f for f in files if is_text_candidate(f, allowed_exts)]

    # Bucket: (dirpath, ext) -> [paths]
    buckets = defaultdict(list)
    for p in candidates:
        dirpath = os.path.dirname(p)
        _, ext = os.path.splitext(p)
        key = (dirpath, ext.lower())
        buckets[key].append(p)

    results = []  # list of (path_a, path_b, ratio)

    for (dirpath, ext), paths in buckets.items():
        if len(paths) < 2:
            continue

        # Sort by size so we can limit comparisons to similar-sized files
        paths_with_size = []
        for p in paths:
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            paths_with_size.append((p, size))

        paths_with_size.sort(key=lambda x: x[1])

        # Compare each file to subsequent files with similar size
        n = len(paths_with_size)
        for i in range(n):
            path_i, size_i = paths_with_size[i]

            # Reasonable cap to avoid O(n^2) explosion in huge dirs:
            # only check next ~50 neighbors with similar size
            max_neighbors = 50
            checked = 0

            for j in range(i + 1, n):
                if checked >= max_neighbors:
                    break

                path_j, size_j = paths_with_size[j]

                size_diff = abs(size_j - size_i)
                size_tolerance = max(int(0.1 * size_i), 4096)  # 10% or 4 KB
                if size_diff > size_tolerance:
                    # Since list is sorted by size, further ones will be even larger
                    break

                checked += 1

                ratio = text_similarity(path_i, path_j)
                if ratio >= similarity_threshold:
                    results.append((path_i, path_j, ratio))

    return results


def write_near_text_report(pairs, report_path):
    """
    Write CSV with columns:
    file_a, file_b, similarity_ratio
    """
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file_a", "file_b", "similarity_ratio"])
        for a, b, r in pairs:
            writer.writerow([a, b, f"{r:.4f}"])


def write_json_report(dupe_groups, near_pairs, report_path):
    """
    Write a JSON report in the user's requested format.
    Each object represents an original file with its duplicates and near-duplicates.
    """
    result = []
    
    # Keep track of all files that are in exact duplicate groups
    exact_duplicate_files = set()
    for file_hash, paths in dupe_groups.items():
        for path in paths:
            exact_duplicate_files.add(os.path.abspath(path))
    
    # Process exact duplicate groups
    for file_hash, paths in dupe_groups.items():
        if len(paths) < 1:
            continue
            
        # First file is the original
        original_path = paths[0]
        original_metadata = get_file_metadata(original_path)
        original_abs_path = os.path.abspath(original_path)
        
        # Create the group object with full_path as key
        file_group = {
            "fileHash": file_hash,
            "original_file": original_metadata["full_path"],
            "metadata": {
                "size_bytes": original_metadata["size_bytes"],
                "created_date": original_metadata["created_date"],
                "modified_date": original_metadata["modified_date"],
                "file_mime_type": original_metadata["file_mime_type"]
            },
            "duplicates": [],
            "near_duplicates": []
        }
        
        # Add exact duplicates (all files after the first)
        for dup_path in paths[1:]:
            dup_metadata = get_file_metadata(dup_path)
            file_group["duplicates"].append({
                dup_metadata["full_path"]: {
                    "hash": file_hash,
                    "full_path": dup_metadata["full_path"],
                    "size_bytes": dup_metadata["size_bytes"],
                    "created_date": dup_metadata["created_date"],
                    "modified_date": dup_metadata["modified_date"],
                    "file_mime_type": dup_metadata["file_mime_type"]
                }
            })
        
        # Find near-duplicates for this original file
        # Only include files that are NOT exact duplicates of this file
        for path_a, path_b, similarity in near_pairs:
            path_a_abs = os.path.abspath(path_a)
            path_b_abs = os.path.abspath(path_b)
            
            # Check if either file in the pair matches our original
            near_dup_path = None
            if path_a_abs == original_abs_path:
                near_dup_path = path_b
                near_dup_path_abs = path_b_abs
            elif path_b_abs == original_abs_path:
                near_dup_path = path_a
                near_dup_path_abs = path_a_abs
            
            # Only add if it's a valid near-duplicate
            if near_dup_path and near_dup_path_abs not in exact_duplicate_files:
                # Skip perfect matches (similarity = 1.0) - those should be exact duplicates
                if similarity < 1.0:
                    near_dup_metadata = get_file_metadata(near_dup_path)
                    near_dup_hash = hash_file(near_dup_path)
                    
                    # Check if we already added this near-duplicate to avoid duplicates
                    already_added = any(
                        near_dup_metadata["full_path"] in nd
                        for nd in file_group["near_duplicates"]
                    )
                    
                    if not already_added:
                        file_group["near_duplicates"].append({
                            near_dup_metadata["full_path"]: {
                                "hash": near_dup_hash,
                                "full_path": near_dup_metadata["full_path"],
                                "size_bytes": near_dup_metadata["size_bytes"],
                                "created_date": near_dup_metadata["created_date"],
                                "modified_date": near_dup_metadata["modified_date"],
                                "file_mime_type": near_dup_metadata["file_mime_type"],
                                "similarity_score": similarity
                            }
                        })
        
        result.append(file_group)
    
    # Handle near-duplicates that don't have exact duplicates
    # (files that only appear in near-duplicate pairs, not exact duplicate groups)
    processed_files = set()
    for file_group in result:
        processed_files.add(file_group["original_file"])
        for dup in file_group["duplicates"]:
            # Each duplicate is a dict with path as key
            for path in dup.keys():
                processed_files.add(path)
        for near_dup in file_group["near_duplicates"]:
            # Each near_duplicate is a dict with path as key  
            for path in near_dup.keys():
                processed_files.add(path)
    
    # Find near-duplicate pairs where neither file is in an exact duplicate group
    # and neither file has been processed yet
    standalone_near_dups = {}
    for path_a, path_b, similarity in near_pairs:
        path_a_abs = os.path.abspath(path_a)
        path_b_abs = os.path.abspath(path_b)
        
        # Skip perfect matches - they should be exact duplicates
        if similarity >= 1.0:
            continue
        
        # Only process if neither file is already handled
        if (path_a_abs not in exact_duplicate_files and 
            path_b_abs not in exact_duplicate_files and
            path_a_abs not in processed_files and 
            path_b_abs not in processed_files):
            
            # Create a group for path_a if it doesn't exist
            if path_a_abs not in standalone_near_dups:
                file_hash = hash_file(path_a)
                metadata = get_file_metadata(path_a)
                standalone_near_dups[path_a_abs] = {
                    "fileHash": file_hash,
                    "original_file": metadata["full_path"],
                    "metadata": {
                        "size_bytes": metadata["size_bytes"],
                        "created_date": metadata["created_date"],
                        "modified_date": metadata["modified_date"],
                        "file_mime_type": metadata["file_mime_type"]
                    },
                    "duplicates": [],
                    "near_duplicates": []
                }
                processed_files.add(path_a_abs)
            
            # Add path_b as a near-duplicate if not already processed
            if path_b_abs not in processed_files:
                near_dup_metadata = get_file_metadata(path_b)
                near_dup_hash = hash_file(path_b)
                standalone_near_dups[path_a_abs]["near_duplicates"].append({
                    "hash": near_dup_hash,
                    "full_path": near_dup_metadata["full_path"],
                    "size_bytes": near_dup_metadata["size_bytes"],
                    "created_date": near_dup_metadata["created_date"],
                    "modified_date": near_dup_metadata["modified_date"],
                    "file_mime_type": near_dup_metadata["file_mime_type"],
                    "similarity_score": similarity
                })
                processed_files.add(path_b_abs)
    
    # Add standalone near-duplicate groups to result
    result.extend(standalone_near_dups.values())
    
    # Write JSON file
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

# -----------------------------
# Main CLI
# -----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Find exact and near-duplicate files."
    )
    parser.add_argument("root", help="Root directory to scan.")

    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        help="Minimum file size in bytes to consider for duplicate detection (default: 1).",
    )

    parser.add_argument(
        "--move",
        metavar="DEST_DIR",
        help="If set, move exact duplicate copies into this directory (keeps one original per group).",
    )

    parser.add_argument(
        "--report",
        metavar="CSV_PATH",
        default="duplicates_report.csv",
        help="Path to write exact-duplicate CSV report (default: duplicates_report.csv).",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format: csv (default) or json. JSON format combines exact and near duplicates in a structured tree.",
    )

    # Near-duplicate text options
    parser.add_argument(
        "--find-near-text",
        action="store_true",
        help="If set, also search for near-duplicate text files and write a separate report.",
    )
    parser.add_argument(
        "--near-text-extensions",
        nargs="+",
        default=DEFAULT_TEXT_EXTENSIONS,
        help=(
            "File extensions to treat as text for near-duplicate detection "
            "(default: some common text/code extensions). Example: --near-text-extensions .txt .md"
        ),
    )
    parser.add_argument(
        "--near-text-sim",
        type=float,
        default=0.9,
        help="Similarity threshold (0-1) for near-duplicate text files (default: 0.9).",
    )
    parser.add_argument(
        "--near-text-report",
        metavar="CSV_PATH",
        default="near_duplicates_text.csv",
        help="Path to write near-duplicate text CSV report (default: near_duplicates_text.csv).",
    )

    args = parser.parse_args()
    root = os.path.abspath(args.root)

    print(f"Scanning: {root}")
    files = list(find_files(root))
    print(f"Found {len(files)} files. Grouping by size for exact duplicates...")

    # ---- Exact duplicates ----
    size_map = group_by_size(files, min_size=args.min_size)

    print("Computing hashes for potential duplicates...")
    dupe_groups = group_by_hash(size_map)

    # ---- Near-duplicate text detection (optional) ----
    near_pairs = []
    if args.find_near_text:
        print("Searching for near-duplicate text files...")
        allowed_exts = [e.lower() if e.startswith(".") else f".{e.lower()}"
                        for e in args.near_text_extensions]
        near_pairs = find_near_duplicate_texts(
            files,
            allowed_exts=allowed_exts,
            similarity_threshold=args.near_text_sim,
        )
        if near_pairs:
            print(f"Found {len(near_pairs)} near-duplicate text file pairs.")
        else:
            print("No near-duplicate text files found (above threshold).")

    # ---- Write reports ----
    
    # Create outputs directory
    outputs_dir = "outputs"
    os.makedirs(outputs_dir, exist_ok=True)
    
    if args.format == "json":
        # JSON format combines everything into one structured file
        base_report_name = os.path.basename(args.report)
        json_report_path = os.path.join(outputs_dir, base_report_name.replace('.csv', '.json') if base_report_name.endswith('.csv') else base_report_name + '.json')
        print(f"Writing JSON report to {json_report_path} ...")
        write_json_report(dupe_groups, near_pairs, json_report_path)
        print("JSON report written.")
        
        if dupe_groups:
            total_duplicates = sum(len(paths) - 1 for paths in dupe_groups.values())
            print(f"Found {len(dupe_groups)} groups of exact duplicates ({total_duplicates} duplicate files).")
    else:
        # Original CSV format
        if dupe_groups:
            csv_report_path = os.path.join(outputs_dir, os.path.basename(args.report))
            print(f"Found {len(dupe_groups)} groups of exact duplicates.")
            print(f"Writing exact-duplicate report to {csv_report_path} ...")
            write_exact_report(dupe_groups, csv_report_path)
            print("Exact-duplicate report written.")
        else:
            print("No exact duplicate files found.")

        # Write near-duplicate CSV if requested and found
        if args.find_near_text and near_pairs:
            near_report_path = os.path.join(outputs_dir, os.path.basename(args.near_text_report))
            print(f"Writing near-duplicate text report to {near_report_path} ...")
            write_near_text_report(near_pairs, near_report_path)
            print("Near-duplicate text report written.")

    # ---- Move duplicates (only for exact duplicates) ----

    # ---- Move duplicates (only for exact duplicates) ----
    if args.move and dupe_groups:
        dest_root = os.path.abspath(args.move)
        print(f"Moving duplicate copies to: {dest_root}")
        moved = move_duplicates(dupe_groups, dest_root)
        print(f"Moved {len(moved)} files.")


if __name__ == "__main__":
    main()
