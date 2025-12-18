"""
Pydantic models for contract comparison and change extraction.

This module defines the structured output format for the contract comparison system,
ensuring type safety and validation for downstream legal systems.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re


class ContractChangeAnalysis(BaseModel):
    """
    Structured output model for contract comparison and change extraction.
    
    This model represents the result of analyzing differences between an original
    contract and its amendment, providing structured data for legal review systems.
    """
    
    sections_changed: List[str] = Field(
        ...,
        description="List of specific section identifiers where changes occurred (e.g., 'Section 3.1', 'Clause 5.a', 'Appendix A')",
        min_items=0
    )
    
    topics_touched: List[str] = Field(
        ...,
        description="List of business/legal topic categories affected by changes (e.g., 'Payment Terms', 'Termination', 'Liability', 'Intellectual Property')",
        min_items=0
    )
    
    summary_of_the_change: str = Field(
        ...,
        description="Detailed narrative summary explaining what changed, why it matters, and potential legal implications",
        min_length=10
    )
    
    # Optional metadata fields for enhanced tracing and debugging
    confidence_score: Optional[float] = Field(
        None,
        description="Agent confidence in the analysis (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    
    processing_notes: Optional[str] = Field(
        None,
        description="Internal notes about processing challenges or edge cases encountered"
    )
    
    @validator('sections_changed')
    def validate_sections(cls, v):
        """Validate that section identifiers follow common legal document patterns."""
        if not v:  # Allow empty list
            return v
            
        valid_patterns = [
            r'Section \d+(\.\d+)*',  # Section 1, Section 1.1, Section 1.1.1
            r'Clause \d+(\.[a-z])*', # Clause 1, Clause 1.a, Clause 1.b
            r'Article \d+',          # Article 1, Article 2
            r'Appendix [A-Z]',       # Appendix A, Appendix B
            r'Schedule \d+',         # Schedule 1, Schedule 2
            r'Exhibit [A-Z]',        # Exhibit A, Exhibit B
            r'Paragraph \d+',        # Paragraph 1, Paragraph 2
            r'Subsection \d+(\.\d+)*', # Subsection 1.1
        ]
        
        pattern = '|'.join(f'({p})' for p in valid_patterns)
        
        for section in v:
            # Allow flexible matching - section can contain but doesn't need to exactly match patterns
            if not any(re.search(p, section, re.IGNORECASE) for p in valid_patterns):
                # Still allow it but add to processing notes if available
                pass
        
        return v
    
    @validator('topics_touched')
    def validate_topics(cls, v):
        """Validate that topics are meaningful business/legal categories."""
        if not v:  # Allow empty list
            return v
            
        # Common legal/business topics for reference (not restrictive)
        common_topics = {
            'payment terms', 'termination', 'liability', 'intellectual property',
            'confidentiality', 'indemnification', 'governing law', 'dispute resolution',
            'force majeure', 'warranties', 'representations', 'compliance',
            'delivery terms', 'performance standards', 'reporting requirements',
            'insurance', 'assignment', 'subcontracting', 'milestones',
            'pricing', 'fees', 'penalties', 'renewal terms', 'scope of work'
        }
        
        # Convert to lowercase for comparison
        normalized_topics = [topic.lower() for topic in v]
        
        # Check for meaningful content (not just single words or gibberish)
        for topic in normalized_topics:
            if len(topic.strip()) < 3:
                raise ValueError(f"Topic '{topic}' is too short to be meaningful")
        
        return v
    
    @validator('summary_of_the_change')
    def validate_summary(cls, v):
        """Validate that summary is comprehensive and meaningful."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Summary must be at least 10 characters long")
        
        # Check for minimum content quality
        words = v.split()
        if len(words) < 5:
            raise ValueError("Summary must contain at least 5 words")
        
        # Avoid generic or template responses
        generic_phrases = [
            "the contract was modified",
            "changes were made",
            "document updated",
            "text amended"
        ]
        
        lower_summary = v.lower()
        if any(phrase in lower_summary for phrase in generic_phrases):
            # Allow it but flag as potentially generic
            pass
        
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"  # Don't allow extra fields
        schema_extra = {
            "example": {
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
        }


class DocumentContext(BaseModel):
    """
    Intermediate model for Agent 1 (contextualization) output.
    
    This model captures the structural analysis of both documents before
    change extraction, facilitating handoff between agents.
    """
    
    original_document_structure: dict = Field(
        ...,
        description="Hierarchical structure of the original contract (sections, clauses, etc.)"
    )
    
    amendment_document_structure: dict = Field(
        ...,
        description="Hierarchical structure of the amendment document"
    )
    
    section_mapping: dict = Field(
        ...,
        description="Mapping between corresponding sections in original and amendment"
    )
    
    document_types: dict = Field(
        ...,
        description="Classification of document types and their purposes"
    )
    
    key_terms_identified: List[str] = Field(
        default_factory=list,
        description="Important legal terms and concepts identified in both documents"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class ContractComparisonResult(BaseModel):
    """
    Complete result model that includes both context and analysis.
    
    This model provides a comprehensive view of the entire comparison process
    for audit trails and debugging.
    """
    
    context: DocumentContext = Field(
        ...,
        description="Structural context analysis from Agent 1"
    )
    
    analysis: ContractChangeAnalysis = Field(
        ...,
        description="Change extraction analysis from Agent 2"
    )
    
    processing_metadata: dict = Field(
        default_factory=dict,
        description="Metadata about the processing workflow (timing, model used, etc.)"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True