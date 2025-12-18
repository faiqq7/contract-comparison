#!/usr/bin/env python3
"""
Generate test contract images for the Contract Comparison Agent.
Creates comprehensive single-page contracts with all key sections visible.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Constants - Larger page for more content
PAGE_WIDTH = 2550   # 8.5" at 300 DPI
PAGE_HEIGHT = 3900  # Taller page to fit more content
MARGIN = 150
LINE_HEIGHT = 38
FONT_SIZE = 32
HEADING_SIZE = 40
TITLE_SIZE = 52

def get_font(size, bold=False):
    """Get a font - uses default if custom fonts aren't available."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()

def create_page():
    """Create a blank contract page."""
    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), 'white')
    draw = ImageDraw.Draw(img)
    return img, draw

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_text(draw, text, y, font, indent=0, bold_font=None):
    """Draw text on the page, returns new y position."""
    max_width = PAGE_WIDTH - 2 * MARGIN - indent
    lines = wrap_text(text, font, max_width, draw)
    
    for line in lines:
        x = MARGIN + indent
        draw.text((x, y), line, fill='black', font=font)
        y += LINE_HEIGHT
    
    return y

def draw_heading(draw, text, y, font):
    """Draw a section heading."""
    draw.text((MARGIN, y), text, fill='black', font=font)
    return y + LINE_HEIGHT + 15

def save_image(img, filename):
    """Save image as high-quality JPEG."""
    img.save(filename, 'JPEG', quality=95)
    print(f"Created: {filename}")

# =============================================================================
# CONTRACT PAIR 1: Service Agreement - ORIGINAL
# =============================================================================

def create_service_agreement_original():
    """Create comprehensive original service agreement with all key sections."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    # Title
    draw.text((PAGE_WIDTH//2 - 400, y), "PROFESSIONAL SERVICES AGREEMENT", fill='black', font=title_font)
    y += 80
    
    # Parties
    y = draw_text(draw, "This Agreement is entered into as of January 15, 2023, by and between TechCorp Solutions ('Service Provider') and Global Manufacturing Inc. ('Client').", y, font)
    y += 30
    
    # Section 1 - Definitions
    y = draw_heading(draw, "SECTION 1 - DEFINITIONS", y, heading_font)
    y = draw_text(draw, "1.1 'Services' means professional consulting and implementation services as described in Exhibit A.", y, font)
    y = draw_text(draw, "1.2 'Deliverables' means all work product created by Service Provider under this Agreement.", y, font)
    y += 20
    
    # Section 2 - Services
    y = draw_heading(draw, "SECTION 2 - SCOPE OF SERVICES", y, heading_font)
    y = draw_text(draw, "2.1 Service Provider shall perform Services in accordance with industry standards.", y, font)
    y = draw_text(draw, "2.2 Service Provider shall assign qualified personnel to perform the Services.", y, font)
    y += 20
    
    # Section 3 - Payment (KEY SECTION)
    y = draw_heading(draw, "SECTION 3 - COMPENSATION AND PAYMENT", y, heading_font)
    y = draw_text(draw, "3.1 Payment Terms. Client shall pay all undisputed invoices within thirty (30) days from the date of invoice. Service Provider shall submit invoices monthly for Services rendered during the preceding month.", y, font)
    y = draw_text(draw, "3.2 Fees. Client shall pay the fees set forth in Exhibit B.", y, font)
    y = draw_text(draw, "3.3 Late Payments. Amounts not paid when due shall bear interest at 1.5% per month.", y, font)
    y += 20
    
    # Section 4 - SLA (KEY SECTION)
    y = draw_heading(draw, "SECTION 4 - SERVICE LEVEL AGREEMENT", y, heading_font)
    y = draw_text(draw, "4.1 Availability. Service Provider shall ensure 99.5% uptime during business hours.", y, font)
    y = draw_text(draw, "4.2 Response Times. For issues reported by Client: (a) Critical Issues - Service Provider shall respond within four (4) business hours of notification and work continuously until resolution; (b) High Priority Issues - Response within eight (8) business hours; (c) Standard Issues - Response within two (2) business days.", y, font)
    y += 20
    
    # Section 5 - Term
    y = draw_heading(draw, "SECTION 5 - TERM", y, heading_font)
    y = draw_text(draw, "5.1 This Agreement shall commence on the Effective Date and continue for two (2) years.", y, font)
    y = draw_text(draw, "5.2 This Agreement shall automatically renew for successive one (1) year periods.", y, font)
    y += 20
    
    # Section 6 - Confidentiality
    y = draw_heading(draw, "SECTION 6 - CONFIDENTIALITY", y, heading_font)
    y = draw_text(draw, "6.1 Each party agrees to maintain the confidentiality of the other party's Confidential Information.", y, font)
    y += 20
    
    # Section 7 - Termination (KEY SECTION)
    y = draw_heading(draw, "SECTION 7 - TERMINATION", y, heading_font)
    y = draw_text(draw, "7.1 Termination. Either party may terminate this Agreement upon ninety (90) days prior written notice to the other party.", y, font)
    y = draw_text(draw, "7.2 Effect of Termination. Upon termination, Client shall pay for all Services performed through termination date.", y, font)
    y += 20
    
    # Section 8 - Warranties
    y = draw_heading(draw, "SECTION 8 - REPRESENTATIONS AND WARRANTIES", y, heading_font)
    y = draw_text(draw, "8.1 Service Provider warrants Services will be performed in a professional manner consistent with industry standards.", y, font)
    y += 20
    
    # Section 9 - Liability (KEY SECTION)
    y = draw_heading(draw, "SECTION 9 - LIMITATION OF LIABILITY", y, heading_font)
    y = draw_text(draw, "9.1 Exclusion of Damages. Neither party shall be liable for indirect, incidental, special, or consequential damages.", y, font)
    y = draw_text(draw, "9.2 Liability Cap. THE TOTAL LIABILITY OF SERVICE PROVIDER UNDER THIS AGREEMENT SHALL NOT EXCEED FIVE HUNDRED THOUSAND DOLLARS ($500,000) IN THE AGGREGATE.", y, font)
    y += 20
    
    # Section 10 - Indemnification
    y = draw_heading(draw, "SECTION 10 - INDEMNIFICATION", y, heading_font)
    y = draw_text(draw, "10.1 Service Provider shall indemnify Client from third-party claims arising from Service Provider's gross negligence.", y, font)
    y += 20
    
    # Section 11 - General
    y = draw_heading(draw, "SECTION 11 - GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "11.1 This Agreement constitutes the entire agreement between the parties.", y, font)
    y = draw_text(draw, "11.2 This Agreement shall be governed by the laws of the State of California.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "IN WITNESS WHEREOF, the parties have executed this Agreement as of January 15, 2023.", y, font)
    y += 50
    
    draw.text((MARGIN, y), "TECHCORP SOLUTIONS", fill='black', font=heading_font)
    draw.text((PAGE_WIDTH//2 + 100, y), "GLOBAL MANUFACTURING INC.", fill='black', font=heading_font)
    y += 50
    draw.text((MARGIN, y), "By: John Smith, CEO", fill='black', font=font)
    draw.text((PAGE_WIDTH//2 + 100, y), "By: Maria Garcia, COO", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 1: Service Agreement - AMENDMENT
# =============================================================================

def create_service_agreement_amendment():
    """Create comprehensive amendment with all 4 key changes."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    # Title
    draw.text((PAGE_WIDTH//2 - 500, y), "FIRST AMENDMENT TO PROFESSIONAL SERVICES AGREEMENT", fill='black', font=title_font)
    y += 80
    
    # Preamble
    y = draw_text(draw, "This First Amendment ('Amendment') to the Professional Services Agreement dated January 15, 2023 ('Agreement') is entered into as of June 15, 2023, by and between TechCorp Solutions ('Service Provider') and Global Manufacturing Inc. ('Client').", y, font)
    y += 20
    
    y = draw_text(draw, "WHEREAS, the parties desire to amend certain terms of the Agreement as set forth herein;", y, font)
    y = draw_text(draw, "NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:", y, font)
    y += 30
    
    # Amendment 1 - Payment Terms
    y = draw_heading(draw, "1. AMENDMENT TO SECTION 3.1 - PAYMENT TERMS", y, heading_font)
    y = draw_text(draw, "Section 3.1 of the Agreement is hereby DELETED in its entirety and REPLACED with:", y, font)
    y += 10
    y = draw_text(draw, "'3.1 Payment Terms. Client shall pay all undisputed invoices within forty-five (45) days from the date of invoice. As an incentive for early payment, Client shall receive a two percent (2%) discount on invoice amounts if payment is received within fifteen (15) days of the invoice date. Service Provider shall submit invoices monthly.'", y, font, indent=40)
    y += 30
    
    # Amendment 2 - Response Times
    y = draw_heading(draw, "2. AMENDMENT TO SECTION 4.2 - RESPONSE TIMES", y, heading_font)
    y = draw_text(draw, "Section 4.2 of the Agreement is hereby DELETED in its entirety and REPLACED with:", y, font)
    y += 10
    y = draw_text(draw, "'4.2 Response Times. For issues reported by Client: (a) Critical Issues - Service Provider shall respond within two (2) business hours of notification and work continuously until resolution; (b) Standard Issues - Response within eight (8) business hours with status updates every four (4) hours; (c) Low Priority Issues - Response within two (2) business days.'", y, font, indent=40)
    y += 30
    
    # Amendment 3 - Termination
    y = draw_heading(draw, "3. AMENDMENT TO SECTION 7.1 - TERMINATION", y, heading_font)
    y = draw_text(draw, "Section 7.1 of the Agreement is hereby DELETED in its entirety and REPLACED with:", y, font)
    y += 10
    y = draw_text(draw, "'7.1 Termination. (a) Termination for Convenience - Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice. (b) Termination for Material Breach - Either party may terminate immediately upon written notice if the other party commits a material breach and fails to cure such breach within thirty (30) days after receiving written notice. (c) Termination for Insolvency - Either party may terminate immediately if the other party becomes insolvent or files for bankruptcy.'", y, font, indent=40)
    y += 30
    
    # Amendment 4 - Liability Cap
    y = draw_heading(draw, "4. AMENDMENT TO SECTION 9.2 - LIABILITY CAP", y, heading_font)
    y = draw_text(draw, "Section 9.2 of the Agreement is hereby DELETED in its entirety and REPLACED with:", y, font)
    y += 10
    y = draw_text(draw, "'9.2 Liability Cap. THE TOTAL LIABILITY OF SERVICE PROVIDER UNDER THIS AGREEMENT SHALL NOT EXCEED TWO HUNDRED FIFTY THOUSAND DOLLARS ($250,000) IN THE AGGREGATE.'", y, font, indent=40)
    y += 30
    
    # Amendment 5 - New Mutual Indemnification
    y = draw_heading(draw, "5. NEW SECTION 10.3 - MUTUAL INDEMNIFICATION", y, heading_font)
    y = draw_text(draw, "A new Section 10.3 is hereby ADDED to the Agreement:", y, font)
    y += 10
    y = draw_text(draw, "'10.3 Mutual Indemnification. Each party shall indemnify and hold harmless the other party from any third-party claims, damages, or expenses arising from the indemnifying party's breach of this Agreement or violation of applicable law.'", y, font, indent=40)
    y += 30
    
    # General Provisions
    y = draw_heading(draw, "6. GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "6.1 Except as expressly modified by this Amendment, all terms and conditions of the Agreement shall remain in full force and effect.", y, font)
    y = draw_text(draw, "6.2 In the event of any conflict between this Amendment and the Agreement, this Amendment shall control.", y, font)
    y = draw_text(draw, "6.3 This Amendment shall be effective as of June 15, 2023.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "IN WITNESS WHEREOF, the parties have executed this Amendment as of June 15, 2023.", y, font)
    y += 50
    
    draw.text((MARGIN, y), "TECHCORP SOLUTIONS", fill='black', font=heading_font)
    draw.text((PAGE_WIDTH//2 + 100, y), "GLOBAL MANUFACTURING INC.", fill='black', font=heading_font)
    y += 50
    draw.text((MARGIN, y), "By: John Smith, CEO", fill='black', font=font)
    draw.text((PAGE_WIDTH//2 + 100, y), "By: Maria Garcia, COO", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 2: Software License - ORIGINAL
# =============================================================================

def create_software_license_original():
    """Create software license agreement original."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 400, y), "ENTERPRISE SOFTWARE LICENSE AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Agreement is entered into as of March 1, 2023, by and between DataFlow Systems, Inc. ('Licensor') and Regional Bank Corp. ('Licensee').", y, font)
    y += 30
    
    # Section 1
    y = draw_heading(draw, "SECTION 1 - DEFINITIONS", y, heading_font)
    y = draw_text(draw, "1.1 'Software' means the DataFlow Banking Platform and related documentation.", y, font)
    y = draw_text(draw, "1.2 'Users' means authorized employees and contractors of Licensee.", y, font)
    y += 20
    
    # Section 2 - License Scope (KEY)
    y = draw_heading(draw, "SECTION 2 - LICENSE GRANT", y, heading_font)
    y = draw_text(draw, "2.1 License Scope. Licensor grants Licensee a non-exclusive, non-transferable license to use the core banking platform Software for up to one hundred (100) authorized Users.", y, font)
    y = draw_text(draw, "2.2 Restrictions. Licensee shall not sublicense, modify, reverse engineer, or create derivative works.", y, font)
    y += 20
    
    # Section 3 - Term
    y = draw_heading(draw, "SECTION 3 - TERM", y, heading_font)
    y = draw_text(draw, "3.1 The initial term shall be three (3) years from the Effective Date.", y, font)
    y += 20
    
    # Section 4 - Warranties
    y = draw_heading(draw, "SECTION 4 - WARRANTIES", y, heading_font)
    y = draw_text(draw, "4.1 Licensor warrants Software will perform substantially in accordance with Documentation.", y, font)
    y += 20
    
    # Section 5 - Fees (KEY)
    y = draw_heading(draw, "SECTION 5 - FEES AND PAYMENT", y, heading_font)
    y = draw_text(draw, "5.1 License Fees. Licensee shall pay Licensor an annual license fee of One Hundred Twenty Thousand Dollars ($120,000), payable in advance on an annual basis.", y, font)
    y = draw_text(draw, "5.2 Payment Terms. All fees are due within thirty (30) days of invoice date.", y, font)
    y += 20
    
    # Section 6 - Confidentiality
    y = draw_heading(draw, "SECTION 6 - CONFIDENTIALITY", y, heading_font)
    y = draw_text(draw, "6.1 Each party shall maintain confidentiality of the other party's proprietary information.", y, font)
    y += 20
    
    # Section 7 - Liability
    y = draw_heading(draw, "SECTION 7 - LIMITATION OF LIABILITY", y, heading_font)
    y = draw_text(draw, "7.1 Licensor's liability shall not exceed fees paid in the prior twelve (12) months.", y, font)
    y += 20
    
    # Section 8 - Data (KEY)
    y = draw_heading(draw, "SECTION 8 - DATA AND SECURITY", y, heading_font)
    y = draw_text(draw, "8.1 Data Ownership. All data entered by Licensee remains Licensee's property.", y, font)
    y = draw_text(draw, "8.2 Data Security. Licensor shall implement reasonable security measures.", y, font)
    y = draw_text(draw, "8.3 Data Processing. Licensor shall process Licensee data in accordance with standard data processing requirements and applicable law.", y, font)
    y += 20
    
    # Exhibit A - Support (KEY)
    y = draw_heading(draw, "EXHIBIT A - SUPPORT SERVICES", y, heading_font)
    y = draw_text(draw, "1. Support Hours: Technical support available during business hours: 8:00 AM to 6:00 PM Eastern Time, Monday through Friday, excluding federal holidays.", y, font)
    y = draw_text(draw, "2. Response Times: Critical Issues - 4 hours; High Priority - 8 hours; Standard - 2 business days.", y, font)
    y = draw_text(draw, "3. Training: Initial training for up to ten (10) users included.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "IN WITNESS WHEREOF, executed as of March 1, 2023.", y, font)
    y += 50
    draw.text((MARGIN, y), "DATAFLOW SYSTEMS: David Chen, President", fill='black', font=font)
    draw.text((PAGE_WIDTH//2, y), "REGIONAL BANK CORP: Robert Williams, CTO", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 2: Software License - AMENDMENT
# =============================================================================

def create_software_license_amendment():
    """Create software license amendment with scope expansion."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 500, y), "SECOND AMENDMENT TO SOFTWARE LICENSE AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Amendment to the Enterprise Software License Agreement dated March 1, 2023 ('Agreement') is entered into as of September 1, 2023, by DataFlow Systems, Inc. ('Licensor') and Regional Bank Corp. ('Licensee').", y, font)
    y += 20
    
    y = draw_text(draw, "WHEREAS, the parties desire to expand the scope of licensed Software and modify certain terms;", y, font)
    y = draw_text(draw, "NOW, THEREFORE, the parties agree as follows:", y, font)
    y += 30
    
    # Amendment 1 - License Scope
    y = draw_heading(draw, "1. AMENDMENT TO SECTION 2.1 - LICENSE SCOPE", y, heading_font)
    y = draw_text(draw, "Section 2.1 is hereby DELETED and REPLACED with:", y, font)
    y = draw_text(draw, "'2.1 License Scope. Licensor grants Licensee a non-exclusive, non-transferable license to use: (a) The core banking platform Software; and (b) The DataFlow Mobile Banking Module for up to two hundred fifty (250) authorized Users.'", y, font, indent=40)
    y += 30
    
    # Amendment 2 - Fees
    y = draw_heading(draw, "2. AMENDMENT TO SECTION 5.1 - LICENSE FEES", y, heading_font)
    y = draw_text(draw, "Section 5.1 is hereby DELETED and REPLACED with:", y, font)
    y = draw_text(draw, "'5.1 License Fees. Licensee shall pay Licensor an annual license fee of Two Hundred Thousand Dollars ($200,000). At Licensee's option, fees may be paid: (a) Annually in advance; or (b) Quarterly at Fifty Thousand Dollars ($50,000) per quarter.'", y, font, indent=40)
    y += 30
    
    # Amendment 3 - Data Processing
    y = draw_heading(draw, "3. AMENDMENT TO SECTION 8.3 - DATA PROCESSING", y, heading_font)
    y = draw_text(draw, "Section 8.3 is hereby DELETED and REPLACED with:", y, font)
    y = draw_text(draw, "'8.3 Data Processing. (a) GDPR Compliance - Licensor shall process all personal data in compliance with GDPR and act as data processor on behalf of Licensee. (b) Data Residency - All Licensee data shall be stored exclusively within data centers located in the United States. No data transfer to other jurisdictions without written consent. (c) Data Processing Agreement - Parties shall execute separate DPA attached as Exhibit C.'", y, font, indent=40)
    y += 30
    
    # Amendment 4 - Support Services
    y = draw_heading(draw, "4. AMENDMENT TO EXHIBIT A - SUPPORT SERVICES", y, heading_font)
    y = draw_text(draw, "Exhibit A is hereby AMENDED as follows:", y, font)
    y = draw_text(draw, "'1. Support Hours: (a) Critical Systems (Core Banking, Mobile Banking) - 24 hours per day, 7 days per week, 365 days per year; (b) Non-Critical Systems - 8:00 AM to 6:00 PM Eastern Time, Monday through Friday.'", y, font, indent=40)
    y = draw_text(draw, "'2. Training: (a) Initial training for up to twenty-five (25) users included; (b) Quarterly refresher sessions (up to 4 per year) included; (c) Mobile Banking Module certification program for administrators.'", y, font, indent=40)
    y += 30
    
    # General Provisions
    y = draw_heading(draw, "5. GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "5.1 Except as modified, all terms remain in full force and effect.", y, font)
    y = draw_text(draw, "5.2 This Amendment effective September 1, 2023.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "IN WITNESS WHEREOF, executed as of September 1, 2023.", y, font)
    y += 50
    draw.text((MARGIN, y), "DATAFLOW SYSTEMS: David Chen, President", fill='black', font=font)
    draw.text((PAGE_WIDTH//2, y), "REGIONAL BANK CORP: Robert Williams, CTO", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 3: Employment Agreement - ORIGINAL
# =============================================================================

def create_employment_original():
    """Create employment agreement original."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 400, y), "SENIOR EXECUTIVE EMPLOYMENT AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Agreement is entered into as of February 1, 2023, by and between InnovaTech Corp. ('Company') and Sarah Johnson ('Executive').", y, font)
    y += 30
    
    # Section 1
    y = draw_heading(draw, "SECTION 1 - EMPLOYMENT AND DUTIES", y, heading_font)
    y = draw_text(draw, "1.1 Position. Company employs Executive as Vice President of Engineering.", y, font)
    y = draw_text(draw, "1.2 Company Address. The Company's principal place of business is located at 123 Tech Street, San Francisco, CA 94105.", y, font)
    y = draw_text(draw, "1.3 Duties. Executive shall perform duties customary for the position.", y, font)
    y += 20
    
    # Section 2
    y = draw_heading(draw, "SECTION 2 - TERM", y, heading_font)
    y = draw_text(draw, "2.1 Employment is at-will and may be terminated by either party at any time.", y, font)
    y += 20
    
    # Section 3 - Reporting (KEY)
    y = draw_heading(draw, "SECTION 3 - REPORTING AND ORGANIZATION", y, heading_font)
    y = draw_text(draw, "3.1 Reporting Structure. Executive shall report directly to the Chief Technology Officer ('CTO') of the Company.", y, font)
    y = draw_text(draw, "3.2 Direct Reports. Executive manages Engineering department (~50 employees).", y, font)
    y = draw_text(draw, "3.3 Performance Reviews. Executive's performance reviewed annually by the CTO.", y, font)
    y += 20
    
    # Section 4
    y = draw_heading(draw, "SECTION 4 - COMPENSATION", y, heading_font)
    y = draw_text(draw, "4.1 Base Salary. Annual base salary of $300,000.", y, font)
    y = draw_text(draw, "4.2 Annual Bonus. Eligible for up to 40% bonus based on goals established by the CTO.", y, font)
    y = draw_text(draw, "4.3 Equity. Stock options for 100,000 shares.", y, font)
    y += 20
    
    # Section 5
    y = draw_heading(draw, "SECTION 5 - BENEFITS", y, heading_font)
    y = draw_text(draw, "5.1 Health insurance and benefit programs.", y, font)
    y = draw_text(draw, "5.2 Four (4) weeks paid vacation per year.", y, font)
    y += 20
    
    # Section 6
    y = draw_heading(draw, "SECTION 6 - TERMINATION", y, heading_font)
    y = draw_text(draw, "6.1 Company may terminate at any time with or without cause.", y, font)
    y = draw_text(draw, "6.2 Executive may terminate upon thirty (30) days written notice.", y, font)
    y = draw_text(draw, "6.3 If terminated without cause, six (6) months severance.", y, font)
    y += 20
    
    # Section 7
    y = draw_heading(draw, "SECTION 7 - CONFIDENTIALITY AND IP", y, heading_font)
    y = draw_text(draw, "7.1 Executive maintains confidentiality of proprietary information.", y, font)
    y = draw_text(draw, "7.2 All work product is Company property.", y, font)
    y += 20
    
    # Section 8
    y = draw_heading(draw, "SECTION 8 - GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "8.1 This Agreement constitutes entire agreement between parties.", y, font)
    y = draw_text(draw, "8.2 Governed by laws of California.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "Executed as of February 1, 2023.", y, font)
    y += 50
    draw.text((MARGIN, y), "INNOVATECH CORP: Michael Thompson, CTO", fill='black', font=font)
    y += 40
    draw.text((MARGIN, y), "EXECUTIVE: Sarah Johnson", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 3: Employment Agreement - AMENDMENT (Administrative)
# =============================================================================

def create_employment_amendment():
    """Create employment amendment with administrative changes."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 500, y), "FIRST AMENDMENT TO EMPLOYMENT AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Amendment to the Employment Agreement dated February 1, 2023 ('Agreement') is entered into as of August 1, 2023, by InnovaTech Corp. ('Company') and Sarah Johnson ('Executive').", y, font)
    y += 20
    
    y = draw_text(draw, "WHEREAS, Company has relocated its principal place of business;", y, font)
    y = draw_text(draw, "WHEREAS, Company has undergone organizational restructuring;", y, font)
    y = draw_text(draw, "WHEREAS, parties desire to update Agreement to reflect these administrative changes;", y, font)
    y = draw_text(draw, "NOW, THEREFORE, the parties agree:", y, font)
    y += 30
    
    # Amendment 1 - Address
    y = draw_heading(draw, "1. AMENDMENT TO SECTION 1.2 - COMPANY ADDRESS", y, heading_font)
    y = draw_text(draw, "Section 1.2 is hereby DELETED and REPLACED with:", y, font)
    y = draw_text(draw, "'1.2 Company Address. The Company's principal place of business is located at 456 Innovation Blvd, San Francisco, CA 94107.'", y, font, indent=40)
    y += 30
    
    # Amendment 2 - Reporting
    y = draw_heading(draw, "2. AMENDMENT TO SECTION 3.1 - REPORTING STRUCTURE", y, heading_font)
    y = draw_text(draw, "Section 3.1 is hereby DELETED and REPLACED with:", y, font)
    y = draw_text(draw, "'3.1 Reporting Structure. Executive shall report directly to the Chief Executive Officer ('CEO') of the Company.'", y, font, indent=40)
    y += 30
    
    # Amendment 3 - Conforming
    y = draw_heading(draw, "3. CONFORMING AMENDMENTS", y, heading_font)
    y = draw_text(draw, "All references to 'Chief Technology Officer' or 'CTO' in the Agreement are hereby REPLACED with 'Chief Executive Officer' or 'CEO', respectively, including:", y, font)
    y = draw_text(draw, "- Section 3.3 (Performance Reviews): Reviews conducted by CEO", y, font, indent=40)
    y = draw_text(draw, "- Section 4.2 (Annual Bonus): Goals established by CEO", y, font, indent=40)
    y += 30
    
    # General
    y = draw_heading(draw, "4. GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "4.1 Except as modified, all terms remain in full force and effect.", y, font)
    y = draw_text(draw, "4.2 This Amendment effective August 1, 2023.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "Executed as of August 1, 2023.", y, font)
    y += 50
    draw.text((MARGIN, y), "INNOVATECH CORP: Jennifer Adams, CEO", fill='black', font=font)
    y += 40
    draw.text((MARGIN, y), "EXECUTIVE: Sarah Johnson", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 4: Master Service Agreement - ORIGINAL
# =============================================================================

def create_msa_original():
    """Create MSA original."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 300, y), "MASTER SERVICE AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Agreement is entered into as of January 1, 2023, by Global Consulting Group, LLC ('Consultant') and Fortune 500 Manufacturing Company ('Client').", y, font)
    y += 30
    
    # Section 1
    y = draw_heading(draw, "SECTION 1 - DEFINITIONS", y, heading_font)
    y = draw_text(draw, "1.1 'Services' means consulting and professional services per Statements of Work.", y, font)
    y = draw_text(draw, "1.2 'Work Product' means all deliverables created under this Agreement.", y, font)
    y += 20
    
    # Section 2 - Scope (KEY - Geographic)
    y = draw_heading(draw, "SECTION 2 - SCOPE OF SERVICES", y, heading_font)
    y = draw_text(draw, "2.1 Consultant shall provide Services as set forth in executed SOWs.", y, font)
    y = draw_text(draw, "2.2 Each SOW shall reference this Agreement and describe specific Services.", y, font)
    y = draw_text(draw, "2.3 Geographic Scope. Services under this Agreement shall be performed for Client's United States operations only.", y, font)
    y += 20
    
    # Section 3 - Term
    y = draw_heading(draw, "SECTION 3 - TERM", y, heading_font)
    y = draw_text(draw, "3.1 Term. Agreement continues for three (3) years, auto-renewing annually.", y, font)
    y += 20
    
    # Section 4 - Compensation (KEY)
    y = draw_heading(draw, "SECTION 4 - COMPENSATION", y, heading_font)
    y = draw_text(draw, "4.1 Fee Structure. Client compensates Consultant based on hourly rates: Partner - $500/hr; Senior Consultant - $350/hr; Consultant - $250/hr; Analyst - $175/hr.", y, font)
    y = draw_text(draw, "4.2 Invoicing. Consultant invoices monthly for Services rendered.", y, font)
    y = draw_text(draw, "4.3 Payment Terms. Payment due within thirty (30) days of invoice.", y, font)
    y += 20
    
    # Section 5 - Personnel
    y = draw_heading(draw, "SECTION 5 - PERSONNEL", y, heading_font)
    y = draw_text(draw, "5.1 Consultant assigns qualified personnel. Client may request replacement.", y, font)
    y += 20
    
    # Section 6 - Governance (KEY)
    y = draw_heading(draw, "SECTION 6 - GOVERNANCE", y, heading_font)
    y = draw_text(draw, "6.1 Project Management. Consultant assigns dedicated project manager per SOW.", y, font)
    y = draw_text(draw, "6.2 Steering Committee. Parties conduct monthly steering committee meetings to review status, issues, and strategic direction.", y, font)
    y = draw_text(draw, "6.3 Reporting. Consultant provides monthly status reports on active SOWs.", y, font)
    y += 20
    
    # Section 11 - IP (KEY)
    y = draw_heading(draw, "SECTION 11 - INTELLECTUAL PROPERTY", y, heading_font)
    y = draw_text(draw, "11.1 Client Ownership. Work Product created specifically for Client owned by Client.", y, font)
    y = draw_text(draw, "11.2 Consultant Tools. Consultant retains ownership of pre-existing methodologies.", y, font)
    y = draw_text(draw, "11.3 License. Consultant grants Client perpetual license to embedded tools.", y, font)
    y += 20
    
    # Section 13 - Insurance (KEY)
    y = draw_heading(draw, "SECTION 13 - INSURANCE", y, heading_font)
    y = draw_text(draw, "13.1 Required Coverage. Consultant maintains: (a) Commercial General Liability - $2,000,000 per occurrence; (b) Professional Liability (E&O) - $5,000,000 per occurrence; (c) Workers' Compensation as required by law.", y, font)
    y += 40
    
    # Signatures
    y = draw_text(draw, "Executed as of January 1, 2023.", y, font)
    y += 40
    draw.text((MARGIN, y), "GLOBAL CONSULTING: Elizabeth Warren, Managing Partner", fill='black', font=font)
    draw.text((PAGE_WIDTH//2, y), "CLIENT: James Mitchell, CPO", fill='black', font=font)
    
    return img

# =============================================================================
# CONTRACT PAIR 4: MSA - AMENDMENT (Complex Multi-Section)
# =============================================================================

def create_msa_amendment():
    """Create MSA amendment with complex multi-section changes."""
    img, draw = create_page()
    font = get_font(FONT_SIZE)
    heading_font = get_font(HEADING_SIZE)
    title_font = get_font(TITLE_SIZE)
    
    y = 100
    
    draw.text((PAGE_WIDTH//2 - 400, y), "THIRD AMENDMENT TO MASTER SERVICE AGREEMENT", fill='black', font=title_font)
    y += 80
    
    y = draw_text(draw, "This Amendment to the Master Service Agreement dated January 1, 2023 ('Agreement') is entered into as of October 15, 2023, by Global Consulting Group, LLC ('Consultant') and Fortune 500 Manufacturing Company ('Client').", y, font)
    y += 20
    y = draw_text(draw, "WHEREAS, parties desire to restructure compensation and expand engagement scope;", y, font)
    y = draw_text(draw, "NOW, THEREFORE, parties agree:", y, font)
    y += 25
    
    # Amendment 1 - Geographic
    y = draw_heading(draw, "1. AMENDMENT TO SECTION 2.3 - GEOGRAPHIC SCOPE", y, heading_font)
    y = draw_text(draw, "Section 2.3 DELETED and REPLACED with: '2.3 Geographic Scope. Services may be performed for Client's operations in the United States, Canada, and Mexico, pursuant to USMCA framework. Cross-border engagements shall comply with applicable local laws.'", y, font, indent=40)
    y += 25
    
    # Amendment 2 - Pricing
    y = draw_heading(draw, "2. AMENDMENT TO SECTION 4 - COMPENSATION", y, heading_font)
    y = draw_text(draw, "Section 4 DELETED and REPLACED with: '4.1 Blended Rate. Client compensates Consultant at blended rate of $325/hour regardless of personnel level. 4.2 Volume Discounts: $1M-$2M annual = 5% discount; $2M-$5M = 10% discount; Over $5M = 15% discount. 4.3 Success Fees. Consultant entitled to 5% of documented cost savings or revenue improvements from recommendations.'", y, font, indent=40)
    y += 25
    
    # Amendment 3 - Governance
    y = draw_heading(draw, "3. AMENDMENT TO SECTION 6 - GOVERNANCE", y, heading_font)
    y = draw_text(draw, "Section 6 DELETED and REPLACED with: '6.1 Program Director assigned plus project managers per SOW. 6.2 Weekly Operational Reviews for status and immediate issues. 6.3 Quarterly Business Reviews for strategic alignment and value assessment. 6.4 Escalation: Issues unresolved at project level within 5 days escalate to executive sponsors; unresolved within 10 days to steering committee.'", y, font, indent=40)
    y += 25
    
    # Amendment 4 - IP
    y = draw_heading(draw, "4. AMENDMENT TO SECTION 11 - INTELLECTUAL PROPERTY", y, heading_font)
    y = draw_text(draw, "Section 11 DELETED and REPLACED with: '11.1 Client Work Product owned by Client. 11.2 Joint Innovations - Jointly developed novel IP owned by both parties; each may use, license, commercialize without accounting. 11.3 Consultant Tools retained by Consultant. 11.4 Joint IP Licensing: Sublicense to affiliates without consent; third-party sublicense requires consent; third-party revenue shared equally.'", y, font, indent=40)
    y += 25
    
    # Amendment 5 - Insurance
    y = draw_heading(draw, "5. AMENDMENT TO SECTION 13.1 - INSURANCE", y, heading_font)
    y = draw_text(draw, "Section 13.1 DELETED and REPLACED with: '13.1 Required Coverage: (a) Commercial General Liability - $5,000,000 per occurrence, $10,000,000 aggregate; (b) Professional Liability (E&O) - $10,000,000 per occurrence, $20,000,000 aggregate; (c) Cyber Liability - $5,000,000 per occurrence covering data breaches, network security, privacy violations; (d) Workers' Compensation as required by applicable law.'", y, font, indent=40)
    y += 25
    
    # General
    y = draw_heading(draw, "6. GENERAL PROVISIONS", y, heading_font)
    y = draw_text(draw, "6.1 Except as modified, all terms remain in full force. 6.2 Effective October 15, 2023. 6.3 This Amendment controls in case of conflict.", y, font)
    y += 30
    
    # Signatures
    y = draw_text(draw, "Executed as of October 15, 2023.", y, font)
    y += 40
    draw.text((MARGIN, y), "GLOBAL CONSULTING: Elizabeth Warren, Managing Partner", fill='black', font=font)
    draw.text((PAGE_WIDTH//2, y), "CLIENT: James Mitchell, CPO", fill='black', font=font)
    
    return img

# =============================================================================
# MAIN
# =============================================================================

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("Generating comprehensive test contract images...")
    print("=" * 60)
    
    # Pair 1
    print("\n📄 Contract Pair 1: Service Agreement")
    img = create_service_agreement_original()
    save_image(img, os.path.join(output_dir, "service_agreement_original.jpg"))
    img = create_service_agreement_amendment()
    save_image(img, os.path.join(output_dir, "service_agreement_amendment_1.jpg"))
    
    # Pair 2
    print("\n📄 Contract Pair 2: Software License")
    img = create_software_license_original()
    save_image(img, os.path.join(output_dir, "software_license_original.jpg"))
    img = create_software_license_amendment()
    save_image(img, os.path.join(output_dir, "software_license_amendment_2.jpg"))
    
    # Pair 3
    print("\n📄 Contract Pair 3: Employment Agreement")
    img = create_employment_original()
    save_image(img, os.path.join(output_dir, "employment_agreement_original.jpg"))
    img = create_employment_amendment()
    save_image(img, os.path.join(output_dir, "employment_agreement_amendment_1.jpg"))
    
    # Pair 4
    print("\n📄 Contract Pair 4: Master Service Agreement")
    img = create_msa_original()
    save_image(img, os.path.join(output_dir, "master_service_agreement_original.jpg"))
    img = create_msa_amendment()
    save_image(img, os.path.join(output_dir, "master_service_agreement_amendment_3.jpg"))
    
    print("\n" + "=" * 60)
    print("✅ All test contracts generated!")
    print("=" * 60)
    print("\nExpected changes per pair:")
    print("  Pair 1: Payment Terms, Response Times, Termination, Liability Cap")
    print("  Pair 2: License Scope, Fees, Data Processing, Support Hours")
    print("  Pair 3: Company Address, Reporting Structure (administrative)")
    print("  Pair 4: Geographic, Pricing, Governance, IP, Insurance")

if __name__ == "__main__":
    main()
