"""
Agent 1: Document Contextualization Agent

This agent reads both original contract and amendment documents,
analyzes their structure, and creates contextual mappings for change extraction.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
import openai
from langfuse.decorators import observe
from langfuse import Langfuse

from ..models import DocumentContext

# Initialize Langfuse
langfuse = Langfuse()


class ContextualizationAgent:
    """
    Agent responsible for analyzing document structure and creating context for change extraction.
    
    This agent specializes in:
    1. Understanding legal document hierarchy and structure
    2. Mapping corresponding sections between original and amendment
    3. Identifying document types and their relationships
    4. Extracting key legal terms and concepts
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the contextualization agent.
        
        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use for analysis
        """
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for document contextualization.
        
        Returns:
            Comprehensive system prompt for legal document analysis
        """
        return """
You are a senior legal document analyst specializing in contract structure analysis and document comparison preparation. Your role is to analyze legal documents and create comprehensive contextual understanding that enables precise change detection.

CORE RESPONSIBILITIES:
1. **Document Structure Analysis**: Parse legal documents to identify hierarchical organization (sections, subsections, clauses, exhibits)
2. **Section Mapping**: Create precise mappings between corresponding sections in original contracts and amendments
3. **Document Classification**: Identify document types, purposes, and their relationships
4. **Key Term Extraction**: Identify important legal concepts, defined terms, and cross-references

ANALYSIS APPROACH:

For STRUCTURE ANALYSIS:
- Identify section numbering schemes (1.0, 1.1, 1.a, Article I, etc.)
- Map document hierarchy (main sections → subsections → clauses → sub-clauses)
- Note any exhibits, schedules, appendices, or attachments
- Identify headers, footers, signature blocks, and administrative sections
- Recognize table of contents, definitions sections, and cross-references

For SECTION MAPPING:
- Match corresponding sections between original and amendment
- Handle section renumbering or reorganization
- Identify new sections added in amendments
- Note sections that appear in original but not in amendment (potential deletions)
- Map exhibits and schedules between documents

For DOCUMENT CLASSIFICATION:
- Determine document type (contract, amendment, exhibit, schedule)
- Identify contract category (service agreement, purchase order, employment, etc.)
- Understand amendment type (modification, extension, termination, etc.)
- Note execution status (draft, executed, partially executed)

For KEY TERM EXTRACTION:
- Extract defined terms (usually capitalized or in quotes)
- Identify legal concepts (warranties, representations, indemnification, etc.)
- Note important dates, monetary amounts, and performance metrics
- Extract party names, addresses, and key personnel
- Identify governing law, jurisdiction, and dispute resolution mechanisms

ANALYSIS QUALITY STANDARDS:
- Maintain >95% accuracy in section identification
- Provide clear rationale for mapping decisions
- Flag ambiguous or unclear document elements
- Note any quality issues with source documents
- Ensure analysis supports downstream change detection

OUTPUT REQUIREMENTS:
You must provide a structured analysis that includes:
1. Complete document structure breakdown
2. Section-to-section mapping with confidence scores
3. Document classification and relationship analysis
4. Key terms and concepts inventory
5. Quality assessment and processing notes

Focus on precision and completeness - your analysis directly impacts the accuracy of change extraction in the subsequent step.
"""

    def get_analysis_prompt(self, original_text: str, amendment_text: str) -> str:
        """
        Generate specific analysis prompt for the given documents.
        
        Args:
            original_text: Extracted text from original contract
            amendment_text: Extracted text from amendment
            
        Returns:
            Detailed prompt for document analysis
        """
        return f"""
Please analyze these two legal documents and provide a comprehensive structural and contextual analysis:

DOCUMENT 1 - ORIGINAL CONTRACT:
{original_text}

DOCUMENT 2 - AMENDMENT:
{amendment_text}

REQUIRED ANALYSIS:

1. **Document Structure Analysis**:
   - Extract complete hierarchical structure for each document
   - Identify section numbering schemes and organization patterns
   - Map all major sections, subsections, and clauses
   - Note exhibits, schedules, and appendices

2. **Section Mapping**:
   - Create precise mappings between corresponding sections in both documents
   - Identify sections that exist in original but not amendment (potential deletions)
   - Identify sections that exist in amendment but not original (potential additions)
   - Note any section renumbering or reorganization

3. **Document Classification**:
   - Classify each document type and purpose
   - Identify the relationship between documents (amendment to original, supplement, etc.)
   - Note contract category and legal domain

4. **Key Terms Identification**:
   - Extract all defined terms from both documents
   - Identify critical legal concepts and provisions
   - Note important dates, amounts, and performance criteria
   - Extract party information and key personnel

Please format your response as a valid JSON object that matches this structure:
{{
    "original_document_structure": {{
        "document_type": "string",
        "total_sections": "number",
        "section_hierarchy": [
            {{
                "section_id": "Section 1",
                "title": "Definitions",
                "subsections": ["1.1", "1.2"],
                "content_summary": "brief description",
                "page_references": ["page 1", "page 2"]
            }}
        ],
        "exhibits_schedules": ["Exhibit A", "Schedule 1"],
        "numbering_scheme": "description of numbering pattern"
    }},
    "amendment_document_structure": {{
        "document_type": "string",
        "total_sections": "number",
        "section_hierarchy": [
            {{
                "section_id": "Section 1", 
                "title": "Amended Definitions",
                "subsections": ["1.1", "1.2", "1.3"],
                "content_summary": "brief description",
                "page_references": ["page 1"]
            }}
        ],
        "exhibits_schedules": ["Exhibit A-1"],
        "numbering_scheme": "description of numbering pattern"
    }},
    "section_mapping": {{
        "direct_correspondences": [
            {{
                "original_section": "Section 1",
                "amendment_section": "Section 1",
                "mapping_confidence": 0.95,
                "notes": "Direct correspondence with modifications"
            }}
        ],
        "amendment_only_sections": [
            {{
                "section_id": "Section 1.3",
                "classification": "addition",
                "notes": "New subsection not in original"
            }}
        ],
        "original_only_sections": [
            {{
                "section_id": "Section 5",
                "classification": "potential_deletion",
                "notes": "Not referenced in amendment"
            }}
        ]
    }},
    "document_types": {{
        "original": {{
            "type": "Service Agreement",
            "category": "Commercial Contract",
            "status": "Executed",
            "parties": ["Company A", "Company B"],
            "execution_date": "2023-01-01",
            "effective_date": "2023-01-15"
        }},
        "amendment": {{
            "type": "First Amendment",
            "category": "Contract Modification", 
            "status": "Executed",
            "amendment_number": "1",
            "execution_date": "2023-06-01",
            "effective_date": "2023-06-15",
            "references_original": true
        }}
    }},
    "key_terms_identified": [
        "Defined Term 1",
        "Defined Term 2", 
        "Service Level Agreement",
        "Termination",
        "Intellectual Property"
    ]
}}

Ensure your analysis is thorough, accurate, and provides the contextual foundation needed for precise change extraction.
"""

    @observe(name="analyze_document_structure")
    def analyze_document_structure(self, document_text: str, document_type: str) -> Dict:
        """
        Analyze the structure of a single document.
        
        Args:
            document_text: Extracted text from the document
            document_type: Type identifier ("original" or "amendment")
            
        Returns:
            Structured analysis of document hierarchy and components
        """
        try:
            prompt = f"""
Analyze the structure of this {document_type} legal document:

{document_text}

Provide a detailed structural breakdown including:
1. Section hierarchy and numbering
2. Major components (TOC, definitions, exhibits, etc.)
3. Document metadata (type, parties, dates)
4. Key legal provisions identified

Format as JSON with clear section mappings and hierarchy.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Look for JSON content
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = analysis_text[json_start:json_end]
                    return json.loads(json_content)
                else:
                    # Fallback: structure the response manually
                    return {
                        "document_type": document_type,
                        "analysis": analysis_text,
                        "parsing_method": "fallback_text_analysis"
                    }
                    
            except json.JSONDecodeError:
                return {
                    "document_type": document_type,
                    "analysis": analysis_text,
                    "parsing_method": "text_only",
                    "error": "JSON parsing failed"
                }
                
        except Exception as e:
            raise Exception(f"Document structure analysis failed: {str(e)}")

    @observe(name="create_section_mapping")
    def create_section_mapping(
        self,
        original_structure: Dict,
        amendment_structure: Dict,
        original_text: str,
        amendment_text: str
    ) -> Dict:
        """
        Create detailed mapping between sections in original and amendment.
        
        Args:
            original_structure: Structure analysis of original document
            amendment_structure: Structure analysis of amendment
            original_text: Full original document text
            amendment_text: Full amendment document text
            
        Returns:
            Comprehensive section mapping with correspondences and changes
        """
        try:
            mapping_prompt = f"""
Based on these document structures and full texts, create precise section mappings:

ORIGINAL STRUCTURE:
{json.dumps(original_structure, indent=2)}

AMENDMENT STRUCTURE: 
{json.dumps(amendment_structure, indent=2)}

ORIGINAL FULL TEXT (first 2000 chars):
{original_text[:2000]}...

AMENDMENT FULL TEXT (first 2000 chars):
{amendment_text[:2000]}...

Create a comprehensive mapping showing:
1. Direct section correspondences with confidence scores
2. Sections added in amendment
3. Sections potentially removed from original
4. Section renumbering or reorganization
5. Quality assessment of mapping confidence

Format as structured JSON with clear mapping relationships.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": mapping_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            mapping_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                json_start = mapping_text.find('{')
                json_end = mapping_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = mapping_text[json_start:json_end]
                    return json.loads(json_content)
                else:
                    return {"mapping": mapping_text, "parsing_method": "text_fallback"}
                    
            except json.JSONDecodeError:
                return {"mapping": mapping_text, "parsing_method": "raw_text"}
                
        except Exception as e:
            raise Exception(f"Section mapping failed: {str(e)}")

    @observe(name="extract_key_terms")
    def extract_key_terms(self, original_text: str, amendment_text: str) -> List[str]:
        """
        Extract key legal terms and concepts from both documents.
        
        Args:
            original_text: Original contract text
            amendment_text: Amendment text
            
        Returns:
            List of key terms and legal concepts
        """
        try:
            terms_prompt = f"""
Extract key legal terms, defined terms, and important concepts from these documents:

ORIGINAL CONTRACT:
{original_text[:1500]}...

AMENDMENT:
{amendment_text[:1500]}...

Identify:
1. Defined terms (capitalized or quoted terms)
2. Legal concepts (warranties, representations, indemnification, etc.)
3. Important business terms (payment, delivery, performance, etc.)
4. Critical dates, amounts, and metrics
5. Party names and key roles

Return as a JSON array of strings with the most important terms.
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a legal terminology expert. Extract key terms precisely."},
                    {"role": "user", "content": terms_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            terms_text = response.choices[0].message.content
            
            # Try to parse as JSON array
            try:
                # Look for JSON array
                if '[' in terms_text and ']' in terms_text:
                    array_start = terms_text.find('[')
                    array_end = terms_text.rfind(']') + 1
                    json_content = terms_text[array_start:array_end]
                    return json.loads(json_content)
                else:
                    # Fallback: extract terms from text
                    lines = terms_text.split('\n')
                    terms = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('*'):
                            # Remove numbering and bullets
                            clean_line = re.sub(r'^\d+\.\s*', '', line)
                            clean_line = re.sub(r'^[-•]\s*', '', clean_line)
                            if clean_line:
                                terms.append(clean_line)
                    return terms[:20]  # Limit to top 20 terms
                    
            except json.JSONDecodeError:
                # Extract terms using regex patterns
                terms = []
                
                # Common legal term patterns
                patterns = [
                    r'"([^"]+)"',  # Quoted terms
                    r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # Capitalized phrases
                    r'\bSection \d+(?:\.\d+)*',  # Section references
                ]
                
                combined_text = original_text + " " + amendment_text
                for pattern in patterns:
                    matches = re.findall(pattern, combined_text)
                    terms.extend(matches[:10])  # Limit per pattern
                
                return list(set(terms))[:15]  # Remove duplicates and limit
                
        except Exception as e:
            return ["Term extraction failed: " + str(e)]

    @observe(name="contextualize_documents")
    def contextualize_documents(
        self,
        original_text: str,
        amendment_text: str,
        session_id: Optional[str] = None
    ) -> DocumentContext:
        """
        Perform complete contextualization of both documents.
        
        Args:
            original_text: Extracted text from original contract
            amendment_text: Extracted text from amendment
            session_id: Optional session identifier for tracing
            
        Returns:
            DocumentContext model with complete analysis
            
        Raises:
            Exception: If contextualization fails
        """
        try:
            # Set trace metadata
            if session_id:
                langfuse.trace(
                    name="document_contextualization",
                    session_id=session_id,
                    metadata={
                        "agent": "contextualization_agent",
                        "original_text_length": len(original_text),
                        "amendment_text_length": len(amendment_text)
                    }
                )
            
            # Perform comprehensive analysis
            full_prompt = self.get_analysis_prompt(original_text, amendment_text)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse structured response
            try:
                # Extract JSON from response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = analysis_text[json_start:json_end]
                    analysis_data = json.loads(json_content)
                    
                    # Validate required fields
                    required_fields = [
                        'original_document_structure',
                        'amendment_document_structure', 
                        'section_mapping',
                        'document_types'
                    ]
                    
                    for field in required_fields:
                        if field not in analysis_data:
                            analysis_data[field] = {}
                    
                    if 'key_terms_identified' not in analysis_data:
                        analysis_data['key_terms_identified'] = []
                    
                    # Create DocumentContext model
                    context = DocumentContext(
                        original_document_structure=analysis_data['original_document_structure'],
                        amendment_document_structure=analysis_data['amendment_document_structure'],
                        section_mapping=analysis_data['section_mapping'],
                        document_types=analysis_data['document_types'],
                        key_terms_identified=analysis_data['key_terms_identified']
                    )
                    
                    return context
                    
                else:
                    raise ValueError("No valid JSON structure found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: create basic context structure
                print(f"Warning: JSON parsing failed ({e}), using fallback analysis")
                
                # Extract key terms as fallback
                key_terms = self.extract_key_terms(original_text, amendment_text)
                
                context = DocumentContext(
                    original_document_structure={
                        "analysis": "Fallback analysis - full text processed",
                        "text_length": len(original_text),
                        "parsing_method": "text_analysis"
                    },
                    amendment_document_structure={
                        "analysis": "Fallback analysis - full text processed", 
                        "text_length": len(amendment_text),
                        "parsing_method": "text_analysis"
                    },
                    section_mapping={
                        "raw_analysis": analysis_text,
                        "parsing_method": "fallback"
                    },
                    document_types={
                        "original": {"type": "contract", "method": "inferred"},
                        "amendment": {"type": "amendment", "method": "inferred"}
                    },
                    key_terms_identified=key_terms
                )
                
                return context
                
        except Exception as e:
            raise Exception(f"Document contextualization failed: {str(e)}")

    def validate_context(self, context: DocumentContext) -> Tuple[bool, List[str]]:
        """
        Validate the quality and completeness of contextualization.
        
        Args:
            context: DocumentContext to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required structures
        if not context.original_document_structure:
            issues.append("Missing original document structure")
        
        if not context.amendment_document_structure:
            issues.append("Missing amendment document structure")
        
        if not context.section_mapping:
            issues.append("Missing section mapping")
        
        if not context.document_types:
            issues.append("Missing document type classification")
        
        # Check key terms
        if not context.key_terms_identified or len(context.key_terms_identified) == 0:
            issues.append("No key terms identified")
        
        # Quality checks
        if isinstance(context.section_mapping, dict):
            if "parsing_method" in context.section_mapping and context.section_mapping["parsing_method"] == "fallback":
                issues.append("Section mapping used fallback method - may be incomplete")
        
        return len(issues) == 0, issues