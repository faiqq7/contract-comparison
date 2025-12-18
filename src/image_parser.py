"""
Multimodal LLM image parsing utilities for contract documents.

This module handles image validation, encoding, and API calls to various
vision-capable LLMs for extracting structured text from contract images.
"""

import base64
import io
import os
import time
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

import openai
from PIL import Image
import requests
from langfuse.decorators import observe
from langfuse import Langfuse

# Initialize Langfuse
langfuse = Langfuse()


class ImageValidationError(Exception):
    """Raised when image validation fails."""
    pass


class VisionAPIError(Exception):
    """Raised when vision API calls fail."""
    pass


class ContractImageParser:
    """
    Handles parsing of contract images using multimodal LLMs.
    
    Supports GPT-4o, Gemini Vision, and Claude Vision APIs for robust
    document text extraction with fallback mechanisms.
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    
    # Maximum image size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum image dimensions
    MAX_DIMENSIONS = (4096, 4096)
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        preferred_model: str = "gpt-4o"
    ):
        """
        Initialize the image parser with API credentials.
        
        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            gemini_api_key: Google Gemini API key (defaults to env var)
            claude_api_key: Anthropic Claude API key (defaults to env var)
            preferred_model: Preferred vision model ('gpt-4o', 'gemini-pro-vision', 'claude-3-vision')
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.claude_api_key = claude_api_key or os.getenv('CLAUDE_API_KEY')
        self.preferred_model = preferred_model
        
        # Initialize OpenAI client
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
    
    def validate_image(self, image_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Validate image file format, size, and dimensions.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            image_path = Path(image_path)
            
            # Check if file exists
            if not image_path.exists():
                return False, f"File does not exist: {image_path}"
            
            # Check file extension
            if image_path.suffix.lower() not in self.SUPPORTED_FORMATS:
                return False, f"Unsupported format: {image_path.suffix}. Supported: {self.SUPPORTED_FORMATS}"
            
            # Check file size
            file_size = image_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                return False, f"File too large: {file_size / 1024 / 1024:.1f}MB. Max: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            
            # Check image dimensions
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    if width > self.MAX_DIMENSIONS[0] or height > self.MAX_DIMENSIONS[1]:
                        return False, f"Image too large: {width}x{height}. Max: {self.MAX_DIMENSIONS[0]}x{self.MAX_DIMENSIONS[1]}"
                    
                    # Check if image is readable
                    img.verify()
            except Exception as e:
                return False, f"Invalid or corrupted image: {str(e)}"
            
            return True, "Image validation passed"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def encode_image_to_base64(self, image_path: Union[str, Path]) -> str:
        """
        Encode image to base64 string for API calls.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ImageValidationError: If image validation fails
        """
        is_valid, error_message = self.validate_image(image_path)
        if not is_valid:
            raise ImageValidationError(error_message)
        
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            raise ImageValidationError(f"Failed to encode image: {str(e)}")
    
    def get_contract_parsing_prompt(self, document_type: str = "contract") -> str:
        """
        Get specialized prompt for contract document parsing.
        
        Args:
            document_type: Type of document ('contract', 'amendment', 'original')
            
        Returns:
            Formatted prompt for vision model
        """
        base_prompt = f"""
You are an expert legal document analyst. Please extract ALL text from this {document_type} image with the following requirements:

EXTRACTION REQUIREMENTS:
1. **Preserve Document Structure**: Maintain the hierarchical organization including:
   - Section numbers and titles (e.g., "Section 1. Definitions")
   - Subsections and clause numbers (e.g., "1.1", "1.a", "1.i")
   - Paragraph breaks and indentation
   - Headers, footers, and page numbers
   - Table structures and formatting

2. **Text Accuracy**: Extract text with >95% accuracy:
   - Include ALL visible text, even if partially obscured
   - Preserve exact wording, capitalization, and punctuation
   - Note any illegible sections as [ILLEGIBLE]
   - Include signature blocks, dates, and notarizations

3. **Legal Document Elements**: Pay special attention to:
   - Defined terms (usually in quotes or capitals)
   - Cross-references to other sections
   - Amendments, modifications, or "strike-through" text
   - Exhibits, schedules, and appendices
   - Legal citations and references

4. **Format Preservation**: Maintain:
   - Numbered and bulleted lists
   - Table of contents structure
   - Indentation levels for nested clauses
   - Bold, italic, or underlined emphasis (note as [BOLD], [ITALIC], [UNDERLINE])

5. **Quality Indicators**: If the image quality affects reading:
   - Note areas of concern: [BLURRY], [FADED], [CROPPED]
   - Provide best-effort transcription with confidence notes
   - Flag potential OCR errors or ambiguous text

OUTPUT FORMAT: Provide the complete extracted text in a structured, readable format that preserves the legal document's organization and hierarchy.
"""
        
        if document_type == "amendment":
            base_prompt += """

AMENDMENT-SPECIFIC INSTRUCTIONS:
- Pay extra attention to strikethrough text (deletions)
- Clearly identify new additions or insertions
- Note any "redline" or "track changes" formatting
- Identify which sections reference the original contract
"""
        
        return base_prompt.strip()
    
    @observe(name="parse_image_gpt4o")
    def parse_with_gpt4o(self, image_path: Union[str, Path], document_type: str = "contract") -> Dict:
        """
        Parse image using GPT-4o vision model.
        
        Args:
            image_path: Path to the image file
            document_type: Type of document for specialized prompting
            
        Returns:
            Dictionary with extracted text and metadata
            
        Raises:
            VisionAPIError: If API call fails
        """
        if not self.openai_client:
            raise VisionAPIError("OpenAI API key not provided")
        
        try:
            # Encode image
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prepare prompt
            prompt = self.get_contract_parsing_prompt(document_type)
            
            # Make API call
            start_time = time.time()
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.1  # Low temperature for consistent text extraction
            )
            
            processing_time = time.time() - start_time
            
            # Extract result
            extracted_text = response.choices[0].message.content
            
            return {
                "extracted_text": extracted_text,
                "model_used": "gpt-4o",
                "processing_time": processing_time,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "image_path": str(image_path),
                "document_type": document_type
            }
            
        except Exception as e:
            raise VisionAPIError(f"GPT-4o parsing failed: {str(e)}")
    
    @observe(name="parse_image_with_fallback")
    def parse_image(
        self,
        image_path: Union[str, Path],
        document_type: str = "contract",
        max_retries: int = 3
    ) -> Dict:
        """
        Parse image with automatic fallback between available models.
        
        Args:
            image_path: Path to the image file
            document_type: Type of document for specialized prompting
            max_retries: Maximum retry attempts per model
            
        Returns:
            Dictionary with extracted text and metadata
            
        Raises:
            VisionAPIError: If all models fail
        """
        # Define model priority order
        models_to_try = []
        
        if self.preferred_model == "gpt-4o" and self.openai_client:
            models_to_try.append("gpt-4o")
        
        # Add other available models as fallbacks
        if self.openai_client and "gpt-4o" not in models_to_try:
            models_to_try.append("gpt-4o")
        
        errors = []
        
        for model in models_to_try:
            for attempt in range(max_retries):
                try:
                    if model == "gpt-4o":
                        return self.parse_with_gpt4o(image_path, document_type)
                    
                    # Placeholder for other models (Gemini, Claude)
                    # These would be implemented similarly with their respective APIs
                    
                except VisionAPIError as e:
                    error_msg = f"{model} attempt {attempt + 1}/{max_retries}: {str(e)}"
                    errors.append(error_msg)
                    
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                except Exception as e:
                    error_msg = f"{model} unexpected error: {str(e)}"
                    errors.append(error_msg)
                    break
        
        # If all models failed
        raise VisionAPIError(f"All vision models failed. Errors: {'; '.join(errors)}")
    
    @observe(name="parse_contract_pair")
    def parse_contract_pair(
        self,
        original_path: Union[str, Path],
        amendment_path: Union[str, Path]
    ) -> Tuple[Dict, Dict]:
        """
        Parse both original contract and amendment images.
        
        Args:
            original_path: Path to original contract image
            amendment_path: Path to amendment contract image
            
        Returns:
            Tuple of (original_result, amendment_result) dictionaries
            
        Raises:
            VisionAPIError: If parsing fails for either document
        """
        try:
            # Parse original contract
            langfuse.trace(
                name="parse_original_contract",
                input={"image_path": str(original_path)}
            )
            original_result = self.parse_image(original_path, "original")
            
            # Parse amendment
            langfuse.trace(
                name="parse_amendment_contract", 
                input={"image_path": str(amendment_path)}
            )
            amendment_result = self.parse_image(amendment_path, "amendment")
            
            return original_result, amendment_result
            
        except Exception as e:
            raise VisionAPIError(f"Contract pair parsing failed: {str(e)}")
    
    def batch_parse_contracts(
        self,
        contract_pairs: List[Tuple[str, str]]
    ) -> List[Tuple[Dict, Dict]]:
        """
        Parse multiple contract pairs in batch.
        
        Args:
            contract_pairs: List of (original_path, amendment_path) tuples
            
        Returns:
            List of (original_result, amendment_result) tuples
        """
        results = []
        
        for i, (original_path, amendment_path) in enumerate(contract_pairs):
            try:
                with langfuse.trace(
                    name="batch_parse_contract_pair",
                    metadata={"pair_index": i, "total_pairs": len(contract_pairs)}
                ):
                    result = self.parse_contract_pair(original_path, amendment_path)
                    results.append(result)
                    
            except VisionAPIError as e:
                print(f"Warning: Failed to parse contract pair {i}: {str(e)}")
                results.append((None, None))
        
        return results