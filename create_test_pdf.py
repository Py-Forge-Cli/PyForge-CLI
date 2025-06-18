#!/usr/bin/env python3
"""Create a test PDF file for testing CortexPy CLI."""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import sys
    
    def create_test_pdf():
        # Create PDF
        doc = SimpleDocTemplate("test_document.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        title = Paragraph("Test Document for CortexPy CLI", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        content = [
            "This is a test PDF document created for testing the CortexPy CLI tool.",
            "",
            "Page 1 Content:",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "",
            "Features to test:",
            "• PDF to text conversion",
            "• Page range extraction", 
            "• Metadata extraction",
            "• File validation",
            "",
            "This document contains multiple paragraphs to test text extraction quality.",
        ]
        
        for line in content:
            if line:
                para = Paragraph(line, styles['Normal'])
                story.append(para)
            story.append(Spacer(1, 6))
        
        # Add page 2
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        
        page2_title = Paragraph("Page 2 - Additional Content", styles['Heading1'])
        story.append(page2_title)
        story.append(Spacer(1, 12))
        
        page2_content = [
            "This is content on the second page.",
            "Use this to test page range functionality:",
            "cortexpy convert test_document.pdf --pages '2'",
            "cortexpy convert test_document.pdf --pages '1-2'",
            "",
            "Additional test content with special characters:",
            "Special chars: áéíóú ñ © ® ™ § ¶",
            "Numbers: 123456789",
            "Symbols: !@#$%^&*()",
        ]
        
        for line in page2_content:
            if line:
                para = Paragraph(line, styles['Normal'])
                story.append(para)
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        print("✓ Created test_document.pdf")
        return True
        
    if __name__ == "__main__":
        create_test_pdf()

except ImportError:
    print("ReportLab not available. Creating simple text-based test instead.")
    print("You can use any existing PDF file for testing.")
    
    # Create a simple instruction file
    with open("test_instructions.txt", "w") as f:
        f.write("""
CortexPy CLI Testing Instructions
================================

Since ReportLab is not available, you can test with any PDF file:

1. Find any PDF file on your system
2. Copy it to this directory as 'test_document.pdf'
3. Run the test commands below

Common locations for PDF files:
- ~/Downloads/
- ~/Documents/ 
- /System/Library/Documentation/ (macOS)

Or create a simple PDF using any application and save it as test_document.pdf
""")
    print("✓ Created test_instructions.txt - follow instructions to get a test PDF")