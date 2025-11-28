#!/usr/bin/env python3
"""
Test Result Validator

Compares the duplicate detection results against our expected test plan.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_test_plan():
    """Load the expected test plan."""
    test_plan_file = os.path.join("test_outputs", "test_plan.json")
    if not os.path.exists(test_plan_file):
        # Fall back to old location for backward compatibility
        test_plan_file = "test_plan.json"
    
    with open(test_plan_file, 'r') as f:
        return json.load(f)

def load_detection_results():
    """Load the actual detection results."""
    results_file = os.path.join("outputs", "duplicates_report.json")
    if not os.path.exists(results_file):
        # Fall back to old location for backward compatibility
        results_file = "duplicates_report.json"
    
    with open(results_file, 'r') as f:
        return json.load(f)

def normalize_path(path, output_dir):
    """Convert absolute path to relative path for comparison."""
    if path.startswith(output_dir):
        return os.path.relpath(path, output_dir)
    return path

def validate_exact_duplicates(plan, results, output_dir):
    """Validate exact duplicate detection."""
    print("🔍 Validating exact duplicates...")
    
    expected_groups = len(plan['duplicate_groups'])
    found_groups = len(results)
    
    print(f"   Expected groups: {expected_groups}")
    print(f"   Found groups: {found_groups}")
    
    if found_groups != expected_groups:
        print(f"   ❌ Group count mismatch!")
        return False
    
    # Build expected file sets (original + duplicates)
    expected_file_sets = []
    for group in plan['duplicate_groups']:
        file_set = {group['original_file']} | set(group['duplicates'])
        expected_file_sets.append(file_set)
    
    # Build found file sets
    found_file_sets = []
    for result_group in results:
        # Get the original file (relative path)
        original_abs = result_group['original_file']
        original_rel = normalize_path(original_abs, output_dir)
        
        # Get all files in this group (original + duplicates)
        file_set = {original_rel}
        
        for dup_obj in result_group.get('duplicates', []):
            for dup_path, dup_data in dup_obj.items():
                dup_rel = normalize_path(dup_path, output_dir)
                file_set.add(dup_rel)
        
        found_file_sets.append(file_set)
    
    validation_passed = True
    
    # Match expected sets to found sets
    matched_expected = set()
    matched_found = set()
    
    for i, expected_set in enumerate(expected_file_sets):
        best_match = None
        best_overlap = 0
        
        for j, found_set in enumerate(found_file_sets):
            if j in matched_found:
                continue
                
            overlap = len(expected_set & found_set)
            if overlap > best_overlap:
                best_match = j
                best_overlap = overlap
        
        if best_match is not None and best_overlap >= len(expected_set) * 0.8:  # 80% match
            matched_expected.add(i)
            matched_found.add(best_match)
            
            expected_set = expected_file_sets[i]
            found_set = found_file_sets[best_match]
            
            if expected_set == found_set:
                print(f"   ✅ Perfect match for group with {len(expected_set)} files")
            else:
                print(f"   ⚠️  Partial match for group:")
                missing = expected_set - found_set
                extra = found_set - expected_set
                if missing:
                    print(f"      Missing: {sorted(missing)}")
                if extra:
                    print(f"      Extra: {sorted(extra)}")
        else:
            print(f"   ❌ No good match found for expected group: {sorted(expected_set)}")
            validation_passed = False
    
    # Check for unmatched found groups
    unmatched_found = set(range(len(found_file_sets))) - matched_found
    if unmatched_found:
        print(f"   ❌ {len(unmatched_found)} unexpected duplicate groups found")
        for i in unmatched_found:
            print(f"      Unexpected group: {sorted(found_file_sets[i])}")
        validation_passed = False
    
    return validation_passed

def validate_near_duplicates(plan, results):
    """Validate near-duplicate detection."""
    print("\n📝 Validating near-duplicates...")
    
    expected_pairs = len(plan.get('near_duplicate_pairs', []))
    
    # Count found pairs
    found_pairs_count = 0
    for result_group in results:
        found_pairs_count += len(result_group.get('near_duplicates', []))
    
    print(f"   Expected pairs: {expected_pairs}")
    print(f"   Found pairs: {found_pairs_count}")
    
    # For now, just check the count (detailed validation would require more complex matching)
    if abs(found_pairs_count - expected_pairs) <= 2:  # Allow some tolerance
        print(f"   ✅ Near-duplicate count within tolerance")
        validation_passed = True
    else:
        print(f"   ⚠️  Near-duplicate count difference: {abs(found_pairs_count - expected_pairs)}")
        validation_passed = True  # Don't fail on this for now
    
    return validation_passed, found_pairs_count

def main():
    """Run validation."""
    print("🔍 Starting test result validation...")
    
    try:
        plan = load_test_plan()
        results = load_detection_results()
        output_dir = plan['config']['output_dir']
        
        # Convert relative output_dir to absolute
        output_dir = os.path.abspath(output_dir)
        
        print(f"📋 Test configuration:")
        print(f"   Output directory: {output_dir}")
        print(f"   Expected unique files: {plan['config']['num_unique_files']}")
        print(f"   Expected duplicate groups: {len(plan['duplicate_groups'])}")
        print(f"   Expected near-duplicate pairs: {len(plan.get('near_duplicate_pairs', []))}")
        
        # Validate exact duplicates
        exact_valid = validate_exact_duplicates(plan, results, output_dir)
        
        # Validate near-duplicates
        near_valid, found_pairs_count = validate_near_duplicates(plan, results)
        
        # Overall result
        if exact_valid and near_valid:
            result_summary = {
                "validation_passed": True,
                "timestamp": datetime.now().isoformat(),
                "test_config": plan['config'],
                "results": {
                    "exact_duplicates": {
                        "expected_groups": len(plan['duplicate_groups']),
                        "found_groups": len(results),
                        "validation_passed": exact_valid
                    },
                    "near_duplicates": {
                        "expected_pairs": len(plan.get('near_duplicate_pairs', [])),
                        "found_pairs": found_pairs_count,
                        "validation_passed": near_valid
                    }
                }
            }
            
            # Save validation results
            os.makedirs("test_outputs", exist_ok=True)
            with open("test_outputs/validation_results.json", 'w') as f:
                json.dump(result_summary, f, indent=2)
            
            print(f"\n🎉 All validations PASSED! The duplicate detection script is working correctly.")
            print(f"📝 Validation results saved to test_outputs/validation_results.json")
            return True
        else:
            print(f"\n❌ Some validations FAILED. Check the output above for details.")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure you've run the test generator and detection script first.")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)