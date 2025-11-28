#!/usr/bin/env python3
"""
Test file generator for duplicate file detection script.
Creates ~50 test files in ./demo with various scenarios:
- Exact duplicates
- Near-duplicate text files with slight variations
- Different file types
- Nested subdirectories
- Large files
- Version-like files (v1, v2, final, etc.)
"""

import os
import shutil
import random
import string
import json
from datetime import datetime

def ensure_clean_demo():
    """Remove and recreate the demo directory."""
    demo_path = "./demo"
    if os.path.exists(demo_path):
        shutil.rmtree(demo_path)
    os.makedirs(demo_path)
    return demo_path

def generate_random_text(lines=10, words_per_line=8):
    """Generate random text content."""
    words = [
        "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
        "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
        "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
        "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
        "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure",
        "python", "script", "file", "data", "test", "example", "function",
        "variable", "import", "class", "method", "return", "value", "string"
    ]
    
    content = []
    for _ in range(lines):
        line_words = random.sample(words, min(words_per_line, len(words)))
        content.append(" ".join(line_words).capitalize() + ".")
    return "\n".join(content)

def create_base_documents():
    """Create base documents that will be used to generate variations."""
    base_docs = {}
    
    # Document 1: Meeting notes
    base_docs["meeting_notes"] = """Meeting Notes - Q4 Planning
Date: November 28, 2025
Attendees: Alice, Bob, Charlie, Diana

Agenda:
1. Review quarterly targets
2. Discuss new project initiatives
3. Budget allocation for next quarter
4. Team performance reviews

Action Items:
- Alice: Finalize budget proposal by Dec 1
- Bob: Review technical requirements
- Charlie: Schedule follow-up meetings
- Diana: Prepare performance metrics

Next meeting: December 5, 2025 at 2:00 PM
Location: Conference Room B
"""

    # Document 2: Code snippet
    base_docs["python_script"] = """#!/usr/bin/env python3
import os
import sys
from datetime import datetime

def process_data(filename):
    \"\"\"Process data from the given file.\"\"\"
    try:
        with open(filename, 'r') as f:
            data = f.read()
        return data.strip()
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    result = process_data(filename)
    
    if result:
        print(f"Processed {len(result)} characters")
        print(f"Timestamp: {datetime.now()}")

if __name__ == "__main__":
    main()
"""

    # Document 3: Configuration
    base_docs["config"] = """{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "production_db",
        "ssl": true
    },
    "api": {
        "version": "v2.1",
        "timeout": 30,
        "retry_attempts": 3
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "features": {
        "analytics": true,
        "caching": true,
        "rate_limiting": false
    }
}"""

    return base_docs

def create_document_variations(base_docs, demo_path):
    """Create variations of base documents with slight differences."""
    variations = []
    
    for doc_name, content in base_docs.items():
        # Original version
        original_path = os.path.join(demo_path, f"{doc_name}_original.txt")
        with open(original_path, 'w') as f:
            f.write(content)
        variations.append(original_path)
        
        # Version 1 - minor changes
        v1_content = content.replace("2025", "2025 (updated)")
        if "Alice" in content:
            v1_content = v1_content.replace("Alice", "Alice Johnson")
        v1_path = os.path.join(demo_path, f"{doc_name}_v1.txt")
        with open(v1_path, 'w') as f:
            f.write(v1_content)
        variations.append(v1_path)
        
        # Version 2 - more changes
        v2_content = v1_content + "\n\n--- Additional notes added ---\nThis document has been revised."
        v2_path = os.path.join(demo_path, f"{doc_name}_v2.txt")
        with open(v2_path, 'w') as f:
            f.write(v2_content)
        variations.append(v2_path)
        
        # Final version - significant changes
        final_content = content.replace("\n", "\n\n")  # Add extra spacing
        if "def " in content:
            final_content = final_content.replace("def process_data", "def process_file_data")
        final_path = os.path.join(demo_path, f"{doc_name}_FINAL.txt")
        with open(final_path, 'w') as f:
            f.write(final_content)
        variations.append(final_path)
    
    return variations

def create_exact_duplicates(demo_path):
    """Create exact duplicate files with different names."""
    duplicates = []
    
    # Create a base file
    content = "This is important data that should not be lost.\n" * 100
    
    # Original
    original = os.path.join(demo_path, "important_data.txt")
    with open(original, 'w') as f:
        f.write(content)
    duplicates.append(original)
    
    # Exact duplicates with different names
    duplicate_names = [
        "important_data copy.txt",
        "important_data (1).txt",
        "important_data_backup.txt",
        "IMPORTANT_DATA.txt",
        "data_backup_final.txt"
    ]
    
    for name in duplicate_names:
        dup_path = os.path.join(demo_path, name)
        with open(dup_path, 'w') as f:
            f.write(content)  # Exact same content
        duplicates.append(dup_path)
    
    return duplicates

def create_binary_duplicates(demo_path):
    """Create binary files with exact duplicates."""
    duplicates = []
    
    # Create fake image data
    binary_data = bytes([random.randint(0, 255) for _ in range(1024 * 10)])  # 10KB
    
    # Original "image"
    original = os.path.join(demo_path, "photo.jpg")
    with open(original, 'wb') as f:
        f.write(binary_data)
    duplicates.append(original)
    
    # Duplicates
    for name in ["photo copy.jpg", "photo_backup.jpg", "IMG_001.jpg"]:
        dup_path = os.path.join(demo_path, name)
        with open(dup_path, 'wb') as f:
            f.write(binary_data)  # Exact same binary data
        duplicates.append(dup_path)
    
    return duplicates

def create_large_files(demo_path):
    """Create some larger files to test performance."""
    large_files = []
    
    # Large text file (about 100KB)
    large_content = generate_random_text(lines=1000, words_per_line=15)
    large_path = os.path.join(demo_path, "large_document.txt")
    with open(large_path, 'w') as f:
        f.write(large_content)
    large_files.append(large_path)
    
    # Duplicate of large file
    large_dup_path = os.path.join(demo_path, "large_document_backup.txt")
    with open(large_dup_path, 'w') as f:
        f.write(large_content)
    large_files.append(large_dup_path)
    
    # Large binary file (about 50KB)
    large_binary = bytes([random.randint(0, 255) for _ in range(1024 * 50)])
    large_bin_path = os.path.join(demo_path, "data.bin")
    with open(large_bin_path, 'wb') as f:
        f.write(large_binary)
    large_files.append(large_bin_path)
    
    # Duplicate binary
    large_bin_dup = os.path.join(demo_path, "data_copy.bin")
    with open(large_bin_dup, 'wb') as f:
        f.write(large_binary)
    large_files.append(large_bin_dup)
    
    return large_files

def create_nested_structure(demo_path):
    """Create nested directories with duplicates across different levels."""
    nested_files = []
    
    # Create nested directories
    subdirs = [
        "projects/web_app",
        "projects/mobile_app", 
        "backup/2025/november",
        "backup/2025/october",
        "documents/personal",
        "documents/work"
    ]
    
    for subdir in subdirs:
        full_path = os.path.join(demo_path, subdir)
        os.makedirs(full_path, exist_ok=True)
    
    # Create a common file that appears in multiple locations
    common_content = """# Project README
This is a standard README file for our project.

## Getting Started
1. Clone the repository
2. Install dependencies
3. Run the application

## Contributing
Please read our contributing guidelines.
"""
    
    readme_locations = [
        "projects/web_app/README.md",
        "projects/mobile_app/README.md",
        "backup/2025/november/README.md",
        "README_old.md"  # Root level
    ]
    
    for location in readme_locations:
        path = os.path.join(demo_path, location)
        with open(path, 'w') as f:
            f.write(common_content)
        nested_files.append(path)
    
    # Create similar but different config files
    base_config = {
        "app_name": "MyApp",
        "version": "1.0.0",
        "debug": False,
        "database_url": "postgresql://localhost/myapp"
    }
    
    # Web app config (slightly different)
    web_config = base_config.copy()
    web_config["app_name"] = "MyWebApp"
    web_config["port"] = 3000
    
    web_config_path = os.path.join(demo_path, "projects/web_app/config.json")
    with open(web_config_path, 'w') as f:
        json.dump(web_config, f, indent=2)
    nested_files.append(web_config_path)
    
    # Mobile app config (slightly different)
    mobile_config = base_config.copy()
    mobile_config["app_name"] = "MyMobileApp"
    mobile_config["platform"] = "react-native"
    
    mobile_config_path = os.path.join(demo_path, "projects/mobile_app/config.json")
    with open(mobile_config_path, 'w') as f:
        json.dump(mobile_config, f, indent=2)
    nested_files.append(mobile_config_path)
    
    # Backup config (exact duplicate)
    backup_config_path = os.path.join(demo_path, "backup/2025/november/config.json")
    with open(backup_config_path, 'w') as f:
        json.dump(web_config, f, indent=2)  # Exact duplicate of web config
    nested_files.append(backup_config_path)
    
    return nested_files

def create_different_file_types(demo_path):
    """Create files of different types with some duplicates."""
    files = []
    
    # HTML file
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Test Page</h1>
        <p>This is a sample HTML document.</p>
    </div>
</body>
</html>"""
    
    html_path = os.path.join(demo_path, "index.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    files.append(html_path)
    
    # Duplicate HTML with different name
    html_dup_path = os.path.join(demo_path, "home.html")
    with open(html_dup_path, 'w') as f:
        f.write(html_content)
    files.append(html_dup_path)
    
    # CSS file
    css_content = """body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
}

h1 {
    color: #333;
    border-bottom: 2px solid #007acc;
}"""
    
    css_path = os.path.join(demo_path, "styles.css")
    with open(css_path, 'w') as f:
        f.write(css_content)
    files.append(css_path)
    
    # JavaScript file
    js_content = """function calculateTotal(items) {
    let total = 0;
    for (let item of items) {
        total += item.price * item.quantity;
    }
    return total;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Example usage
const cartItems = [
    { name: 'Widget', price: 10.99, quantity: 2 },
    { name: 'Gadget', price: 25.50, quantity: 1 }
];

console.log('Total:', formatCurrency(calculateTotal(cartItems)));"""
    
    js_path = os.path.join(demo_path, "calculator.js")
    with open(js_path, 'w') as f:
        f.write(js_content)
    files.append(js_path)
    
    # CSV file
    csv_content = """Name,Age,City,Salary
John Smith,30,New York,50000
Jane Doe,25,Los Angeles,45000
Bob Johnson,35,Chicago,55000
Alice Williams,28,Houston,48000
Charlie Brown,32,Phoenix,52000"""
    
    csv_path = os.path.join(demo_path, "employees.csv")
    with open(csv_path, 'w') as f:
        f.write(csv_content)
    files.append(csv_path)
    
    # Duplicate CSV with slight modification
    csv_modified = csv_content.replace("50000", "51000")  # Slight change
    csv_mod_path = os.path.join(demo_path, "employees_updated.csv")
    with open(csv_mod_path, 'w') as f:
        f.write(csv_modified)
    files.append(csv_mod_path)
    
    return files

def create_version_like_files(demo_path):
    """Create files that look like different versions."""
    files = []
    
    base_content = """Project Proposal: Advanced Analytics Platform

Executive Summary:
Our company is proposing the development of an advanced analytics platform
that will revolutionize how we process and analyze customer data.

Key Features:
- Real-time data processing
- Machine learning integration  
- Interactive dashboards
- Automated reporting

Budget Estimate: $150,000
Timeline: 6 months
Team Size: 5 developers"""
    
    # Create version progression
    versions = [
        ("proposal_draft.txt", base_content),
        ("proposal_v1.txt", base_content.replace("$150,000", "$175,000")),
        ("proposal_v2.txt", base_content.replace("6 months", "8 months").replace("$150,000", "$175,000")),
        ("proposal_v2_reviewed.txt", base_content.replace("6 months", "8 months").replace("$150,000", "$185,000")),
        ("proposal_final.txt", base_content.replace("6 months", "8 months").replace("$150,000", "$200,000") + "\n\nApproved by: Management Team"),
        ("proposal_FINAL_FINAL.txt", base_content.replace("6 months", "8 months").replace("$150,000", "$200,000") + "\n\nApproved by: Management Team\nStatus: APPROVED")
    ]
    
    for filename, content in versions:
        path = os.path.join(demo_path, filename)
        with open(path, 'w') as f:
            f.write(content)
        files.append(path)
    
    return files

def main():
    """Generate all test files."""
    print("🚀 Generating test files for duplicate detection...")
    
    # Clean and create demo directory
    demo_path = ensure_clean_demo()
    
    all_files = []
    
    # Generate different types of test files
    print("📝 Creating base documents and variations...")
    base_docs = create_base_documents()
    all_files.extend(create_document_variations(base_docs, demo_path))
    
    print("📋 Creating exact duplicates...")
    all_files.extend(create_exact_duplicates(demo_path))
    
    print("🖼️  Creating binary duplicates...")
    all_files.extend(create_binary_duplicates(demo_path))
    
    print("📦 Creating large files...")
    all_files.extend(create_large_files(demo_path))
    
    print("📁 Creating nested directory structure...")
    all_files.extend(create_nested_structure(demo_path))
    
    print("🌐 Creating different file types...")
    all_files.extend(create_different_file_types(demo_path))
    
    print("📊 Creating version-like files...")
    all_files.extend(create_version_like_files(demo_path))
    
    print(f"\n✅ Generated {len(all_files)} test files in ./demo")
    print("\nTest scenarios covered:")
    print("  ✓ Exact duplicates with different names")
    print("  ✓ Near-duplicate text files (versions)")
    print("  ✓ Binary file duplicates")
    print("  ✓ Large files for performance testing")
    print("  ✓ Nested subdirectories")
    print("  ✓ Multiple file types (txt, html, css, js, csv, json, md)")
    print("  ✓ Version progression files (v1, v2, final, etc.)")
    
    print(f"\n🔍 Now run your duplicate detector:")
    print(f"   python3 main.py ./demo --find-near-text --near-text-sim 0.8")

if __name__ == "__main__":
    main()