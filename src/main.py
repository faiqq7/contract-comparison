#!/usr/bin/env python3
"""
Autonomous Contract Comparison and Change Extraction Agent

Main application orchestrating the complete workflow:
1. Parse contract images using multimodal LLMs
2. Execute Agent 1 (Contextualization)
3. Execute Agent 2 (Change Extraction)  
4. Validate output with Pydantic
5. Return structured JSON results

Usage:
    python src/main.py --original path/to/original.jpg --amendment path/to/amendment.jpg
"""

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe

from src.image_parser import ContractImageParser, ImageValidationError, VisionAPIError
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.models import ContractChangeAnalysis, ContractComparisonResult, DocumentContext

# Load environment variables
load_dotenv()

# Initialize Langfuse
langfuse = Langfuse()


class ContractComparisonPipeline:
    """
    Main pipeline orchestrating the complete contract comparison workflow.
    
    Integrates image parsing, contextual analysis, and change extraction
    with comprehensive tracing and validation.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        langfuse_public_key: Optional[str] = None,
        langfuse_secret_key: Optional[str] = None,
        langfuse_host: Optional[str] = None
    ):
        """
        Initialize the contract comparison pipeline.
        
        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            langfuse_public_key: Langfuse public key (defaults to env var)
            langfuse_secret_key: Langfuse secret key (defaults to env var)  
            langfuse_host: Langfuse host URL (defaults to env var)
        """
        # Set up API keys
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize Langfuse with credentials
        self.langfuse = Langfuse(
            public_key=langfuse_public_key or os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=langfuse_secret_key or os.getenv('LANGFUSE_SECRET_KEY'),
            host=langfuse_host or os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        )
        
        # Initialize components
        self.image_parser = ContractImageParser(
            openai_api_key=self.openai_api_key,
            preferred_model="gpt-4o"
        )
        
        self.contextualization_agent = ContextualizationAgent(
            openai_api_key=self.openai_api_key,
            model="gpt-4"
        )
        
        self.extraction_agent = ExtractionAgent(
            openai_api_key=self.openai_api_key,
            model="gpt-4"
        )
        
    def validate_inputs(self, original_path: str, amendment_path: str) -> Tuple[bool, str]:
        """
        Validate input file paths and image quality.
        
        Args:
            original_path: Path to original contract image
            amendment_path: Path to amendment contract image
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if files exist
        if not Path(original_path).exists():
            return False, f"Original contract file not found: {original_path}"
        
        if not Path(amendment_path).exists():
            return False, f"Amendment file not found: {amendment_path}"
        
        # Validate image formats and quality
        is_valid, error_msg = self.image_parser.validate_image(original_path)
        if not is_valid:
            return False, f"Original contract validation failed: {error_msg}"
        
        is_valid, error_msg = self.image_parser.validate_image(amendment_path)
        if not is_valid:
            return False, f"Amendment validation failed: {error_msg}"
        
        return True, "Input validation passed"
    
    @observe(name="contract_comparison_pipeline")
    def process_contract_comparison(
        self,
        original_path: str,
        amendment_path: str,
        session_id: Optional[str] = None,
        contract_id: Optional[str] = None
    ) -> ContractComparisonResult:
        """
        Execute the complete contract comparison pipeline.
        
        Args:
            original_path: Path to original contract image
            amendment_path: Path to amendment contract image
            session_id: Optional session identifier for tracing
            contract_id: Optional contract identifier for metadata
            
        Returns:
            ContractComparisonResult with complete analysis
            
        Raises:
            Exception: If any step in the pipeline fails
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"contract_comparison_{uuid.uuid4().hex[:8]}"
        
        if not contract_id:
            contract_id = f"contract_{int(time.time())}"
        
        # Initialize trace
        trace = self.langfuse.trace(
            name="contract_comparison_workflow",
            session_id=session_id,
            metadata={
                "contract_id": contract_id,
                "original_file": Path(original_path).name,
                "amendment_file": Path(amendment_path).name,
                "pipeline_version": "1.0.0"
            }
        )
        
        processing_metadata = {
            "session_id": session_id,
            "contract_id": contract_id,
            "start_time": time.time(),
            "steps_completed": [],
            "model_usage": {}
        }
        
        try:
            # Step 1: Validate inputs
            trace.span(
                name="input_validation",
                input={"original_path": original_path, "amendment_path": amendment_path}
            )
            
            is_valid, validation_message = self.validate_inputs(original_path, amendment_path)
            if not is_valid:
                raise ValueError(f"Input validation failed: {validation_message}")
            
            processing_metadata["steps_completed"].append("input_validation")
            
            # Step 2: Parse images with multimodal LLM
            parse_span = trace.span(
                name="image_parsing",
                input={
                    "original_image": str(original_path),
                    "amendment_image": str(amendment_path)
                }
            )
            
            print(f"🔍 Parsing contract images using GPT-4o...")
            original_result, amendment_result = self.image_parser.parse_contract_pair(
                original_path, amendment_path
            )
            
            parse_span.update(
                output={
                    "original_text_length": len(original_result["extracted_text"]),
                    "amendment_text_length": len(amendment_result["extracted_text"]),
                    "model_used": original_result["model_used"],
                    "processing_time": original_result["processing_time"] + amendment_result["processing_time"]
                }
            )
            
            processing_metadata["steps_completed"].append("image_parsing")
            processing_metadata["model_usage"]["image_parsing"] = {
                "model": original_result["model_used"],
                "total_tokens": original_result["token_usage"]["total_tokens"] + amendment_result["token_usage"]["total_tokens"]
            }
            
            # Step 3: Agent 1 - Document Contextualization
            context_span = trace.span(
                name="agent_1_contextualization",
                input={
                    "original_text_length": len(original_result["extracted_text"]),
                    "amendment_text_length": len(amendment_result["extracted_text"])
                }
            )
            
            print(f"🧠 Agent 1: Analyzing document structure and context...")
            context = self.contextualization_agent.contextualize_documents(
                original_result["extracted_text"],
                amendment_result["extracted_text"],
                session_id=session_id
            )
            
            # Validate context quality
            is_valid_context, context_issues = self.contextualization_agent.validate_context(context)
            if context_issues:
                print(f"⚠️  Context validation issues: {', '.join(context_issues)}")
            
            context_span.update(
                output={
                    "sections_mapped": len(context.section_mapping) if isinstance(context.section_mapping, dict) else 0,
                    "key_terms_count": len(context.key_terms_identified),
                    "validation_issues": context_issues
                }
            )
            
            processing_metadata["steps_completed"].append("agent_1_contextualization")
            
            # Step 4: Agent 2 - Change Extraction  
            extraction_span = trace.span(
                name="agent_2_extraction",
                input={
                    "context_quality": is_valid_context,
                    "sections_to_analyze": len(context.section_mapping) if isinstance(context.section_mapping, dict) else 0
                }
            )
            
            print(f"🔎 Agent 2: Extracting and analyzing changes...")
            analysis = self.extraction_agent.extract_changes(
                original_result["extracted_text"],
                amendment_result["extracted_text"],
                context,
                session_id=session_id
            )
            
            # Validate extraction quality
            is_valid_analysis, analysis_issues = self.extraction_agent.validate_extraction(analysis)
            if analysis_issues:
                print(f"⚠️  Analysis validation issues: {', '.join(analysis_issues)}")
            
            extraction_span.update(
                output={
                    "sections_changed_count": len(analysis.sections_changed),
                    "topics_touched_count": len(analysis.topics_touched),
                    "summary_length": len(analysis.summary_of_the_change),
                    "confidence_score": analysis.confidence_score,
                    "validation_issues": analysis_issues
                }
            )
            
            processing_metadata["steps_completed"].append("agent_2_extraction")
            
            # Step 5: Pydantic Validation
            validation_span = trace.span(
                name="pydantic_validation",
                input={"analysis_type": "ContractChangeAnalysis"}
            )
            
            print(f"✅ Validating structured output...")
            # Analysis is already validated through Pydantic in extract_changes()
            # Additional validation if needed
            try:
                validated_analysis = ContractChangeAnalysis.model_validate(analysis.model_dump())
                validation_span.update(output={"validation_status": "passed"})
            except Exception as e:
                validation_span.update(output={"validation_status": "failed", "error": str(e)})
                raise ValueError(f"Pydantic validation failed: {str(e)}")
            
            processing_metadata["steps_completed"].append("pydantic_validation")
            
            # Complete processing metadata
            processing_metadata["end_time"] = time.time()
            processing_metadata["total_duration"] = processing_metadata["end_time"] - processing_metadata["start_time"]
            processing_metadata["success"] = True
            
            # Create complete result
            result = ContractComparisonResult(
                context=context,
                analysis=validated_analysis,
                processing_metadata=processing_metadata
            )
            
            # Update final trace
            trace.update(
                output={
                    "sections_changed": len(validated_analysis.sections_changed),
                    "topics_touched": len(validated_analysis.topics_touched),
                    "processing_duration": processing_metadata["total_duration"],
                    "steps_completed": processing_metadata["steps_completed"]
                }
            )
            
            print(f"🎉 Contract comparison completed successfully!")
            print(f"   📊 Found changes in {len(validated_analysis.sections_changed)} sections")
            print(f"   📋 Identified {len(validated_analysis.topics_touched)} topic areas")
            print(f"   ⏱️  Total processing time: {processing_metadata['total_duration']:.2f} seconds")
            
            return result
            
        except Exception as e:
            # Update trace with error
            trace.update(
                output={
                    "error": str(e),
                    "steps_completed": processing_metadata["steps_completed"],
                    "success": False
                }
            )
            
            processing_metadata["error"] = str(e)
            processing_metadata["success"] = False
            processing_metadata["end_time"] = time.time()
            
            print(f"❌ Contract comparison failed: {str(e)}")
            raise

    def format_output(self, result: ContractComparisonResult, format_type: str = "json") -> str:
        """
        Format the comparison result for output.
        
        Args:
            result: ContractComparisonResult to format
            format_type: Output format ("json", "summary")
            
        Returns:
            Formatted output string
        """
        if format_type == "json":
            return json.dumps({
                "sections_changed": result.analysis.sections_changed,
                "topics_touched": result.analysis.topics_touched, 
                "summary_of_the_change": result.analysis.summary_of_the_change,
                "confidence_score": result.analysis.confidence_score,
                "processing_metadata": {
                    "session_id": result.processing_metadata.get("session_id"),
                    "total_duration": result.processing_metadata.get("total_duration"),
                    "steps_completed": result.processing_metadata.get("steps_completed")
                }
            }, indent=2)
        
        elif format_type == "summary":
            return f"""
CONTRACT COMPARISON ANALYSIS
============================

📋 SECTIONS CHANGED ({len(result.analysis.sections_changed)}):
{chr(10).join(f"  • {section}" for section in result.analysis.sections_changed)}

🏷️  TOPICS AFFECTED ({len(result.analysis.topics_touched)}):
{chr(10).join(f"  • {topic}" for topic in result.analysis.topics_touched)}

📝 CHANGE SUMMARY:
{result.analysis.summary_of_the_change}

📊 ANALYSIS METADATA:
  • Confidence Score: {result.analysis.confidence_score:.2%}
  • Processing Time: {result.processing_metadata.get('total_duration', 0):.2f}s
  • Session ID: {result.processing_metadata.get('session_id', 'N/A')}
"""
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(
        description="Autonomous Contract Comparison and Change Extraction Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --original data/original_contract.jpg --amendment data/amendment.jpg
  python src/main.py --original contract1.png --amendment contract2.png --format summary
  python src/main.py --original doc1.jpg --amendment doc2.jpg --session my_session_123
        """
    )
    
    parser.add_argument(
        "--original",
        required=True,
        help="Path to original contract image file"
    )
    
    parser.add_argument(
        "--amendment", 
        required=True,
        help="Path to amendment contract image file"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--session",
        help="Optional session ID for tracing"
    )
    
    parser.add_argument(
        "--output",
        help="Optional output file path (prints to stdout if not specified)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        if args.verbose:
            print(f"🚀 Initializing Contract Comparison Pipeline...")
            print(f"   📄 Original: {args.original}")
            print(f"   📄 Amendment: {args.amendment}")
        
        pipeline = ContractComparisonPipeline()
        
        # Execute comparison
        result = pipeline.process_contract_comparison(
            original_path=args.original,
            amendment_path=args.amendment,
            session_id=args.session
        )
        
        # Format output
        formatted_output = pipeline.format_output(result, args.format)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(formatted_output)
            print(f"📁 Results saved to: {args.output}")
        else:
            print(formatted_output)
        
        # Return success
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())