"""
Integration tests for the complete contract comparison pipeline.

This module tests end-to-end functionality including image parsing,
agent collaboration, and output validation.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import ContractComparisonPipeline
from src.image_parser import ContractImageParser, ImageValidationError
from src.models import ContractComparisonResult
from PIL import Image


class TestImageParsingIntegration:
    """Test image parsing functionality."""
    
    def create_test_image(self, width=800, height=1000) -> str:
        """Create a temporary test image file."""
        # Create a temporary image file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        
        # Create a simple test image
        image = Image.new('RGB', (width, height), color='white')
        image.save(temp_file.name, 'JPEG')
        
        return temp_file.name
    
    def test_image_validation_valid_file(self):
        """Test that valid images pass validation."""
        parser = ContractImageParser(openai_api_key="test_key")
        test_image = self.create_test_image()
        
        try:
            is_valid, message = parser.validate_image(test_image)
            assert is_valid, f"Valid image should pass validation: {message}"
        finally:
            os.unlink(test_image)
    
    def test_image_validation_invalid_format(self):
        """Test that invalid file formats are rejected."""
        parser = ContractImageParser(openai_api_key="test_key")
        
        # Create a text file with wrong extension
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"This is not an image")
        temp_file.close()
        
        try:
            is_valid, message = parser.validate_image(temp_file.name)
            assert not is_valid
            assert "Unsupported format" in message
        finally:
            os.unlink(temp_file.name)
    
    def test_image_validation_nonexistent_file(self):
        """Test that nonexistent files are rejected."""
        parser = ContractImageParser(openai_api_key="test_key")
        
        is_valid, message = parser.validate_image("nonexistent_file.jpg")
        assert not is_valid
        assert "does not exist" in message
    
    def test_image_validation_oversized_file(self):
        """Test that oversized images are rejected.""" 
        parser = ContractImageParser(openai_api_key="test_key")
        
        # Create image that exceeds max dimensions
        test_image = self.create_test_image(width=5000, height=5000)
        
        try:
            is_valid, message = parser.validate_image(test_image)
            assert not is_valid
            assert "too large" in message.lower()
        finally:
            os.unlink(test_image)
    
    @patch('openai.OpenAI')
    def test_gpt4o_parsing_integration(self, mock_openai):
        """Test GPT-4o image parsing integration."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = """
SERVICE AGREEMENT

Section 1. Definitions
1.1 "Services" means the professional services described in Exhibit A.
1.2 "Client" means ABC Corporation.

Section 2. Payment Terms
2.1 Client shall pay Service Provider within thirty (30) days of invoice date.
2.2 Late fees of 1.5% per month apply to overdue amounts.
"""
        mock_response.usage.prompt_tokens = 1500
        mock_response.usage.completion_tokens = 800
        mock_response.usage.total_tokens = 2300
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        parser = ContractImageParser(openai_api_key="test_key")
        test_image = self.create_test_image()
        
        try:
            result = parser.parse_with_gpt4o(test_image, "contract")
            
            assert result["model_used"] == "gpt-4o"
            assert "extracted_text" in result
            assert "SERVICE AGREEMENT" in result["extracted_text"]
            assert "token_usage" in result
            assert result["token_usage"]["total_tokens"] == 2300
            
        finally:
            os.unlink(test_image)
    
    @patch('openai.OpenAI')
    def test_contract_pair_parsing(self, mock_openai):
        """Test parsing of contract pairs."""
        # Mock OpenAI responses
        original_response = Mock()
        original_response.choices[0].message.content = "ORIGINAL CONTRACT - Section 1: Payment Net 30"
        original_response.usage.prompt_tokens = 1000
        original_response.usage.completion_tokens = 500
        original_response.usage.total_tokens = 1500
        
        amendment_response = Mock()
        amendment_response.choices[0].message.content = "AMENDMENT - Section 1: Payment Net 45"
        amendment_response.usage.prompt_tokens = 1100
        amendment_response.usage.completion_tokens = 600
        amendment_response.usage.total_tokens = 1700
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [original_response, amendment_response]
        mock_openai.return_value = mock_client
        
        parser = ContractImageParser(openai_api_key="test_key")
        original_image = self.create_test_image()
        amendment_image = self.create_test_image()
        
        try:
            original_result, amendment_result = parser.parse_contract_pair(
                original_image, amendment_image
            )
            
            assert "ORIGINAL CONTRACT" in original_result["extracted_text"]
            assert "AMENDMENT" in amendment_result["extracted_text"]
            assert original_result["document_type"] == "original"
            assert amendment_result["document_type"] == "amendment"
            
        finally:
            os.unlink(original_image)
            os.unlink(amendment_image)


class TestPipelineIntegration:
    """Test the complete pipeline integration."""
    
    def create_test_image(self) -> str:
        """Create a temporary test image."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image = Image.new('RGB', (800, 1000), color='white')
        image.save(temp_file.name, 'JPEG')
        return temp_file.name
    
    @patch('openai.OpenAI')
    def test_pipeline_initialization(self, mock_openai):
        """Test that pipeline initializes correctly."""
        mock_openai.return_value = Mock()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            pipeline = ContractComparisonPipeline()
            
            assert pipeline.image_parser is not None
            assert pipeline.contextualization_agent is not None
            assert pipeline.extraction_agent is not None
    
    def test_pipeline_input_validation(self):
        """Test pipeline input validation."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            pipeline = ContractComparisonPipeline()
            
            # Test nonexistent files
            is_valid, message = pipeline.validate_inputs("nonexistent1.jpg", "nonexistent2.jpg")
            assert not is_valid
            assert "not found" in message
    
    @patch('openai.OpenAI')
    @patch('langfuse.Langfuse')
    def test_end_to_end_pipeline_flow(self, mock_langfuse, mock_openai):
        """Test complete end-to-end pipeline execution."""
        # Mock Langfuse
        mock_trace = Mock()
        mock_span = Mock()
        mock_trace.span.return_value = mock_span
        mock_langfuse_instance = Mock()
        mock_langfuse_instance.trace.return_value = mock_trace
        mock_langfuse.return_value = mock_langfuse_instance
        
        # Mock OpenAI responses for all stages
        image_response = Mock()
        image_response.choices[0].message.content = "SERVICE AGREEMENT\n\nSection 1. Definitions\nSection 2. Payment Terms - Net 30 days"
        image_response.usage.prompt_tokens = 1000
        image_response.usage.completion_tokens = 500
        image_response.usage.total_tokens = 1500
        
        amendment_response = Mock()
        amendment_response.choices[0].message.content = "FIRST AMENDMENT\n\nSection 1. Definitions (unchanged)\nSection 2. Payment Terms - Net 45 days"
        amendment_response.usage.prompt_tokens = 1100
        amendment_response.usage.completion_tokens = 600
        amendment_response.usage.total_tokens = 1700
        
        context_response = Mock()
        context_response.choices[0].message.content = json.dumps({
            "original_document_structure": {
                "document_type": "Service Agreement",
                "section_hierarchy": [
                    {"section_id": "Section 2", "title": "Payment Terms"}
                ]
            },
            "amendment_document_structure": {
                "document_type": "First Amendment", 
                "section_hierarchy": [
                    {"section_id": "Section 2", "title": "Payment Terms"}
                ]
            },
            "section_mapping": {
                "direct_correspondences": [{
                    "original_section": "Section 2",
                    "amendment_section": "Section 2",
                    "mapping_confidence": 0.95,
                    "notes": "Payment terms modified"
                }]
            },
            "document_types": {
                "original": {"type": "Service Agreement"},
                "amendment": {"type": "First Amendment"}
            },
            "key_terms_identified": ["Payment Terms", "Net 30", "Net 45"]
        })
        
        extraction_response = Mock()
        extraction_response.choices[0].message.content = json.dumps({
            "sections_changed": ["Section 2 - Payment Terms"],
            "topics_touched": ["Payment Terms", "Cash Flow Management"],
            "summary_of_the_change": "The amendment extends payment terms from Net 30 to Net 45 days, providing additional cash flow flexibility for the client while extending the service provider's collection timeline. This change represents a material modification to the commercial terms of the agreement.",
            "confidence_score": 0.92
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            image_response,      # Original image parsing
            amendment_response,  # Amendment image parsing
            context_response,    # Contextualization
            extraction_response  # Change extraction
        ]
        mock_openai.return_value = mock_client
        
        # Set up environment
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_key',
            'LANGFUSE_PUBLIC_KEY': 'test_public',
            'LANGFUSE_SECRET_KEY': 'test_secret'
        }):
            pipeline = ContractComparisonPipeline()
            
            original_image = self.create_test_image()
            amendment_image = self.create_test_image()
            
            try:
                result = pipeline.process_contract_comparison(
                    original_path=original_image,
                    amendment_path=amendment_image,
                    session_id="test_session"
                )
                
                # Verify result structure
                assert isinstance(result, ContractComparisonResult)
                assert result.context is not None
                assert result.analysis is not None
                
                # Verify analysis content
                assert "Section 2 - Payment Terms" in result.analysis.sections_changed
                assert "Payment Terms" in result.analysis.topics_touched
                assert "Net 30" in result.analysis.summary_of_the_change
                assert "Net 45" in result.analysis.summary_of_the_change
                
                # Verify processing metadata
                assert result.processing_metadata["session_id"] == "test_session"
                assert result.processing_metadata["success"] is True
                assert "image_parsing" in result.processing_metadata["steps_completed"]
                assert "agent_1_contextualization" in result.processing_metadata["steps_completed"]
                assert "agent_2_extraction" in result.processing_metadata["steps_completed"]
                
                # Verify all OpenAI calls were made
                assert mock_client.chat.completions.create.call_count == 4
                
            finally:
                os.unlink(original_image)
                os.unlink(amendment_image)
    
    @patch('openai.OpenAI')
    def test_pipeline_error_handling(self, mock_openai):
        """Test pipeline error handling."""
        # Mock API failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            pipeline = ContractComparisonPipeline()
            
            original_image = self.create_test_image()
            amendment_image = self.create_test_image()
            
            try:
                with pytest.raises(Exception):
                    pipeline.process_contract_comparison(
                        original_path=original_image,
                        amendment_path=amendment_image
                    )
            finally:
                os.unlink(original_image)
                os.unlink(amendment_image)
    
    def test_pipeline_output_formatting(self):
        """Test pipeline output formatting."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            pipeline = ContractComparisonPipeline()
            
            # Create mock result
            from src.models import DocumentContext, ContractChangeAnalysis
            
            mock_context = DocumentContext(
                original_document_structure={"type": "contract"},
                amendment_document_structure={"type": "amendment"},
                section_mapping={"mappings": []},
                document_types={"original": {"type": "contract"}}
            )
            
            mock_analysis = ContractChangeAnalysis(
                sections_changed=["Section 1 - Test"],
                topics_touched=["Test Topic"],
                summary_of_the_change="This is a test summary for formatting validation purposes."
            )
            
            mock_result = ContractComparisonResult(
                context=mock_context,
                analysis=mock_analysis,
                processing_metadata={"session_id": "test", "total_duration": 45.2}
            )
            
            # Test JSON formatting
            json_output = pipeline.format_output(mock_result, "json")
            parsed_json = json.loads(json_output)
            
            assert "sections_changed" in parsed_json
            assert "topics_touched" in parsed_json
            assert "summary_of_the_change" in parsed_json
            
            # Test summary formatting
            summary_output = pipeline.format_output(mock_result, "summary")
            
            assert "CONTRACT COMPARISON ANALYSIS" in summary_output
            assert "SECTIONS CHANGED" in summary_output
            assert "TOPICS AFFECTED" in summary_output
            assert "CHANGE SUMMARY" in summary_output


class TestRealWorldScenarios:
    """Test realistic contract comparison scenarios."""
    
    def test_no_changes_scenario(self):
        """Test scenario where no meaningful changes are detected."""
        from src.models import ContractChangeAnalysis
        
        # Should handle "no changes" gracefully
        no_changes = ContractChangeAnalysis(
            sections_changed=[],
            topics_touched=[],
            summary_of_the_change="Analysis indicates no substantive changes between documents. The amendment appears to be administrative in nature with no material modifications to contract terms."
        )
        
        assert len(no_changes.sections_changed) == 0
        assert len(no_changes.topics_touched) == 0
        assert "no" in no_changes.summary_of_the_change.lower()
    
    def test_complex_changes_scenario(self):
        """Test scenario with complex, multi-section changes."""
        from src.models import ContractChangeAnalysis
        
        complex_changes = ContractChangeAnalysis(
            sections_changed=[
                "Section 2.3 - Payment Schedule",
                "Section 4.1 - Service Levels", 
                "Section 7.2 - Termination Rights",
                "Section 9.1 - Liability Limitations",
                "Exhibit A - Statement of Work"
            ],
            topics_touched=[
                "Payment Terms",
                "Performance Standards", 
                "Termination Rights",
                "Risk Allocation",
                "Scope of Work"
            ],
            summary_of_the_change="""
The Second Amendment introduces significant modifications across multiple contract sections. Payment terms are extended from Net 30 to Net 60 days with early payment discounts. Service level requirements are tightened with new penalty structures for non-performance. Termination rights are expanded to include convenience termination with 90-day notice. Liability caps are reduced from $1M to $500K while adding mutual indemnification clauses. The Statement of Work is substantially revised to include additional deliverables and quarterly reviews. These changes collectively shift risk allocation and operational requirements for both parties.
            """.strip()
        )
        
        assert len(complex_changes.sections_changed) == 5
        assert len(complex_changes.topics_touched) == 5
        assert len(complex_changes.summary_of_the_change) > 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])