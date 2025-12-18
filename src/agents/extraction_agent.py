"""
Agent 2: Change Extraction Agent

This agent receives contextual analysis from Agent 1 and performs precise
extraction of changes between original contract and amendment documents.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
import openai
from langfuse.decorators import observe
from langfuse import Langfuse

from ..models import DocumentContext, ContractChangeAnalysis

# Initialize Langfuse
langfuse = Langfuse()


class ExtractionAgent:
    """
    Agent responsible for extracting and analyzing specific changes between documents.
    
    This agent specializes in:
    1. Identifying precise textual changes using contextual analysis
    2. Classifying changes by type (addition, deletion, modification)
    3. Categorizing changes by business/legal topics
    4. Generating comprehensive change summaries with legal implications
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the extraction agent.
        
        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            model: OpenAI model to use for extraction
        """
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for change extraction.
        
        Returns:
            Comprehensive system prompt for legal change analysis
        """
        return """
You are an expert legal change analyst specializing in contract comparison and amendment analysis. Your role is to extract precise, meaningful changes between original contracts and amendments using contextual document analysis.

CORE RESPONSIBILITIES:
1. **Change Identification**: Detect all modifications, additions, and deletions between documents
2. **Change Classification**: Categorize changes by type and business impact
3. **Topic Analysis**: Group changes by legal/business domains (payment, termination, liability, etc.)
4. **Impact Assessment**: Analyze legal and business implications of identified changes

ANALYSIS METHODOLOGY:

For CHANGE IDENTIFICATION:
- Use provided document context and section mappings to focus analysis
- Compare corresponding sections identified by contextualization agent
- Detect additions: text in amendment not in original
- Detect deletions: text in original not referenced in amendment
- Detect modifications: text changes, rephrasing, or substitutions
- Account for section renumbering and reorganization

For CHANGE CLASSIFICATION:
- **Material Changes**: Affect core business terms (pricing, scope, duration, termination)
- **Administrative Changes**: Updates to addresses, contacts, formatting
- **Legal Changes**: Modify warranties, representations, liability, governing law
- **Operational Changes**: Alter performance requirements, delivery terms, reporting

For TOPIC CATEGORIZATION:
Use standardized business/legal categories:
- Payment Terms, Pricing, Financial Obligations
- Scope of Work, Deliverables, Performance Standards  
- Termination, Renewal, Duration
- Liability, Indemnification, Risk Allocation
- Intellectual Property, Confidentiality
- Compliance, Regulatory Requirements
- Dispute Resolution, Governing Law
- Insurance, Warranties, Representations
- Reporting, Communication, Notice Requirements

For IMPACT ASSESSMENT:
- Analyze who benefits from each change (which party gains advantage)
- Assess risk implications (increased/decreased exposure)
- Identify potential compliance or legal concerns
- Note changes that may require additional review or approval

QUALITY STANDARDS:
- Maintain >95% accuracy in change detection
- Provide specific section references for all changes
- Include exact text quotes for material changes
- Explain legal/business significance of each change
- Flag any ambiguous or unclear modifications

ANALYSIS CONSTRAINTS:
- Focus only on substantive changes, not formatting differences
- Distinguish between actual changes and text extraction variations
- Account for legal document conventions and standard language
- Consider context when evaluating significance of changes

Your analysis directly impacts legal decision-making and contract risk assessment. Prioritize precision, completeness, and clear business relevance.
"""

    def get_extraction_prompt(
        self,
        original_text: str,
        amendment_text: str,
        context: DocumentContext
    ) -> str:
        """
        Generate specific extraction prompt using contextual analysis.
        
        Args:
            original_text: Original contract text
            amendment_text: Amendment text  
            context: Contextual analysis from Agent 1
            
        Returns:
            Detailed prompt for change extraction
        """
        return f"""
Using the contextual analysis provided, extract and analyze all changes between these contract documents:

ORIGINAL CONTRACT TEXT:
{original_text}

AMENDMENT TEXT:
{amendment_text}

CONTEXTUAL ANALYSIS FROM AGENT 1:
Document Structures:
- Original: {json.dumps(context.original_document_structure, indent=2)[:1000]}...
- Amendment: {json.dumps(context.amendment_document_structure, indent=2)[:1000]}...

Section Mapping:
{json.dumps(context.section_mapping, indent=2)[:1500]}...

Key Terms Identified:
{context.key_terms_identified}

Document Types:
{json.dumps(context.document_types, indent=2)}

EXTRACTION REQUIREMENTS:

1. **Sections Changed**: Identify all specific sections where changes occurred
   - Use section identifiers from the contextual mapping
   - Include both original and amendment section references where applicable
   - Format as clear section identifiers (e.g., "Section 3.1 - Payment Terms")

2. **Topics Touched**: Categorize changes by business/legal domains
   - Use standardized legal/business categories
   - Focus on substantive business impact areas
   - Examples: "Payment Terms", "Termination", "Liability", "Intellectual Property"

3. **Summary of Changes**: Provide comprehensive analysis including:
   - What specifically changed (additions, deletions, modifications)
   - Why the changes matter (business and legal implications)
   - Which party benefits from each change
   - Risk implications and potential concerns
   - Overall impact on contract terms and relationship

ANALYSIS APPROACH:
- Use the section mapping to focus on corresponding areas
- Pay special attention to sections marked as "direct_correspondences" with modifications
- Investigate "amendment_only_sections" for new additions
- Consider "original_only_sections" for potential deletions or omissions
- Reference key terms to understand context of changes

QUALITY REQUIREMENTS:
- Include specific text quotes for material changes
- Provide section references for each change identified
- Explain legal and business significance
- Distinguish between substantive changes and administrative updates
- Account for document quality issues noted in context

Format your response as a valid JSON object matching this structure:
{{
    "sections_changed": [
        "Section 3.1 - Payment Terms",
        "Clause 7.b - Termination Notice Period",
        "Appendix A - Service Level Requirements"
    ],
    "topics_touched": [
        "Payment Terms",
        "Termination", 
        "Performance Standards",
        "Notice Requirements"
    ],
    "summary_of_the_change": "Detailed analysis of what changed, business implications, legal significance, risk assessment, and overall impact. Include specific examples and quotes where relevant.",
    "confidence_score": 0.95,
    "processing_notes": "Any challenges or quality concerns in analysis"
}}

Ensure your analysis is thorough, accurate, and provides actionable insights for legal review and decision-making.
"""

    @observe(name="analyze_change_patterns")
    def analyze_change_patterns(
        self,
        original_text: str,
        amendment_text: str,
        section_mapping: Dict
    ) -> Dict:
        """
        Analyze patterns of changes between documents using section mapping.
        
        Args:
            original_text: Original contract text
            amendment_text: Amendment text
            section_mapping: Section correspondence mapping from context
            
        Returns:
            Dictionary of change patterns and locations
        """
        try:
            patterns = {
                "additions": [],
                "deletions": [],
                "modifications": [],
                "section_changes": []
            }
            
            # Analyze direct correspondences for modifications
            if isinstance(section_mapping, dict) and "direct_correspondences" in section_mapping:
                for correspondence in section_mapping["direct_correspondences"]:
                    if correspondence.get("mapping_confidence", 0) > 0.7:
                        patterns["modifications"].append({
                            "section": correspondence.get("original_section", "Unknown"),
                            "confidence": correspondence.get("mapping_confidence", 0),
                            "notes": correspondence.get("notes", "")
                        })
            
            # Identify additions from amendment-only sections
            if isinstance(section_mapping, dict) and "amendment_only_sections" in section_mapping:
                for section in section_mapping["amendment_only_sections"]:
                    patterns["additions"].append({
                        "section": section.get("section_id", "Unknown"),
                        "type": section.get("classification", "addition"),
                        "notes": section.get("notes", "")
                    })
            
            # Identify potential deletions from original-only sections
            if isinstance(section_mapping, dict) and "original_only_sections" in section_mapping:
                for section in section_mapping["original_only_sections"]:
                    patterns["deletions"].append({
                        "section": section.get("section_id", "Unknown"),
                        "type": section.get("classification", "potential_deletion"),
                        "notes": section.get("notes", "")
                    })
            
            return patterns
            
        except Exception as e:
            return {
                "error": f"Change pattern analysis failed: {str(e)}",
                "fallback_analysis": "Manual text comparison required"
            }

    @observe(name="categorize_legal_topics")
    def categorize_legal_topics(
        self,
        changes_identified: List[str],
        key_terms: List[str],
        original_text: str,
        amendment_text: str
    ) -> List[str]:
        """
        Categorize changes by legal and business topics.
        
        Args:
            changes_identified: List of sections where changes occurred
            key_terms: Key legal terms from context
            original_text: Original contract text
            amendment_text: Amendment text
            
        Returns:
            List of categorized legal/business topics
        """
        try:
            # Standard legal topic categories
            topic_keywords = {
                "Payment Terms": ["payment", "pay", "invoice", "billing", "fee", "cost", "price", "amount"],
                "Termination": ["terminate", "termination", "end", "expire", "expiry", "cancel"],
                "Liability": ["liable", "liability", "responsible", "responsibility", "damages", "harm"],
                "Intellectual Property": ["intellectual property", "ip", "copyright", "trademark", "patent", "proprietary"],
                "Confidentiality": ["confidential", "confidentiality", "non-disclosure", "nda", "proprietary"],
                "Performance Standards": ["performance", "standards", "service level", "sla", "deliverables", "quality"],
                "Indemnification": ["indemnify", "indemnification", "hold harmless", "defend"],
                "Governing Law": ["governing law", "jurisdiction", "applicable law", "laws of"],
                "Dispute Resolution": ["dispute", "arbitration", "mediation", "court", "litigation"],
                "Insurance": ["insurance", "coverage", "policy", "insured", "insurer"],
                "Warranties": ["warrant", "warranty", "warranties", "represent", "representation"],
                "Compliance": ["comply", "compliance", "regulation", "regulatory", "legal requirement"],
                "Assignment": ["assign", "assignment", "transfer", "delegate"],
                "Force Majeure": ["force majeure", "act of god", "unforeseeable", "beyond control"],
                "Notice Requirements": ["notice", "notification", "notify", "inform", "written notice"],
                "Renewal": ["renew", "renewal", "extend", "extension", "automatic renewal"],
                "Scope of Work": ["scope", "work", "services", "deliverables", "obligations", "duties"]
            }
            
            identified_topics = []
            combined_text = (original_text + " " + amendment_text).lower()
            
            # Check each topic category
            for topic, keywords in topic_keywords.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        if topic not in identified_topics:
                            identified_topics.append(topic)
                        break
            
            # Also check against key terms for additional context
            for term in key_terms:
                term_lower = term.lower()
                for topic, keywords in topic_keywords.items():
                    if any(keyword in term_lower for keyword in keywords):
                        if topic not in identified_topics:
                            identified_topics.append(topic)
            
            # If we found sections changed, try to infer topics from section names
            for section in changes_identified:
                section_lower = section.lower()
                for topic, keywords in topic_keywords.items():
                    if any(keyword in section_lower for keyword in keywords):
                        if topic not in identified_topics:
                            identified_topics.append(topic)
            
            # Return at least some topics even if detection is limited
            if not identified_topics:
                identified_topics = ["Contract Modifications"]
            
            return identified_topics[:10]  # Limit to top 10 most relevant
            
        except Exception as e:
            return ["Contract Analysis", "Document Changes"]

    @observe(name="generate_change_summary")
    def generate_change_summary(
        self,
        sections_changed: List[str],
        topics_touched: List[str],
        original_text: str,
        amendment_text: str,
        context: DocumentContext
    ) -> str:
        """
        Generate comprehensive summary of changes and their implications.
        
        Args:
            sections_changed: List of sections where changes occurred
            topics_touched: List of legal/business topics affected
            original_text: Original contract text
            amendment_text: Amendment text
            context: Document context from Agent 1
            
        Returns:
            Detailed change summary with business and legal implications
        """
        try:
            summary_prompt = f"""
Generate a comprehensive summary of contract changes based on this analysis:

SECTIONS CHANGED: {sections_changed}
TOPICS AFFECTED: {topics_touched}
DOCUMENT CONTEXT: {json.dumps(context.document_types, indent=2)}

REQUIREMENTS FOR SUMMARY:
1. What specifically changed (be precise about additions, deletions, modifications)
2. Business implications (who benefits, what risks change, operational impact)
3. Legal significance (enforceability, compliance, risk exposure changes)
4. Recommendations for stakeholders (legal review needs, approvals required)

Keep summary concise but comprehensive (200-400 words). Focus on actionable insights.

Original text length: {len(original_text)} characters
Amendment text length: {len(amendment_text)} characters
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a legal analyst creating executive summaries of contract changes for business stakeholders."
                    },
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback summary generation
            fallback_summary = f"""
Analysis of contract amendment affecting {len(topics_touched)} key areas: {', '.join(topics_touched[:3])}.

Changes identified in {len(sections_changed)} sections including: {', '.join(sections_changed[:2])}.

The amendment modifies the original contract with updates that impact business operations and legal obligations. 
Key areas of change include {', '.join(topics_touched[:2])} which may affect contractual relationships and performance requirements.

Stakeholders should review these changes for compliance with business objectives and legal requirements. 
Additional legal review may be warranted given the scope of modifications.

Note: Automated analysis encountered processing limitations. Manual review recommended for complete assessment.
"""
            return fallback_summary

    @observe(name="extract_changes")
    def extract_changes(
        self,
        original_text: str,
        amendment_text: str,
        context: DocumentContext,
        session_id: Optional[str] = None
    ) -> ContractChangeAnalysis:
        """
        Extract comprehensive change analysis using contextual information.
        
        Args:
            original_text: Original contract text
            amendment_text: Amendment text
            context: Contextual analysis from Agent 1
            session_id: Optional session identifier for tracing
            
        Returns:
            ContractChangeAnalysis with validated structured output
            
        Raises:
            Exception: If extraction fails
        """
        try:
            # Set trace metadata
            if session_id:
                langfuse.trace(
                    name="change_extraction",
                    session_id=session_id,
                    metadata={
                        "agent": "extraction_agent",
                        "sections_mapped": len(context.section_mapping) if isinstance(context.section_mapping, dict) else 0,
                        "key_terms_count": len(context.key_terms_identified)
                    }
                )
            
            # Generate extraction prompt
            extraction_prompt = self.get_extraction_prompt(original_text, amendment_text, context)
            
            # Perform change extraction
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            extraction_text = response.choices[0].message.content
            
            # Parse structured response
            try:
                # Extract JSON from response
                json_start = extraction_text.find('{')
                json_end = extraction_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = extraction_text[json_start:json_end]
                    extraction_data = json.loads(json_content)
                    
                    # Validate and clean extraction data
                    sections_changed = extraction_data.get("sections_changed", [])
                    topics_touched = extraction_data.get("topics_touched", [])
                    summary = extraction_data.get("summary_of_the_change", "")
                    
                    # Ensure we have meaningful data
                    if not sections_changed:
                        # Analyze change patterns as fallback
                        patterns = self.analyze_change_patterns(
                            original_text, amendment_text, context.section_mapping
                        )
                        sections_changed = [
                            f"Section {mod['section']}" for mod in patterns.get("modifications", [])
                        ] + [
                            f"New: {add['section']}" for add in patterns.get("additions", [])
                        ]
                    
                    if not topics_touched:
                        topics_touched = self.categorize_legal_topics(
                            sections_changed, context.key_terms_identified,
                            original_text, amendment_text
                        )
                    
                    if not summary or len(summary.strip()) < 50:
                        summary = self.generate_change_summary(
                            sections_changed, topics_touched, 
                            original_text, amendment_text, context
                        )
                    
                    # Create validated analysis
                    analysis = ContractChangeAnalysis(
                        sections_changed=sections_changed[:20],  # Limit to prevent overwhelming output
                        topics_touched=topics_touched[:15],  # Limit to most relevant topics
                        summary_of_the_change=summary,
                        confidence_score=extraction_data.get("confidence_score", 0.8),
                        processing_notes=extraction_data.get("processing_notes", "Standard processing")
                    )
                    
                    return analysis
                    
                else:
                    raise ValueError("No valid JSON structure found in extraction response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: JSON parsing failed ({e}), using fallback extraction")
                
                # Fallback extraction using individual methods
                patterns = self.analyze_change_patterns(
                    original_text, amendment_text, context.section_mapping
                )
                
                sections_changed = []
                if "modifications" in patterns:
                    sections_changed.extend([
                        f"Modified: {mod['section']}" for mod in patterns["modifications"]
                    ])
                if "additions" in patterns:
                    sections_changed.extend([
                        f"Added: {add['section']}" for add in patterns["additions"]  
                    ])
                
                topics_touched = self.categorize_legal_topics(
                    sections_changed, context.key_terms_identified,
                    original_text, amendment_text
                )
                
                summary = self.generate_change_summary(
                    sections_changed, topics_touched,
                    original_text, amendment_text, context
                )
                
                analysis = ContractChangeAnalysis(
                    sections_changed=sections_changed if sections_changed else ["Document Modified"],
                    topics_touched=topics_touched if topics_touched else ["Contract Changes"],
                    summary_of_the_change=summary,
                    confidence_score=0.6,  # Lower confidence for fallback
                    processing_notes="Fallback extraction used due to parsing issues"
                )
                
                return analysis
                
        except Exception as e:
            raise Exception(f"Change extraction failed: {str(e)}")

    def validate_extraction(self, analysis: ContractChangeAnalysis) -> Tuple[bool, List[str]]:
        """
        Validate the quality and completeness of extracted analysis.
        
        Args:
            analysis: ContractChangeAnalysis to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Validate sections_changed
        if not analysis.sections_changed:
            issues.append("No sections changed identified")
        elif len(analysis.sections_changed) > 25:
            issues.append("Too many sections identified - may be overly broad")
        
        # Validate topics_touched
        if not analysis.topics_touched:
            issues.append("No topics categorized")
        elif len(analysis.topics_touched) > 20:
            issues.append("Too many topics - may lack focus")
        
        # Validate summary
        if len(analysis.summary_of_the_change) < 100:
            issues.append("Summary too brief for comprehensive analysis")
        elif len(analysis.summary_of_the_change) > 2000:
            issues.append("Summary too lengthy - may be unfocused")
        
        # Check confidence
        if analysis.confidence_score and analysis.confidence_score < 0.5:
            issues.append("Low confidence score indicates potential quality concerns")
        
        # Check for generic content
        generic_phrases = [
            "the contract was modified",
            "changes were made to the document",
            "the amendment updates"
        ]
        
        summary_lower = analysis.summary_of_the_change.lower()
        if any(phrase in summary_lower for phrase in generic_phrases):
            issues.append("Summary contains generic language - may lack specific insights")
        
        return len(issues) == 0, issues