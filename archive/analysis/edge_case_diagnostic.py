import pandas as pd
import csv

print("=== EDGE CASES TEST FILE DIAGNOSTIC ===\n")

file_path = 'tests/test_data/edge_cases_test.csv'

# First, let's read the raw file to see the structure
print("1. RAW FILE ANALYSIS:")
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    print("First 15 lines:")
    for i, line in enumerate(lines[:15], 1):
        # Show line with visible special characters
        visible_line = repr(line)[1:-1]  # Remove outer quotes from repr
        print(f"  Line {i:2d}: {visible_line}")
        
        # Count commas to check field count
        comma_count = line.count(',')
        print(f"          Commas: {comma_count}")
        print()

except Exception as e:
    print(f"Error reading raw file: {e}")

print("\n2. CSV PARSING ANALYSIS:")

# Try different parsing approaches
parsing_methods = [
    ("Default pandas", lambda: pd.read_csv(file_path)),
    ("Pandas with quoting", lambda: pd.read_csv(file_path, quoting=csv.QUOTE_ALL)),
    ("Pandas skip bad lines", lambda: pd.read_csv(file_path, on_bad_lines='skip')),
    ("Pandas with error handling", lambda: pd.read_csv(file_path, on_bad_lines='warn')),
]

for method_name, method_func in parsing_methods:
    try:
        print(f"\n{method_name}:")
        df = method_func()
        print(f"  ✅ Success: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)}")
        
        # Check for issues
        if len(df.columns) != 2:
            print(f"  ⚠️  Warning: Expected 2 columns, got {len(df.columns)}")
        
        # Show sample problematic rows
        for idx, row in df.head().iterrows():
            if pd.isna(row.iloc[1]) or len(str(row.iloc[1])) == 0:
                print(f"  ⚠️  Row {idx}: Empty log_message")
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")

print("\n3. SPECIFIC PROBLEM IDENTIFICATION:")

# Manual line-by-line analysis
problems = []
try:
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for line_num, row in enumerate(reader, 1):
            if line_num == 1:  # Header
                continue
                
            # Check for common CSV issues
            if len(row) != 2:
                problems.append(f"Line {line_num}: Expected 2 fields, got {len(row)} - {row}")
            elif len(row) >= 2:
                source, message = row[0], row[1]
                
                # Check for problematic content
                if '\n' in message:
                    problems.append(f"Line {line_num}: Newline in message - {source}")
                if message == 'null':
                    problems.append(f"Line {line_num}: Literal 'null' value - {source}")
                if not message.strip():
                    problems.append(f"Line {line_num}: Empty/whitespace message - {source}")
                    
except Exception as e:
    print(f"Error in manual analysis: {e}")

if problems:
    print("Found problems:")
    for problem in problems[:10]:  # Show first 10 problems
        print(f"  ❌ {problem}")
    if len(problems) > 10:
        print(f"  ... and {len(problems) - 10} more problems")
else:
    print("✅ No obvious CSV parsing problems found")

print("\n4. PROBLEMATIC LINES DETAILED ANALYSIS:")

# Find the specific line that's causing the parsing error
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check lines around where pandas reported the error (line 10)
    problem_lines = [7, 8, 9, 10, 11, 12, 13]  # Lines around the reported issue
    
    for line_num in problem_lines:
        if line_num <= len(lines):
            line = lines[line_num - 1]  # 0-indexed
            print(f"\nLine {line_num}:")
            print(f"  Raw: {repr(line)}")
            print(f"  Commas: {line.count(',')}")
            
            # Try to parse this line manually
            try:
                parts = line.strip().split(',', 1)  # Split on first comma only
                if len(parts) == 2:
                    source, message = parts
                    print(f"  Source: {repr(source)}")
                    print(f"  Message: {repr(message)}")
                else:
                    print(f"  ⚠️  Split resulted in {len(parts)} parts")
            except Exception as e:
                print(f"  ❌ Manual parse error: {e}")

except Exception as e:
    print(f"Error in detailed analysis: {e}")

print("\n5. RECOMMENDATIONS:")
print("Based on analysis, here are the likely issues and fixes:")

recommendations = [
    "✅ Use pandas with on_bad_lines='skip' to ignore problematic rows",
    "✅ Handle 'null' values in the message field properly",
    "✅ Be aware of multiline messages that break CSV structure",
    "✅ Consider using a more robust CSV parser for edge cases",
    "✅ Add data validation to ensure proper CSV formatting"
]

for rec in recommendations:
    print(f"  {rec}")

print("\n6. TESTING CORRECTED PARSING:")

# Test the corrected parsing approach
try:
    df = pd.read_csv(file_path, on_bad_lines='skip')
    print(f"✅ Successfully parsed {len(df)} rows using skip bad lines")
    
    # Show some examples of edge cases that were successfully parsed
    print("\nSuccessfully parsed edge cases:")
    interesting_rows = df[df['source'].isin(['SpecialChars', 'UnicodeTest', 'VeryLongMessage', 'JSONInMessage'])]
    for idx, row in interesting_rows.iterrows():
        print(f"  {row['source']}: {str(row['log_message'])[:50]}...")
        
except Exception as e:
    print(f"❌ Still failing: {e}")