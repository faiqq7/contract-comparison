# Test Contract Data

This directory contains sample contract pairs for testing the Contract Comparison and Change Extraction Agent. Each pair consists of an original contract and its amendment, designed to test different types of contract modifications and edge cases.

## Contract Pair 1: Service Agreement - Payment Terms Modification

### Files:
- `service_agreement_original.jpg` - Original service agreement (8 pages)
- `service_agreement_amendment_1.jpg` - First amendment (3 pages)

### Contract Details:
- **Original Date**: January 15, 2023
- **Amendment Date**: June 15, 2023
- **Contract Type**: Professional Services Agreement
- **Parties**: TechCorp Solutions (Service Provider) and Global Manufacturing Inc. (Client)

### Changes Implemented:
1. **Payment Terms (Section 3.1)**:
   - **Original**: Net 30 days from invoice date
   - **Amendment**: Net 45 days from invoice date with 2% early payment discount if paid within 15 days

2. **Service Level Agreement (Section 4.2)**:
   - **Original**: Response time within 4 business hours for critical issues
   - **Amendment**: Response time within 2 business hours for critical issues, 8 hours for standard issues

3. **Termination Clause (Section 7.1)**:
   - **Original**: 90-day written notice required for termination
   - **Amendment**: Added termination for convenience with 60-day notice, material breach clause with 30-day cure period

4. **Liability Limitation (Section 9.2)**:
   - **Original**: Liability capped at $500,000
   - **Amendment**: Liability cap reduced to $250,000, mutual indemnification added

### Expected Analysis Results:
- **Sections Changed**: ["Section 3.1 - Payment Terms", "Section 4.2 - Service Levels", "Section 7.1 - Termination", "Section 9.2 - Liability"]
- **Topics Touched**: ["Payment Terms", "Performance Standards", "Termination Rights", "Risk Allocation"]
- **Key Impacts**: Payment flexibility for client, increased service standards, enhanced termination options, reduced provider liability

---

## Contract Pair 2: Software License Agreement - Scope Expansion

### Files:
- `software_license_original.jpg` - Original software license (12 pages)
- `software_license_amendment_2.jpg` - Second amendment (5 pages)

### Contract Details:
- **Original Date**: March 1, 2023
- **Amendment Date**: September 1, 2023
- **Contract Type**: Enterprise Software License Agreement
- **Parties**: DataFlow Systems (Licensor) and Regional Bank Corp (Licensee)

### Changes Implemented:
1. **Licensed Software Scope (Section 2.1)**:
   - **Original**: Core banking platform for 100 users
   - **Amendment**: Extended to include mobile banking module, increased to 250 users

2. **Fees and Payment (Section 5.1)**:
   - **Original**: Annual license fee of $120,000
   - **Amendment**: Increased to $200,000 annually, quarterly payment option added

3. **Data Processing (Section 8.3)**:
   - **Original**: Standard data processing requirements
   - **Amendment**: Added GDPR compliance requirements, data residency restrictions

4. **Support Services (Exhibit A)**:
   - **Original**: Business hours support (8 AM - 6 PM EST)
   - **Amendment**: Extended to 24/7 support for critical systems, additional training included

### Expected Analysis Results:
- **Sections Changed**: ["Section 2.1 - License Scope", "Section 5.1 - Fees", "Section 8.3 - Data Processing", "Exhibit A - Support Services"]
- **Topics Touched**: ["Scope of Work", "Pricing", "Compliance", "Support Services", "Data Privacy"]
- **Key Impacts**: Significant scope expansion, cost increase justified by enhanced services, new regulatory compliance requirements

---

## Contract Pair 3: Employment Agreement - Minimal Administrative Changes

### Files:
- `employment_agreement_original.jpg` - Original employment agreement (6 pages)
- `employment_agreement_amendment_1.jpg` - Administrative amendment (2 pages)

### Contract Details:
- **Original Date**: February 1, 2023
- **Amendment Date**: August 1, 2023
- **Contract Type**: Senior Executive Employment Agreement
- **Parties**: InnovaTech Corp and Sarah Johnson (VP of Engineering)

### Changes Implemented:
1. **Contact Information (Section 1.2)**:
   - **Original**: Company address: 123 Tech Street, San Francisco, CA
   - **Amendment**: Updated to: 456 Innovation Blvd, San Francisco, CA (office relocation)

2. **Reporting Structure (Section 3.1)**:
   - **Original**: Reports to Chief Technology Officer
   - **Amendment**: Reports to Chief Executive Officer (organizational restructure)

3. **Administrative Updates**:
   - **Original**: Various references to "CTO" throughout document
   - **Amendment**: Updated all references to "CEO"

### Expected Analysis Results:
- **Sections Changed**: ["Section 1.2 - Company Address", "Section 3.1 - Reporting Structure"]
- **Topics Touched**: ["Administrative Updates", "Organizational Structure"]
- **Key Impacts**: Administrative changes with minimal business impact, reflects company restructuring

---

## Contract Pair 4: Complex Multi-Section Amendment

### Files:
- `master_service_agreement_original.jpg` - Original MSA (15 pages)
- `master_service_agreement_amendment_3.jpg` - Third amendment (8 pages)

### Contract Details:
- **Original Date**: January 1, 2023
- **Amendment Date**: October 15, 2023
- **Contract Type**: Master Service Agreement with multiple SOWs
- **Parties**: Global Consulting Group and Fortune 500 Manufacturing Company

### Changes Implemented:
1. **Pricing Structure (Section 4)**:
   - **Original**: Fixed hourly rates by role
   - **Amendment**: Blended rate model with volume discounts, success fee components

2. **Intellectual Property (Section 11)**:
   - **Original**: Work product owned by client
   - **Amendment**: Shared IP model for jointly developed innovations, licensing terms added

3. **Governance (Section 6)**:
   - **Original**: Monthly steering committee meetings
   - **Amendment**: Weekly operational reviews, quarterly business reviews, escalation procedures

4. **Risk and Insurance (Section 13)**:
   - **Original**: $2M general liability, $5M E&O coverage
   - **Amendment**: Increased to $5M general liability, $10M E&O, cyber liability added

5. **Geographic Scope (Section 2.3)**:
   - **Original**: United States operations only
   - **Amendment**: Extended to include Canada and Mexico under USMCA framework

### Expected Analysis Results:
- **Sections Changed**: ["Section 4 - Pricing", "Section 11 - Intellectual Property", "Section 6 - Governance", "Section 13 - Insurance", "Section 2.3 - Geographic Scope"]
- **Topics Touched**: ["Pricing Models", "Intellectual Property Rights", "Project Governance", "Risk Management", "Geographic Expansion"]
- **Key Impacts**: Comprehensive restructuring affecting multiple business areas, increased complexity and risk allocation

---

## Testing Guidelines

### Image Quality Standards:
- **Resolution**: 300 DPI minimum for clear text recognition
- **Format**: JPEG or PNG formats supported
- **Size**: Files should be under 10MB for optimal processing
- **Quality**: Professional scanning preferred, phone photos acceptable if well-lit and focused

### Usage Instructions:

**Basic Test:**
```bash
python src/main.py --original data/test_contracts/service_agreement_original.jpg --amendment data/test_contracts/service_agreement_amendment_1.jpg
```

**Batch Testing:**
```bash
# Test all contract pairs
for pair in service_agreement software_license employment_agreement master_service_agreement; do
    echo "Testing $pair..."
    python src/main.py --original "data/test_contracts/${pair}_original.jpg" --amendment "data/test_contracts/${pair}_amendment_*.jpg" --session "test_$pair"
done
```

### Expected Performance:
- **Processing Time**: 30-90 seconds per contract pair
- **Accuracy**: >90% change detection rate on test data
- **Confidence Scores**: Should average >0.8 for high-quality scanned documents

### Validation Checklist:
- [ ] All expected sections identified in results
- [ ] Topic categorization aligns with change descriptions
- [ ] Summary captures key business implications
- [ ] No hallucinated changes (false positives)
- [ ] Confidence scores reflect analysis quality

## Notes on Real Contract Images

**Important**: The actual image files are not included in this repository due to:
1. **Confidentiality**: Real contract content contains sensitive business information
2. **Legal Compliance**: Actual legal documents require careful handling and permissions
3. **File Size**: High-resolution contract images are large and not suitable for repository storage

**For Production Use**: 
- Source your own contract images for testing
- Ensure you have proper authorization to process contract documents
- Consider data privacy and confidentiality requirements in your jurisdiction
- Use anonymized or synthetic contract data when possible for development

**Creating Your Own Test Data**:
1. Use contract templates from legal document libraries
2. Create mock amendments with realistic changes
3. Print and scan documents to simulate real-world image quality
4. Vary document layouts and formatting to test robustness