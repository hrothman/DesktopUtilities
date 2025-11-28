# Duplicate & Near-Duplicate File Cleaner
### Python Script for Safely Identifying, Reporting, and Cleaning Duplicate Files

This tool helps you **find and safely clean duplicate files** on your computer — even when filenames differ — and optionally detect **near-duplicate text files** (e.g., `notes_v1.txt`, `notes_v2.txt`).

It is designed to be:

- **Safe** — nothing is deleted automatically  
- **Auditable** — generates CSV reports for review  
- **Automated** — can move duplicate copies into a folder  
- **Extendable** — supports optional near-duplicate text detection  

---

## 🚀 Features

### **1. Exact Duplicate Detection (Automated & Safe)**
- Uses **SHA-256 content hashing** to identify duplicates by content, not name  
- Groups identical files  
- Generates a full CSV mapping `original → duplicates`  
- Can automatically move duplicate copies into a `duplicates/` folder  

### **2. Near-Duplicate Text Detection (Optional)**
- Uses a similarity algorithm to find files that are *similar, but not identical*  
- Ideal for versioned text files (v1, v2, final_final, etc.)  
- Outputs a separate CSV; **no automatic actions taken**  

### **3. Zero Risk**
- First run is report-only  
- Moving duplicates is reversible  
- You control which near-duplicates (if any) to remove  

---

# 📦 Installation

### **1. Ensure Python 3 is installed**

```bash
# 📦 Installation

### **1. Ensure Python 3 is installed**

```bash
python3 --version   # macOS/Linux
python --version    # Windows
```

### **2. No additional dependencies required**
This script uses only Python standard library modules.

---

## 🚀 Quick Start & Runbook

### **Basic Command Structure**
```bash
python3 main.py <directory_to_scan> [options]
```

### **Example 1: Basic Scan (Report Only)**
```bash
# Scan the demo directory and generate a report
python3 main.py ./demo

# Output: duplicates_report.csv
```

### **Example 2: Scan Your Home Documents**
```bash
# Scan your Documents folder
python3 main.py ~/Documents --min-size 1024

# Only considers files >= 1KB to avoid tiny system files
```

### **Example 3: Move Duplicates to Safe Location**
```bash
# Scan and move duplicate copies to a separate folder
python3 main.py ./demo --move ./moved_duplicates

# Original files stay in place, duplicates are moved
```

### **Example 4: Find Near-Duplicate Text Files**
```bash
# Also find similar text files (like v1.txt vs v2.txt)
python3 main.py ./demo --find-near-text --near-text-sim 0.85

# Output: duplicates_report.csv + near_duplicates_text.csv
```

### **Example 5: Complete Professional Scan**
```bash
# Full scan with custom settings and reports
python3 main.py ~/Documents \
  --min-size 1024 \
  --move ~/Desktop/found_duplicates \
  --report ~/Desktop/exact_duplicates.csv \
  --find-near-text \
  --near-text-sim 0.8 \
  --near-text-report ~/Desktop/similar_files.csv \
  --near-text-extensions .txt .md .py .js .html .css
```

---

## 📋 Command-Line Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `<directory>` | **Required.** Root directory to scan | - |
| `--min-size BYTES` | Minimum file size to consider | 1 |
| `--move DEST_DIR` | Move duplicates to this directory | None (report only) |
| `--report CSV_PATH` | Output file for exact duplicates | duplicates_report.csv |
| `--find-near-text` | Enable near-duplicate text detection | False |
| `--near-text-extensions` | File types to check for similarity | .txt .md .py .js .ts .json .csv .html .htm .css .java .c .cpp .cs |
| `--near-text-sim FLOAT` | Similarity threshold (0.0-1.0) | 0.9 |
| `--near-text-report CSV_PATH` | Output for near-duplicates | near_duplicates_text.csv |

---

## 📊 Understanding the Reports

### **Exact Duplicates Report (duplicates_report.csv)**
```csv
group_id,hash,role,path
1,a1b2c3d4,original,/path/to/photo.jpg
1,a1b2c3d4,duplicate,/path/to/photo copy.jpg
1,a1b2c3d4,duplicate,/path/to/photo (1).jpg
```

- **group_id**: Files in same group are identical
- **hash**: SHA-256 hash (first 8 chars shown)
- **role**: `original` (kept) vs `duplicate` (moved if --move used)
- **path**: Full file path

### **Near-Duplicates Report (near_duplicates_text.csv)**
```csv
file_a,file_b,similarity_ratio
/path/to/notes_v1.txt,/path/to/notes_v2.txt,0.9245
/path/to/draft.md,/path/to/final.md,0.8876
```

- **similarity_ratio**: 1.0 = identical, 0.0 = completely different
- **Manual review required** - script doesn't auto-move these

---

## ⚡ Recommended Workflow

### **Step 1: Safe Scan First**
```bash
# Always start with report-only to see what's found
python3 main.py ~/Documents --min-size 1024
```

### **Step 2: Review the Report**
Open `duplicates_report.csv` and verify the findings make sense.

### **Step 3: Move Duplicates (Optional)**
```bash
# If satisfied, re-run with --move
python3 main.py ~/Documents --min-size 1024 --move ~/Desktop/duplicates_moved
```

### **Step 4: Check for Near-Duplicates (Optional)**
```bash
# Find similar text files for manual review
python3 main.py ~/Documents --find-near-text --near-text-sim 0.85
```

### **Step 5: Manual Cleanup**
Review `near_duplicates_text.csv` and manually delete unwanted versions.

---

## 🔍 Tips & Best Practices

### **Performance Tips**
- Use `--min-size 1024` to skip tiny files
- Start with smaller directories to test
- Near-duplicate detection is slower on large text collections

### **Safety Tips**
- Always run without `--move` first to review findings
- Keep backups when cleaning important directories
- The moved files can always be restored from the destination folder

### **Common Use Cases**
```bash
# Photo cleanup
python3 main.py ~/Pictures --min-size 10240 --move ~/Desktop/duplicate_photos

# Document cleanup with text similarity
python3 main.py ~/Documents --find-near-text --move ~/Desktop/duplicate_docs

# Code cleanup
python3 main.py ~/Projects --find-near-text --near-text-extensions .py .js .ts .java
```

---

## 🛠️ Troubleshooting

### **"Permission denied" errors**
- Run with appropriate permissions
- Some system directories may be protected

### **Large number of duplicates found**
- Check if you're scanning system directories
- Increase `--min-size` to focus on larger files

### **Script runs slowly**
- Use `--min-size` to reduce files processed
- Near-duplicate detection is computationally intensive

### **No duplicates found when you expect them**
- Files must have identical content (not just names)
- Check file permissions and accessibility
python --version    # Windows
