#!/usr/bin/env python3
"""
Automated lead collection script for Heal at India retreat centres.
Searches all wellness categories across India and exports combined results.
"""

import json
import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration
QUERIES = [
    "yoga retreats",
    "Ayurveda retreats",
    "wellness retreats",
    "spa retreats",
    "Panchakarma centres",
    "naturopathy retreats",
]

LOCATION = "India"
LIMIT_PER_QUERY = 200
OUTPUT_DIR = Path("lead_results")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"✓ Output directory ready: {OUTPUT_DIR}")

def run_query(query, index, total):
    """Run a single lead search query."""
    print(f"\n[{index}/{total}] Searching: '{query}' in {LOCATION}...")
    
    output_file = OUTPUT_DIR / f"{query.replace(' ', '_').lower()}_{TIMESTAMP}.json"
    
    cmd = [
        sys.executable,
        "-m",
        "lead_agent.cli",
        "--query", query,
        "--location", LOCATION,
        "--limit", str(LIMIT_PER_QUERY),
        "--output", str(output_file),
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✓ Completed: {output_file}")
            return str(output_file)
        else:
            print(f"✗ Failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout on query: {query}")
        return None
    except Exception as e:
        print(f"✗ Error running query '{query}': {e}")
        return None

def combine_results(json_files):
    """Combine all JSON results into a single file and CSV."""
    all_leads = []
    
    print("\n\nCombining results...")
    
    for json_file in json_files:
        if not json_file:
            continue
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_leads.extend(data)
                elif isinstance(data, dict) and 'leads' in data:
                    all_leads.extend(data['leads'])
        except Exception as e:
            print(f"Warning: Could not read {json_file}: {e}")
    
    print(f"✓ Total leads collected: {len(all_leads)}")
    
    # Export combined JSON
    combined_json = OUTPUT_DIR / f"all_retreats_combined_{TIMESTAMP}.json"
    with open(combined_json, 'w') as f:
        json.dump(all_leads, f, indent=2)
    print(f"✓ Combined JSON: {combined_json}")
    
    # Export to CSV for Excel
    if all_leads:
        combined_csv = OUTPUT_DIR / f"all_retreats_combined_{TIMESTAMP}.csv"
        
        # Get all possible keys
        all_keys = set()
        for lead in all_leads:
            if isinstance(lead, dict):
                all_keys.update(lead.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(combined_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for lead in all_leads:
                writer.writerow(lead)
        
        print(f"✓ Combined CSV: {combined_csv}")
        return combined_csv
    
    return None

def main():
    """Main execution."""
    print("=" * 60)
    print("HEAL AT INDIA - Automated Retreat Lead Collection")
    print("=" * 60)
    print(f"Queries: {', '.join(QUERIES)}")
    print(f"Location: {LOCATION}")
    print(f"Limit per query: {LIMIT_PER_QUERY}")
    print("=" * 60)
    
    ensure_output_dir()
    
    # Run all queries
    json_files = []
    for i, query in enumerate(QUERIES, 1):
        result_file = run_query(query, i, len(QUERIES))
        json_files.append(result_file)
    
    # Combine results
    csv_file = combine_results(json_files)
    
    print("\n" + "=" * 60)
    print("✓ COMPLETE! Your leads are ready in:")
    print(f"  Directory: {OUTPUT_DIR}")
    print(f"  CSV file: {csv_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
