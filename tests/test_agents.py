"""
Tests for agent collaboration and handoff mechanisms.

This module tests that Agent 1 (Contextualization) properly hands off
its analysis to Agent 2 (Extraction) and that the workflow integrates correctly.
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.models import DocumentContext, ContractChangeAnalysis
from src.image_parser import ContractImageParser


class TestAgentHandoff:
    """Test the handoff mechanism between Agent 1 and Agent 2."""
    
    def create_mock_context(self) -> DocumentContext:
        """Create a mock DocumentContext for testing handoff."""
        return DocumentContext(
            original_document_structure={
                "document_type": "Service Agreement",
                "total_sections": 8,
                "section_hierarchy": [
                    {
                        "section_id": "Section 1",
                        "title": "Definitions", 
                        "subsections": ["1.1", "1.2"],
                        "content_summary": "Key definitions"
                    },
                    {
                        "section_id": "Section 2",
                        "title": "Payment Terms",
                        "subsections": ["2.1", "2.2", "2.3"],
                        "content_summary": "Payment schedule and terms"
                    }
                ]
            },
            amendment_document_structure={
                "document_type": "First Amendment",
                "total_sections": 5,
                "section_hierarchy": [
                    {
                        "section_id": "Section 1", 
                        "title": "Definitions",
                        "subsections": ["1.1", "1.2", "1.3"],
                        "content_summary": "Updated definitions"
                    },
                    {
                        "section_id": "Section 2",
                        "title": "Revised Payment Terms", 
                        "subsections": ["2.1", "2.2", "2.3"],
                        "content_summary": "Modified payment schedule"
                    }
                ]
            },
            section_mapping={
                "direct_correspondences": [
                    {
                        "original_section": "Section 1",
                        "amendment_section": "Section 1",
                        "mapping_confidence": 0.95,
                        "notes": "New subsection 1.3 added"
                    },
                    {
                        "original_section": "Section 2", 
                        "amendment_section": "Section 2",
                        "mapping_confidence": 0.90,
                        "notes": "Payment terms modified"
                    }
                ],
                "amendment_only_sections": [
                    {
                        "section_id": "Section 1.3",
                        "classification": "addition",
                        "notes": "New definition for 'Business Hours'"
                    }
                ]
            },
            document_types={
                "original": {
                    "type": "Service Agreement",
                    "category": "Commercial Contract",
                    "execution_date": "2023-01-15"
                },
                "amendment": {
                    "type": "First Amendment", 
                    "category": "Contract Modification",
                    "execution_date": "2023-06-15"
                }
            },
            key_terms_identified=[
                "Service Level Agreement",
                "Payment Terms",
                "Business Hours",
                "Termination",
                "Deliverables"
            ]
        )
    
    @patch('openai.OpenAI')
    def test_agent_1_creates_valid_context(self, mock_openai):
        """Test that Agent 1 produces valid DocumentContext for handoff."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "original_document_structure": {
                "document_type": "Service Agreement",
                "total_sections": 5,
                "section_hierarchy": [{"section_id": "Section 1", "title": "Test"}]
            },
            "amendment_document_structure": {
                "document_type": "Amendment",
                "total_sections": 3,
                "section_hierarchy": [{"section_id": "Section 1", "title": "Test Modified"}]
            },
            "section_mapping": {
                "direct_correspondences": [{
                    "original_section": "Section 1",
                    "amendment_section": "Section 1", 
                    "mapping_confidence": 0.95
                }]
            },
            "document_types": {
                "original": {"type": "contract"},
                "amendment": {"type": "amendment"}
            },
            "key_terms_identified": ["Test Term", "Payment", "Delivery"]
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test Agent 1
        agent1 = ContextualizationAgent(openai_api_key="test_key")
        
        original_text = "This is a test contract with Section 1 containing definitions..."
        amendment_text = "This is an amendment modifying Section 1 definitions..."
        
        context = agent1.contextualize_documents(original_text, amendment_text)
        
        # Verify context structure for handoff
        assert isinstance(context, DocumentContext)
        assert context.original_document_structure is not None
        assert context.amendment_document_structure is not None
        assert context.section_mapping is not None
        assert context.document_types is not None
        assert isinstance(context.key_terms_identified, list)
    
    @patch('openai.OpenAI')
    def test_agent_2_receives_agent_1_output(self, mock_openai):
        """Test that Agent 2 can process Agent 1's DocumentContext output."""
        # Mock OpenAI response for Agent 2
        mock_response = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "sections_changed": [
                "Section 1 - Definitions",
                "Section 2 - Payment Terms"
            ],
            "topics_touched": [
                "Definitions",
                "Payment Terms", 
                "Contract Modifications"
            ],
            "summary_of_the_change": "The amendment adds new definitions and modifies payment terms from Net 30 to Net 45 days. This change provides additional cash flow flexibility for the paying party while extending the service provider's collection timeline.",
            "confidence_score": 0.88
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create Agent 2 and mock context from Agent 1
        agent2 = ExtractionAgent(openai_api_key="test_key")
        context = self.create_mock_context()
        
        original_text = "Original contract text with payment terms Net 30..."
        amendment_text = "Amendment changing payment terms to Net 45..."
        
        # Test Agent 2 processing Agent 1's output
        analysis = agent2.extract_changes(original_text, amendment_text, context)
        
        # Verify Agent 2 used Agent 1's context
        assert isinstance(analysis, ContractChangeAnalysis)
        assert len(analysis.sections_changed) >= 1
        assert len(analysis.topics_touched) >= 1
        assert len(analysis.summary_of_the_change) > 50
        
        # Verify Agent 2 received context information
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        
        # Check that Agent 1's context was included in Agent 2's prompt
        assert "CONTEXTUAL ANALYSIS FROM AGENT 1" in user_message
        assert "Section Mapping" in user_message
        assert "Key Terms Identified" in user_message
    
    def test_context_data_preservation(self):
        """Test that context data is preserved through handoff."""
        context = self.create_mock_context()
        
        # Verify all essential data is present for Agent 2
        assert context.original_document_structure["document_type"] == "Service Agreement"
        assert context.amendment_document_structure["document_type"] == "First Amendment"
        
        # Check section mapping preservation
        mapping = context.section_mapping
        assert "direct_correspondences" in mapping
        assert len(mapping["direct_correspondences"]) == 2
        
        # Check key terms preservation
        assert "Payment Terms" in context.key_terms_identified
        assert "Service Level Agreement" in context.key_terms_identified
        
        # Verify document types
        assert context.document_types["original"]["type"] == "Service Agreement"
        assert context.document_types["amendment"]["type"] == "First Amendment"
    
    def test_handoff_with_empty_context(self):
        """Test handoff behavior when Agent 1 produces minimal context."""
        minimal_context = DocumentContext(
            original_document_structure={},
            amendment_document_structure={},
            section_mapping={},
            document_types={},
            key_terms_identified=[]
        )
        
        # Agent 2 should handle minimal context gracefully
        agent2 = ExtractionAgent(openai_api_key="test_key")
        
        # Mock the extract_changes method to test input handling
        with patch.object(agent2, 'openai_client') as mock_client:
            mock_response = Mock()
            mock_response.choices[0].message.content = json.dumps({
                "sections_changed": ["Document Modified"],
                "topics_touched": ["General Changes"],
                "summary_of_the_change": "Changes detected despite minimal contextual information available for analysis."
            })
            mock_client.chat.completions.create.return_value = mock_response
            
            try:
                analysis = agent2.extract_changes(
                    "test original", "test amendment", minimal_context
                )
                # Should not raise exception and produce valid analysis
                assert isinstance(analysis, ContractChangeAnalysis)
            except Exception as e:
                pytest.fail(f"Agent 2 should handle minimal context gracefully: {e}")
    
    def test_handoff_error_handling(self):
        """Test error handling during agent handoff.""" 
        context = self.create_mock_context()
        
        # Test Agent 2 handling of invalid input
        agent2 = ExtractionAgent(openai_api_key="test_key")
        
        with patch.object(agent2, 'openai_client') as mock_client:
            # Simulate API failure
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                agent2.extract_changes("test", "test", context)
            
            assert "Change extraction failed" in str(exc_info.value)


class TestAgentIntegration:
    """Integration tests for agent collaboration."""
    
    @patch('openai.OpenAI')
    def test_end_to_end_agent_workflow(self, mock_openai):
        """Test complete workflow from Agent 1 → Agent 2."""
        # Mock OpenAI responses
        context_response = Mock()
        context_response.choices[0].message.content = json.dumps({
            "original_document_structure": {
                "document_type": "Service Agreement",
                "section_hierarchy": [{"section_id": "Section 2", "title": "Payment Terms"}]
            },
            "amendment_document_structure": {
                "document_type": "Amendment",
                "section_hierarchy": [{"section_id": "Section 2", "title": "Modified Payment Terms"}]
            },
            "section_mapping": {
                "direct_correspondences": [{
                    "original_section": "Section 2",
                    "amendment_section": "Section 2",
                    "mapping_confidence": 0.95,
                    "notes": "Payment terms changed"
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
            "topics_touched": ["Payment Terms", "Cash Flow"],
            "summary_of_the_change": "Payment terms extended from Net 30 to Net 45 days, improving cash flow for the client while extending collection period for the service provider.",
            "confidence_score": 0.92
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [context_response, extraction_response]
        mock_openai.return_value = mock_client
        
        # Execute workflow
        agent1 = ContextualizationAgent(openai_api_key="test_key")
        agent2 = ExtractionAgent(openai_api_key="test_key")
        
        original_text = "Service Agreement - Section 2: Payment Terms - Net 30 days"
        amendment_text = "First Amendment - Section 2: Modified Payment Terms - Net 45 days"
        
        # Step 1: Agent 1 contextualization
        context = agent1.contextualize_documents(original_text, amendment_text)
        
        # Step 2: Agent 2 extraction using Agent 1's context
        analysis = agent2.extract_changes(original_text, amendment_text, context)
        
        # Verify end-to-end workflow
        assert isinstance(context, DocumentContext)
        assert isinstance(analysis, ContractChangeAnalysis)
        
        # Verify data flow
        assert "Payment Terms" in context.key_terms_identified
        assert "Payment Terms" in analysis.topics_touched
        assert "Section 2" in str(analysis.sections_changed)
        
        # Verify both agents were called
        assert mock_client.chat.completions.create.call_count == 2
    
    def test_agent_validation_integration(self):
        """Test that agent outputs integrate with validation."""
        context = DocumentContext(
            original_document_structure={"type": "contract"},
            amendment_document_structure={"type": "amendment"},
            section_mapping={"mappings": []},
            document_types={"original": {"type": "contract"}},
            key_terms_identified=["Test Term"]
        )
        
        analysis_data = {
            "sections_changed": ["Section 1"],
            "topics_touched": ["Payment Terms"],
            "summary_of_the_change": "Test summary with sufficient length for validation requirements to pass."
        }
        
        # Should integrate without validation errors
        analysis = ContractChangeAnalysis(**analysis_data)
        
        # Verify integration
        assert context.key_terms_identified == ["Test Term"]
        assert analysis.sections_changed == ["Section 1"]
    
    @patch('openai.OpenAI') 
    def test_agent_error_propagation(self, mock_openai):
        """Test that errors propagate correctly through agent chain."""
        # Mock Agent 1 failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Agent 1 failed")
        mock_openai.return_value = mock_client
        
        agent1 = ContextualizationAgent(openai_api_key="test_key")
        
        with pytest.raises(Exception) as exc_info:
            agent1.contextualize_documents("test", "test")
        
        assert "Document contextualization failed" in str(exc_info.value)
    
    def test_agent_data_types(self):
        """Test that agents produce and consume correct data types."""
        # Agent 1 should produce DocumentContext
        context = DocumentContext(
            original_document_structure={"test": "data"},
            amendment_document_structure={"test": "data"},
            section_mapping={"test": "mapping"},
            document_types={"test": "types"}
        )
        
        assert isinstance(context, DocumentContext)
        assert hasattr(context, 'original_document_structure')
        assert hasattr(context, 'amendment_document_structure')
        assert hasattr(context, 'section_mapping')
        assert hasattr(context, 'document_types')
        assert hasattr(context, 'key_terms_identified')
        
        # Agent 2 should produce ContractChangeAnalysis
        analysis = ContractChangeAnalysis(
            sections_changed=["Test Section"],
            topics_touched=["Test Topic"],
            summary_of_the_change="This is a test summary with sufficient content for validation."
        )
        
        assert isinstance(analysis, ContractChangeAnalysis)
        assert hasattr(analysis, 'sections_changed')
        assert hasattr(analysis, 'topics_touched')
        assert hasattr(analysis, 'summary_of_the_change')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])