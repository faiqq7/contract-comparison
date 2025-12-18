"""
Tests for Pydantic validation of contract analysis models.

This module tests that our Pydantic models correctly validate
both valid and invalid outputs from the contract analysis pipeline.
"""

import pytest
from pydantic import ValidationError

from src.models import ContractChangeAnalysis, DocumentContext, ContractComparisonResult


class TestContractChangeAnalysisValidation:
    """Test validation for ContractChangeAnalysis model."""
    
    def test_valid_contract_analysis(self):
        """Test that valid contract analysis data passes validation."""
        valid_data = {
            "sections_changed": [
                "Section 3.1 - Payment Terms",
                "Clause 7.b - Termination Notice Period"
            ],
            "topics_touched": [
                "Payment Terms",
                "Termination",
                "Notice Requirements"
            ],
            "summary_of_the_change": "The amendment extends the payment period from 30 to 45 days and reduces the termination notice requirement from 60 to 30 days. These changes favor the service provider by allowing longer payment cycles while reducing their commitment period through shorter termination notice.",
            "confidence_score": 0.95
        }
        
        # Should not raise any validation errors
        analysis = ContractChangeAnalysis(**valid_data)
        
        assert analysis.sections_changed == valid_data["sections_changed"]
        assert analysis.topics_touched == valid_data["topics_touched"]
        assert analysis.summary_of_the_change == valid_data["summary_of_the_change"]
        assert analysis.confidence_score == valid_data["confidence_score"]
    
    def test_empty_sections_allowed(self):
        """Test that empty sections_changed list is allowed."""
        valid_data = {
            "sections_changed": [],
            "topics_touched": ["General Updates"],
            "summary_of_the_change": "Minor administrative updates with no material changes to contract terms."
        }
        
        analysis = ContractChangeAnalysis(**valid_data)
        assert analysis.sections_changed == []
    
    def test_empty_topics_allowed(self):
        """Test that empty topics_touched list is allowed."""
        valid_data = {
            "sections_changed": ["Section 1 - Definitions"],
            "topics_touched": [],
            "summary_of_the_change": "Updated definition section with clarified terminology."
        }
        
        analysis = ContractChangeAnalysis(**valid_data)
        assert analysis.topics_touched == []
    
    def test_invalid_summary_too_short(self):
        """Test that summary validation fails for too-short summaries."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Updates"],
            "summary_of_the_change": "Short"  # Too short
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "at least 10 characters" in str(exc_info.value)
    
    def test_invalid_summary_too_few_words(self):
        """Test that summary validation fails for too few words."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Updates"], 
            "summary_of_the_change": "One two three four"  # Only 4 words
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "at least 5 words" in str(exc_info.value)
    
    def test_invalid_confidence_score_range(self):
        """Test that confidence score validation enforces 0.0-1.0 range."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Updates"],
            "summary_of_the_change": "This is a valid summary with sufficient length and content.",
            "confidence_score": 1.5  # Invalid - over 1.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "less than or equal to 1" in str(exc_info.value)
    
    def test_invalid_sections_type(self):
        """Test that sections_changed validates type correctly."""
        invalid_data = {
            "sections_changed": "Section 1",  # Should be list, not string
            "topics_touched": ["Updates"],
            "summary_of_the_change": "This is a valid summary with sufficient content for validation testing."
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "list" in str(exc_info.value).lower()
    
    def test_invalid_topics_type(self):
        """Test that topics_touched validates type correctly."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": "Updates",  # Should be list, not string
            "summary_of_the_change": "This is a valid summary with sufficient content for validation testing."
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "list" in str(exc_info.value).lower()
    
    def test_extra_fields_forbidden(self):
        """Test that extra fields are not allowed (Config.extra = 'forbid')."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Updates"],
            "summary_of_the_change": "This is a valid summary with sufficient content for validation testing.",
            "extra_field": "This should not be allowed"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        assert "extra" in str(exc_info.value).lower()
    
    def test_missing_required_fields(self):
        """Test that missing required fields cause validation failure."""
        invalid_data = {
            "sections_changed": ["Section 1"],
            # Missing topics_touched and summary_of_the_change
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ContractChangeAnalysis(**invalid_data)
        
        error_str = str(exc_info.value).lower()
        assert "required" in error_str or "missing" in error_str


class TestDocumentContextValidation:
    """Test validation for DocumentContext model."""
    
    def test_valid_document_context(self):
        """Test that valid document context data passes validation."""
        valid_data = {
            "original_document_structure": {
                "document_type": "Service Agreement",
                "total_sections": 10,
                "section_hierarchy": [
                    {
                        "section_id": "Section 1",
                        "title": "Definitions",
                        "subsections": ["1.1", "1.2"],
                        "content_summary": "Key term definitions"
                    }
                ]
            },
            "amendment_document_structure": {
                "document_type": "First Amendment",
                "total_sections": 5,
                "section_hierarchy": [
                    {
                        "section_id": "Section 1",
                        "title": "Modified Definitions", 
                        "subsections": ["1.1", "1.2", "1.3"],
                        "content_summary": "Updated definitions"
                    }
                ]
            },
            "section_mapping": {
                "direct_correspondences": [
                    {
                        "original_section": "Section 1",
                        "amendment_section": "Section 1",
                        "mapping_confidence": 0.95
                    }
                ]
            },
            "document_types": {
                "original": {"type": "contract", "category": "service"},
                "amendment": {"type": "amendment", "number": 1}
            },
            "key_terms_identified": [
                "Service Level Agreement",
                "Termination",
                "Payment Terms"
            ]
        }
        
        context = DocumentContext(**valid_data)
        
        assert context.original_document_structure == valid_data["original_document_structure"]
        assert context.amendment_document_structure == valid_data["amendment_document_structure"]
        assert context.section_mapping == valid_data["section_mapping"]
        assert context.document_types == valid_data["document_types"]
        assert context.key_terms_identified == valid_data["key_terms_identified"]
    
    def test_empty_key_terms_default(self):
        """Test that key_terms_identified defaults to empty list."""
        minimal_data = {
            "original_document_structure": {"type": "contract"},
            "amendment_document_structure": {"type": "amendment"},
            "section_mapping": {"mappings": []},
            "document_types": {"original": {"type": "contract"}}
        }
        
        context = DocumentContext(**minimal_data)
        assert context.key_terms_identified == []
    
    def test_missing_required_fields(self):
        """Test that missing required fields cause validation failure."""
        invalid_data = {
            "original_document_structure": {"type": "contract"},
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DocumentContext(**invalid_data)
        
        error_str = str(exc_info.value).lower()
        assert "required" in error_str or "missing" in error_str


class TestContractComparisonResultValidation:
    """Test validation for ContractComparisonResult model."""
    
    def test_valid_comparison_result(self):
        """Test that valid comparison result passes validation."""
        context_data = {
            "original_document_structure": {"type": "contract"},
            "amendment_document_structure": {"type": "amendment"},
            "section_mapping": {"mappings": []},
            "document_types": {"original": {"type": "contract"}}
        }
        
        analysis_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Payment Terms"],
            "summary_of_the_change": "This is a comprehensive summary of the changes made to the contract with sufficient detail for validation."
        }
        
        result_data = {
            "context": DocumentContext(**context_data),
            "analysis": ContractChangeAnalysis(**analysis_data),
            "processing_metadata": {
                "session_id": "test_session",
                "duration": 45.2,
                "success": True
            }
        }
        
        result = ContractComparisonResult(**result_data)
        
        assert result.context is not None
        assert result.analysis is not None
        assert result.processing_metadata["session_id"] == "test_session"
    
    def test_missing_required_components(self):
        """Test that missing context or analysis causes validation failure."""
        invalid_data = {
            "context": None,  # This should fail
            "processing_metadata": {}
        }
        
        with pytest.raises(ValidationError):
            ContractComparisonResult(**invalid_data)


class TestValidationIntegration:
    """Integration tests for model validation in realistic scenarios."""
    
    def test_realistic_contract_analysis(self):
        """Test validation with realistic contract analysis data."""
        realistic_data = {
            "sections_changed": [
                "Section 2.3 - Payment Schedule",
                "Section 5.1 - Termination for Convenience", 
                "Section 8.4 - Limitation of Liability",
                "Exhibit A - Statement of Work"
            ],
            "topics_touched": [
                "Payment Terms",
                "Termination Rights",
                "Liability Allocation", 
                "Scope of Work",
                "Risk Management"
            ],
            "summary_of_the_change": """
The First Amendment makes several material changes to the original Service Agreement dated January 15, 2023. 

Key modifications include: (1) Extension of payment terms from Net 30 to Net 45 days, providing additional cash flow relief for the Client; (2) Addition of termination for convenience clause allowing either party to terminate with 90 days written notice; (3) Reduction of liability cap from $500,000 to $250,000, limiting the Service Provider's maximum exposure; and (4) Updated Statement of Work expanding deliverables to include quarterly business reviews.

These changes collectively shift risk allocation toward the Service Provider while providing operational flexibility for both parties. The extended payment terms and reduced liability cap favor the Client, while the termination for convenience clause provides exit flexibility. Legal review recommended for liability cap reduction impact on insurance coverage requirements.
            """.strip(),
            "confidence_score": 0.92,
            "processing_notes": "High-quality document images enabled precise text extraction and analysis"
        }
        
        # Should validate successfully
        analysis = ContractChangeAnalysis(**realistic_data)
        
        assert len(analysis.sections_changed) == 4
        assert len(analysis.topics_touched) == 5
        assert len(analysis.summary_of_the_change) > 500  # Comprehensive summary
        assert 0.9 <= analysis.confidence_score <= 1.0
    
    def test_edge_case_minimal_changes(self):
        """Test validation with minimal change scenario."""
        minimal_data = {
            "sections_changed": ["Administrative Update - Contact Information"],
            "topics_touched": ["Administrative Changes"],
            "summary_of_the_change": "Minor administrative amendment updating contact information for notifications. No material terms affected."
        }
        
        analysis = ContractChangeAnalysis(**minimal_data)
        
        assert len(analysis.sections_changed) == 1
        assert len(analysis.topics_touched) == 1
        assert "administrative" in analysis.summary_of_the_change.lower()
    
    def test_edge_case_no_changes_detected(self):
        """Test validation when no meaningful changes are detected."""
        no_changes_data = {
            "sections_changed": [],
            "topics_touched": [],
            "summary_of_the_change": "Analysis indicates no substantive changes between the original contract and amendment. Documents appear to be duplicates or contain only formatting differences."
        }
        
        analysis = ContractChangeAnalysis(**no_changes_data)
        
        assert analysis.sections_changed == []
        assert analysis.topics_touched == []
        assert "no" in analysis.summary_of_the_change.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])