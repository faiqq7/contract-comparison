#!/usr/bin/env python3
"""
Simple execution script for Contract Comparison Agent.

This script provides an easy way to run contract analysis with
common configuration options and helpful output formatting.
"""

import os
import sys
import argparse
from pathlib import Path


def main():
    """Main execution function with user-friendly interface."""
    
    print("🤖 Contract Comparison and Change Extraction Agent")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(
        description="Analyze changes between contract documents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "original",
        help="Path to original contract image"
    )
    
    parser.add_argument(
        "amendment", 
        help="Path to amendment contract image"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)"
    )
    
    parser.add_argument(
        "--output",
        help="Save results to file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed processing information"
    )
    
    args = parser.parse_args()
    
    # Validate input files
    if not Path(args.original).exists():
        print(f"❌ Error: Original contract file not found: {args.original}")
        return 1
    
    if not Path(args.amendment).exists():
        print(f"❌ Error: Amendment file not found: {args.amendment}")
        return 1
    
    # Check environment setup
    required_env_vars = ["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with API keys.")
        return 1
    
    # Import and run main system
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from main import main as run_main
        
        # Prepare arguments for main system
        sys.argv = [
            "main.py",
            "--original", args.original,
            "--amendment", args.amendment,
            "--format", args.format
        ]
        
        if args.output:
            sys.argv.extend(["--output", args.output])
        
        if args.verbose:
            sys.argv.append("--verbose")
        
        # Execute analysis
        print(f"📄 Original Contract: {Path(args.original).name}")
        print(f"📄 Amendment: {Path(args.amendment).name}")
        print(f"📊 Output Format: {args.format}")
        if args.output:
            print(f"📁 Output File: {args.output}")
        print()
        
        return run_main()
        
    except ImportError as e:
        print(f"❌ Error: Failed to import analysis system: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return 1
    
    except Exception as e:
        print(f"❌ Error: Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())