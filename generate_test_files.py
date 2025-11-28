#!/usr/bin/env python3
"""
Structured Test File Generator for Duplicate Detection Script.

This generator creates a controlled test environment where we:
1. Define the expected duplicate structure FIRST
2. Generate files according to that structure
3. Validate that our detection script finds what we expect

This approach makes debugging much easier and tests more reliable.
"""

import os
import shutil
import random
import string
import json
import difflib
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from pathlib import Path

@dataclass
class TestConfig:
    """Configuration for test file generation."""
    num_unique_files: int = 20
    max_file_size: int = 1024 * 50  # 50KB max
    min_file_size: int = 100        # 100 bytes min
    max_dir_depth: int = 3          # How deep to nest directories
    duplicate_percentage: float = 0.7      # 70% of files get duplicates
    near_duplicate_percentage: float = 0.4  # 40% get near-duplicates
    max_duplicates_per_file: int = 4        # Max exact copies per file
    max_near_duplicates_per_file: int = 3   # Max similar copies per file
    similarity_range: Tuple[float, float] = (0.8, 0.95)  # Near-duplicate similarity range
    output_dir: str = "./demo"
    random_seed: Optional[int] = 42  # For reproducible tests

@dataclass 
class FileSpec:
    """Specification for a file to be created."""
    path: str
    content: str
    size: int
    file_type: str
    hash: Optional[str] = None

@dataclass
class DuplicateGroup:
    """Represents a group of exact duplicates."""
    original_file: FileSpec
    duplicates: List[FileSpec] = field(default_factory=list)
    
@dataclass
class NearDuplicatePair:
    """Represents a pair of near-duplicate files."""
    file1: FileSpec
    file2: FileSpec
    expected_similarity: float

@dataclass
class TestPlan:
    """The complete test plan - what we expect to create and find."""
    unique_files: List[FileSpec] = field(default_factory=list)
    duplicate_groups: List[DuplicateGroup] = field(default_factory=list) 
    near_duplicate_pairs: List[NearDuplicatePair] = field(default_factory=list)
    directory_structure: Dict[str, List[str]] = field(default_factory=dict)
    
    def get_all_files(self) -> List[FileSpec]:
        """Get all files that should be created."""
        all_files = []
        
        # Add unique files
        all_files.extend(self.unique_files)
        
        # Add duplicates
        for group in self.duplicate_groups:
            all_files.append(group.original_file)
            all_files.extend(group.duplicates)
            
        # Add near-duplicates that aren't already included
        existing_paths = {f.path for f in all_files}
        for pair in self.near_duplicate_pairs:
            if pair.file1.path not in existing_paths:
                all_files.append(pair.file1)
            if pair.file2.path not in existing_paths:
                all_files.append(pair.file2)
                
        return all_files

class ContentGenerator:
    """Generates various types of file content."""
    
    FILE_TYPES = {
        '.txt': 'text/plain',
        '.py': 'text/x-python', 
        '.js': 'application/javascript',
        '.html': 'text/html',
        '.css': 'text/css',
        '.json': 'application/json',
        '.md': 'text/markdown',
        '.csv': 'text/csv'
    }
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
    
    def generate_content(self, file_type: str, target_size: int) -> str:
        """Generate content of specified type and approximate size."""
        if file_type == '.txt':
            return self._generate_text_content(target_size)
        elif file_type == '.py':
            return self._generate_python_content(target_size)
        elif file_type == '.js':
            return self._generate_javascript_content(target_size)
        elif file_type == '.html':
            return self._generate_html_content(target_size)
        elif file_type == '.css':
            return self._generate_css_content(target_size)
        elif file_type == '.json':
            return self._generate_json_content(target_size)
        elif file_type == '.md':
            return self._generate_markdown_content(target_size)
        elif file_type == '.csv':
            return self._generate_csv_content(target_size)
        else:
            return self._generate_text_content(target_size)
    
    def create_near_duplicate(self, original_content: str, target_similarity: float) -> str:
        """Create a near-duplicate with controlled similarity."""
        lines = original_content.split('\n')
        num_lines_to_modify = max(1, int(len(lines) * (1 - target_similarity)))
        
        modified_lines = lines.copy()
        
        # Randomly modify some lines to achieve target similarity
        for _ in range(num_lines_to_modify):
            if len(modified_lines) > 1:
                line_idx = random.randint(0, len(modified_lines) - 1)
                original_line = modified_lines[line_idx]
                
                # Different modification strategies
                if random.choice([True, False]):
                    # Add some text
                    modified_lines[line_idx] = original_line + " // MODIFIED"
                else:
                    # Change some words
                    words = original_line.split()
                    if words:
                        word_idx = random.randint(0, len(words) - 1)
                        words[word_idx] = f"CHANGED_{words[word_idx]}"
                        modified_lines[line_idx] = " ".join(words)
        
        return '\n'.join(modified_lines)
    
    def _generate_text_content(self, target_size: int) -> str:
        """Generate plain text content."""
        words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", 
                "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore"]
        
        content = []
        current_size = 0
        
        while current_size < target_size:
            line = " ".join(random.choices(words, k=random.randint(5, 15)))
            content.append(line.capitalize() + ".")
            current_size += len(line) + 1
            
        return "\n".join(content)
    
    def _generate_python_content(self, target_size: int) -> str:
        """Generate Python code content."""
        base_code = '''#!/usr/bin/env python3
"""
Generated test module.
"""

import os
import sys
from datetime import datetime

class DataProcessor:
    def __init__(self, config=None):
        self.config = config or {}
        self.processed_count = 0
    
    def process_item(self, item):
        """Process a single data item."""
        self.processed_count += 1
        return f"processed_{item}_{self.processed_count}"
    
    def get_stats(self):
        """Return processing statistics."""
        return {
            "processed_count": self.processed_count,
            "timestamp": datetime.now().isoformat()
        }

def main():
    processor = DataProcessor()
    
    # Process some test data
    test_items = ["item_1", "item_2", "item_3"]
    results = [processor.process_item(item) for item in test_items]
    
    print("Processing complete:")
    print(f"Results: {results}")
    print(f"Stats: {processor.get_stats()}")

if __name__ == "__main__":
    main()
'''
        
        # Pad with comments if needed
        while len(base_code) < target_size:
            base_code += f"\n# Additional comment line {random.randint(1, 1000)}"
            
        return base_code
    
    def _generate_javascript_content(self, target_size: int) -> str:
        """Generate JavaScript content."""
        base_js = '''/**
 * Generated test JavaScript module
 */

class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(a, b) {
        const result = a + b;
        this.history.push({operation: 'add', operands: [a, b], result});
        return result;
    }
    
    subtract(a, b) {
        const result = a - b;
        this.history.push({operation: 'subtract', operands: [a, b], result});
        return result;
    }
    
    getHistory() {
        return this.history;
    }
    
    clear() {
        this.history = [];
    }
}

// Usage example
const calc = new Calculator();
console.log('Addition:', calc.add(5, 3));
console.log('Subtraction:', calc.subtract(10, 4));
console.log('History:', calc.getHistory());
'''
        
        while len(base_js) < target_size:
            base_js += f"\n// Generated comment {random.randint(1, 1000)}"
            
        return base_js
    
    def _generate_html_content(self, target_size: int) -> str:
        """Generate HTML content."""
        base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .content { background: #f5f5f5; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Document</h1>
        <div class="content">
            <p>This is a generated test HTML document.</p>
            <ul>
                <li>Feature 1</li>
                <li>Feature 2</li>
                <li>Feature 3</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
        
        while len(base_html) < target_size:
            base_html = base_html.replace('</body>', 
                f'    <p>Additional content paragraph {random.randint(1, 1000)}.</p>\n</body>')
            
        return base_html
    
    def _generate_css_content(self, target_size: int) -> str:
        """Generate CSS content."""
        base_css = '''/* Generated test stylesheet */

body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: #f9f9f9;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1, h2, h3 {
    color: #333;
    margin-bottom: 1rem;
}

.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.button {
    background: #007acc;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}

.button:hover {
    background: #005999;
}
'''
        
        while len(base_css) < target_size:
            rule_num = random.randint(1, 1000)
            base_css += f'''
.generated-class-{rule_num} {{
    margin: 10px;
    padding: 5px;
    color: #{random.randint(100000, 999999):06x};
}}
'''
            
        return base_css
    
    def _generate_json_content(self, target_size: int) -> str:
        """Generate JSON content."""
        base_data = {
            "name": "Test Configuration",
            "version": "1.0.0",
            "description": "Generated test JSON file",
            "settings": {
                "debug": True,
                "timeout": 30,
                "retry_attempts": 3
            },
            "features": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "generator": "test_file_generator"
            }
        }
        
        # Add features to reach target size
        feature_count = 0
        while len(json.dumps(base_data, indent=2)) < target_size:
            feature_count += 1
            base_data["features"].append({
                "id": f"feature_{feature_count}",
                "enabled": random.choice([True, False]),
                "config": {"value": random.randint(1, 100)}
            })
            
        return json.dumps(base_data, indent=2)
    
    def _generate_markdown_content(self, target_size: int) -> str:
        """Generate Markdown content."""
        base_md = '''# Test Document

This is a generated test markdown document.

## Features

- Feature 1: Basic functionality
- Feature 2: Advanced options  
- Feature 3: Integration support

## Code Example

```python
def hello_world():
    print("Hello, World!")
    
hello_world()
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| debug   | true  | Enable debug mode |
| timeout | 30    | Request timeout |

## Notes

This document was automatically generated for testing purposes.
'''
        
        while len(base_md) < target_size:
            section_num = random.randint(1, 1000)
            base_md += f'''
## Section {section_num}

Generated content for section {section_num}. This content is added to reach the target file size.

- Point 1
- Point 2
- Point 3
'''
            
        return base_md
    
    def _generate_csv_content(self, target_size: int) -> str:
        """Generate CSV content."""
        headers = ["id", "name", "age", "city", "salary", "department"]
        rows = [",".join(headers)]
        
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
        
        row_count = 1
        while len("\n".join(rows)) < target_size:
            row = [
                str(row_count),
                f"Employee_{row_count}",
                str(random.randint(22, 65)),
                random.choice(cities),
                str(random.randint(40000, 120000)),
                random.choice(departments)
            ]
            rows.append(",".join(row))
            row_count += 1
            
        return "\n".join(rows)

class TestPlanGenerator:
    """Generates the test plan - what files should be created and their relationships."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.content_gen = ContentGenerator(config.random_seed)
        
    def generate_plan(self) -> TestPlan:
        """Generate a complete test plan."""
        print(f"🎯 Generating test plan...")
        print(f"   - {self.config.num_unique_files} unique files")
        print(f"   - {self.config.duplicate_percentage:.0%} will have exact duplicates")
        print(f"   - {self.config.near_duplicate_percentage:.0%} will have near-duplicates")
        
        plan = TestPlan()
        
        # Generate unique files first
        unique_files = self._generate_unique_files()
        plan.unique_files = unique_files
        
        # Select files for duplication
        files_to_duplicate = random.sample(
            unique_files, 
            int(len(unique_files) * self.config.duplicate_percentage)
        )
        
        # Create duplicate groups
        for original_file in files_to_duplicate:
            group = self._create_duplicate_group(original_file)
            plan.duplicate_groups.append(group)
        
        # Select text files for near-duplication
        text_files = [f for f in plan.get_all_files() 
                     if f.file_type in ['.txt', '.py', '.js', '.html', '.css', '.md']]
        
        files_for_near_dup = random.sample(
            text_files,
            min(len(text_files), int(len(unique_files) * self.config.near_duplicate_percentage))
        )
        
        # Create near-duplicate pairs
        for original_file in files_for_near_dup:
            pairs = self._create_near_duplicate_pairs(original_file)
            plan.near_duplicate_pairs.extend(pairs)
        
        # Generate directory structure
        plan.directory_structure = self._plan_directory_structure(plan.get_all_files())
        
        self._print_plan_summary(plan)
        return plan
        
    def _generate_unique_files(self) -> List[FileSpec]:
        """Generate specifications for unique files."""
        files = []
        file_types = list(ContentGenerator.FILE_TYPES.keys())
        
        for i in range(self.config.num_unique_files):
            file_type = random.choice(file_types)
            size = random.randint(self.config.min_file_size, self.config.max_file_size)
            
            # Generate content
            content = self.content_gen.generate_content(file_type, size)
            
            # Create file spec
            file_spec = FileSpec(
                path=f"unique_file_{i:03d}{file_type}",
                content=content,
                size=len(content.encode('utf-8')),
                file_type=file_type
            )
            
            files.append(file_spec)
            
        return files
        
    def _create_duplicate_group(self, original_file: FileSpec) -> DuplicateGroup:
        """Create a group of exact duplicates for a file."""
        num_duplicates = random.randint(1, self.config.max_duplicates_per_file)
        
        group = DuplicateGroup(original_file=original_file)
        
        for i in range(num_duplicates):
            # Create duplicate with different name but same content
            base_name = Path(original_file.path).stem
            extension = Path(original_file.path).suffix
            
            duplicate_names = [
                f"{base_name}_copy_{i}{extension}",
                f"{base_name}_backup{extension}",
                f"{base_name} ({i+1}){extension}",
                f"Copy_of_{base_name}{extension}",
                f"{base_name.upper()}_DUP{extension}"
            ]
            
            dup_name = random.choice(duplicate_names)
            
            duplicate = FileSpec(
                path=dup_name,
                content=original_file.content,  # Exact same content
                size=original_file.size,
                file_type=original_file.file_type
            )
            
            group.duplicates.append(duplicate)
            
        return group
        
    def _create_near_duplicate_pairs(self, original_file: FileSpec) -> List[NearDuplicatePair]:
        """Create near-duplicate pairs for a file."""
        num_near_dups = random.randint(1, self.config.max_near_duplicates_per_file)
        pairs = []
        
        base_name = Path(original_file.path).stem
        extension = Path(original_file.path).suffix
        
        for i in range(num_near_dups):
            # Generate target similarity
            target_similarity = random.uniform(*self.config.similarity_range)
            
            # Create near-duplicate content
            near_dup_content = self.content_gen.create_near_duplicate(
                original_file.content, 
                target_similarity
            )
            
            # Create near-duplicate file spec
            near_dup_names = [
                f"{base_name}_v{i+2}{extension}",
                f"{base_name}_modified{extension}", 
                f"{base_name}_draft{extension}",
                f"{base_name}_final{extension}",
                f"{base_name}_updated{extension}"
            ]
            
            near_dup = FileSpec(
                path=random.choice(near_dup_names),
                content=near_dup_content,
                size=len(near_dup_content.encode('utf-8')),
                file_type=original_file.file_type
            )
            
            pair = NearDuplicatePair(
                file1=original_file,
                file2=near_dup,
                expected_similarity=target_similarity
            )
            
            pairs.append(pair)
            
        return pairs
        
    def _plan_directory_structure(self, all_files: List[FileSpec]) -> Dict[str, List[str]]:
        """Plan which files go in which directories."""
        structure = {"": []}  # Root directory
        
        # Create some subdirectories
        subdirs = []
        for depth in range(1, self.config.max_dir_depth + 1):
            for i in range(random.randint(1, 3)):  # 1-3 dirs per depth level
                if depth == 1:
                    subdir = f"subdir_{i}"
                else:
                    parent = random.choice([d for d in subdirs if d.count('/') == depth-2])
                    subdir = f"{parent}/subdir_{depth}_{i}"
                subdirs.append(subdir)
                structure[subdir] = []
        
        # Distribute files across directories
        all_dirs = list(structure.keys())
        
        for file_spec in all_files:
            # 60% chance to put in subdirectory, 40% in root
            if random.random() < 0.6 and subdirs:
                chosen_dir = random.choice(subdirs)
            else:
                chosen_dir = ""
                
            structure[chosen_dir].append(file_spec.path)
            
            # Update the file path to include directory
            if chosen_dir:
                file_spec.path = f"{chosen_dir}/{file_spec.path}"
                
        return structure
        
    def _print_plan_summary(self, plan: TestPlan):
        """Print a summary of the generated plan."""
        all_files = plan.get_all_files()
        
        print(f"\n📊 Test Plan Summary:")
        print(f"   Total files to create: {len(all_files)}")
        print(f"   Unique files: {len(plan.unique_files)}")
        print(f"   Duplicate groups: {len(plan.duplicate_groups)}")
        print(f"   Near-duplicate pairs: {len(plan.near_duplicate_pairs)}")
        print(f"   Directory levels: {len([d for d in plan.directory_structure.keys() if d])}")
        
        # Show file type distribution
        type_counts = {}
        for file_spec in all_files:
            type_counts[file_spec.file_type] = type_counts.get(file_spec.file_type, 0) + 1
        
        print(f"   File type distribution:")
        for file_type, count in sorted(type_counts.items()):
            print(f"     {file_type}: {count} files")

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


class FileCreator:
    """Creates actual files on disk according to the test plan."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        
    def create_files(self, plan: TestPlan) -> None:
        """Create all files specified in the test plan."""
        print(f"\n� Creating files in {self.config.output_dir}...")
        
        # Clean output directory
        self._clean_output_dir()
        
        # Create directory structure
        self._create_directories(plan.directory_structure)
        
        # Create all files
        all_files = plan.get_all_files()
        created_count = 0
        
        for file_spec in all_files:
            try:
                self._create_file(file_spec)
                created_count += 1
            except Exception as e:
                print(f"❌ Failed to create {file_spec.path}: {e}")
        
        print(f"✅ Created {created_count}/{len(all_files)} files successfully")
        
    def _clean_output_dir(self) -> None:
        """Remove and recreate the output directory."""
        if os.path.exists(self.config.output_dir):
            shutil.rmtree(self.config.output_dir)
        os.makedirs(self.config.output_dir)
        
    def _create_directories(self, structure: Dict[str, List[str]]) -> None:
        """Create the directory structure."""
        for dir_path in structure.keys():
            if dir_path:  # Skip root directory
                full_path = os.path.join(self.config.output_dir, dir_path)
                os.makedirs(full_path, exist_ok=True)
                
    def _create_file(self, file_spec: FileSpec) -> None:
        """Create a single file."""
        full_path = os.path.join(self.config.output_dir, file_spec.path)
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(file_spec.content)


class TestValidator:
    """Validates that our duplicate detection script finds what we expect."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        
    def validate_results(self, plan: TestPlan, detection_results: Dict) -> bool:
        """Validate that detection results match our expectations."""
        print(f"\n🔍 Validating detection results...")
        
        validation_passed = True
        
        # Validate exact duplicate groups
        exact_validation = self._validate_exact_duplicates(plan, detection_results)
        validation_passed = validation_passed and exact_validation
        
        # Validate near-duplicate pairs  
        near_validation = self._validate_near_duplicates(plan, detection_results)
        validation_passed = validation_passed and near_validation
        
        # Print overall result
        if validation_passed:
            print(f"🎉 All validations PASSED! Detection script is working correctly.")
        else:
            print(f"❌ Some validations FAILED. Check the output above for details.")
            
        return validation_passed
        
    def _validate_exact_duplicates(self, plan: TestPlan, results: Dict) -> bool:
        """Validate exact duplicate detection."""
        print(f"  📋 Validating exact duplicates...")
        
        expected_groups = len(plan.duplicate_groups)
        found_groups = len(results) if results else 0
        
        if found_groups != expected_groups:
            print(f"    ❌ Expected {expected_groups} duplicate groups, found {found_groups}")
            return False
            
        # Check each expected group
        for expected_group in plan.duplicate_groups:
            original_path = os.path.join(self.config.output_dir, expected_group.original_file.path)
            expected_dup_paths = {
                os.path.join(self.config.output_dir, dup.path) 
                for dup in expected_group.duplicates
            }
            
            # Find the group in results that contains our original
            found_group = self._find_group_containing_file(original_path, results)
            
            if not found_group:
                print(f"    ❌ No group found containing original file: {original_path}")
                return False
                
            # Check if all expected duplicates are found
            found_dup_paths = {
                dup_obj.get(list(dup_obj.keys())[0], {}).get('full_path', '')
                for dup_obj in found_group.get('duplicates', [])
            }
            
            missing_dups = expected_dup_paths - found_dup_paths
            extra_dups = found_dup_paths - expected_dup_paths
            
            if missing_dups:
                print(f"    ❌ Missing duplicates for {original_path}: {missing_dups}")
                return False
                
            if extra_dups:
                print(f"    ⚠️  Extra duplicates found for {original_path}: {extra_dups}")
                # This might be OK depending on the test
                
        print(f"    ✅ Exact duplicate validation passed")
        return True
        
    def _validate_near_duplicates(self, plan: TestPlan, results: Dict) -> bool:
        """Validate near-duplicate detection."""
        print(f"  📝 Validating near-duplicates...")
        
        expected_pairs = len(plan.near_duplicate_pairs)
        
        # Count found pairs across all groups
        found_pairs_count = 0
        for group in results:
            found_pairs_count += len(group.get('near_duplicates', []))
            
        print(f"    Expected pairs: {expected_pairs}, Found pairs: {found_pairs_count}")
        
        # Check each expected pair
        validation_passed = True
        
        for expected_pair in plan.near_duplicate_pairs:
            file1_path = os.path.join(self.config.output_dir, expected_pair.file1.path)
            file2_path = os.path.join(self.config.output_dir, expected_pair.file2.path)
            expected_similarity = expected_pair.expected_similarity
            
            found_pair = self._find_near_duplicate_pair(file1_path, file2_path, results)
            
            if not found_pair:
                print(f"    ❌ Near-duplicate pair not found: {file1_path} <-> {file2_path}")
                validation_passed = False
                continue
                
            found_similarity = found_pair.get('similarity_score', 0)
            similarity_diff = abs(found_similarity - expected_similarity)
            
            # Allow 5% tolerance in similarity
            if similarity_diff > 0.05:
                print(f"    ⚠️  Similarity mismatch: expected {expected_similarity:.3f}, "
                      f"found {found_similarity:.3f} (diff: {similarity_diff:.3f})")
                # This is a warning, not a failure for now
                
        if validation_passed:
            print(f"    ✅ Near-duplicate validation passed")
        else:
            print(f"    ❌ Near-duplicate validation failed")
            
        return validation_passed
        
    def _find_group_containing_file(self, file_path: str, results: Dict) -> Optional[Dict]:
        """Find the duplicate group that contains the specified file."""
        for group in results:
            # Check if it's the original file
            if group.get('original_file') == file_path:
                return group
                
            # Check if it's in duplicates
            for dup_obj in group.get('duplicates', []):
                for dup_path, dup_data in dup_obj.items():
                    if dup_data.get('full_path') == file_path:
                        return group
                        
        return None
        
    def _find_near_duplicate_pair(self, file1_path: str, file2_path: str, 
                                 results: Dict) -> Optional[Dict]:
        """Find a near-duplicate pair in the results."""
        for group in results:
            for near_dup_obj in group.get('near_duplicates', []):
                for near_path, near_data in near_dup_obj.items():
                    group_original = group.get('original_file')
                    
                    # Check if this pair matches (in either direction)
                    if ((group_original == file1_path and near_data.get('full_path') == file2_path) or
                        (group_original == file2_path and near_data.get('full_path') == file1_path)):
                        return near_data
                        
        return None


class TestRunner:
    """Orchestrates the entire test process."""
    
    def __init__(self, config: TestConfig = None):
        self.config = config or TestConfig()
        self.plan_generator = TestPlanGenerator(self.config)
        self.file_creator = FileCreator(self.config) 
        self.validator = TestValidator(self.config)
        
    def run_test(self) -> bool:
        """Run the complete test process."""
        print("🚀 Starting structured duplicate detection test...")
        print(f"📋 Configuration:")
        print(f"   Output directory: {self.config.output_dir}")
        print(f"   Unique files: {self.config.num_unique_files}")
        print(f"   Duplicate %: {self.config.duplicate_percentage:.0%}")
        print(f"   Near-duplicate %: {self.config.near_duplicate_percentage:.0%}")
        print(f"   Random seed: {self.config.random_seed}")
        
        try:
            # Phase 1: Generate test plan
            plan = self.plan_generator.generate_plan()
            
            # Phase 2: Create files
            self.file_creator.create_files(plan)
            
            # Phase 3: Save the plan for later validation
            self._save_test_plan(plan)
            
            print(f"\n🔍 Test files created! Now run the detection script:")
            print(f"   python3 main.py {self.config.output_dir} --format json --find-near-text --near-text-sim 0.8")
            print(f"\nThen run validation with:")
            print(f"   python3 validate_test_results.py")
            print(f"\n📁 Output structure:")
            print(f"   test_outputs/ - Test plans and validation results")
            print(f"   outputs/      - Duplicate detection reports")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _save_test_plan(self, plan: TestPlan) -> None:
        """Save the test plan to a file for later validation."""
        plan_data = {
            "config": {
                "num_unique_files": self.config.num_unique_files,
                "duplicate_percentage": self.config.duplicate_percentage,
                "near_duplicate_percentage": self.config.near_duplicate_percentage,
                "output_dir": self.config.output_dir
            },
            "duplicate_groups": [
                {
                    "original_file": group.original_file.path,
                    "duplicates": [dup.path for dup in group.duplicates]
                }
                for group in plan.duplicate_groups
            ],
            "near_duplicate_pairs": [
                {
                    "file1": pair.file1.path,
                    "file2": pair.file2.path, 
                    "expected_similarity": pair.expected_similarity
                }
                for pair in plan.near_duplicate_pairs
            ],
            "all_files": [
                {
                    "path": f.path,
                    "size": f.size,
                    "file_type": f.file_type
                }
                for f in plan.get_all_files()
            ]
        }
        
        # Create test_outputs directory
        test_outputs_dir = "test_outputs"
        os.makedirs(test_outputs_dir, exist_ok=True)
        
        plan_file = os.path.join(test_outputs_dir, "test_plan.json")
        with open(plan_file, 'w') as f:
            json.dump(plan_data, f, indent=2)
            
        print(f"� Test plan saved to {plan_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate structured test files for duplicate detection")
    parser.add_argument("--num-files", type=int, default=20, help="Number of unique files to generate")
    parser.add_argument("--max-size", type=int, default=51200, help="Maximum file size in bytes")
    parser.add_argument("--dup-percent", type=float, default=0.7, help="Percentage of files that get duplicates")
    parser.add_argument("--near-percent", type=float, default=0.4, help="Percentage of files that get near-duplicates")
    parser.add_argument("--output-dir", default="./demo", help="Output directory for test files")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible tests")
    
    args = parser.parse_args()
    
    # Create configuration
    config = TestConfig(
        num_unique_files=args.num_files,
        max_file_size=args.max_size,
        duplicate_percentage=args.dup_percent,
        near_duplicate_percentage=args.near_percent,
        output_dir=args.output_dir,
        random_seed=args.seed
    )
    
    # Run the test
    runner = TestRunner(config)
    success = runner.run_test()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()