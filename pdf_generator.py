"""PDF generation utilities for pipeline deliverables"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import urllib.request
from PIL import Image

class PDFGenerator:
    """Generate professional PDF reports from pipeline output"""
    
    def __init__(self):
        self.pagesize = letter
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=4 , # Justify
            spaceAfter=12
        ))
    
    def generate_pdf(self, content_dict, image_url=None, output_filename="deliverable.pdf"):
        """
        Generate PDF from pipeline content dictionary
        
        Args:
            content_dict: Dictionary with problem_reqs, technical_plan, etc.
            image_url: URL of the architecture diagram (optional)
            output_filename: Name of output PDF file
            
        Returns:
            bytes: PDF file content
        """
        try:
            # Create PDF buffer
            pdf_buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=self.pagesize,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Story to hold all elements
            story = []
            
            # Add title page
            story.extend(self._create_title_page(content_dict))
            story.append(PageBreak())
            
            # Add table of contents
            story.extend(self._create_toc())
            story.append(PageBreak())
            
            # Add problem requirements section
            story.extend(self._create_problem_section(content_dict.get('problem-requirements', {})))
            story.append(PageBreak())
            
            # Add technical plan section
            story.extend(self._create_technical_section(content_dict.get('technical-plan', {})))
            story.append(PageBreak())
            
            # Add ARCHITECTURE DIAGRAM section (NEW!)
            if image_url:
                story.extend(self._create_architecture_section(image_url))
                story.append(PageBreak())
            
            # Add deliverable plan section
            story.extend(self._create_deliverable_section(content_dict.get('deliverable-plan', {})))
            story.append(PageBreak())
            
            # Add data plan section
            story.extend(self._create_data_section(content_dict.get('data-plan', {})))
            
            # Build PDF
            doc.build(story)
            
            # Get bytes
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _create_title_page(self, content):
        """Create title page"""
        story = []
        
        story.append(Spacer(1, 2*inch))
        
        title = Paragraph(
            "AI Deliverable Generator",
            self.styles['CustomTitle']
        )
        story.append(title)
        
        subtitle = Paragraph(
            "Comprehensive Technical Deliverable",
            self.styles['Heading2']
        )
        story.append(subtitle)
        
        story.append(Spacer(1, 0.5*inch))
        
        date_text = Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        story.append(date_text)
        
        return story
    
    def _create_toc(self):
        """Create table of contents"""
        story = []
        
        toc_title = Paragraph("Table of Contents", self.styles['CustomHeading2'])
        story.append(toc_title)
        story.append(Spacer(1, 0.5*inch))
        
        toc_items = [
            "1. Executive Summary",
            "2. Problem Definition & Requirements",
            "3. Technical Approach & Architecture",
            "4. Technology Stack",
            "5. Deliverable Plan & Milestones",
            "6. Success Criteria",
            "7. Data Architecture",
            "8. Data Governance"
        ]
        
        for item in toc_items:
            p = Paragraph(item, self.styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_problem_section(self, problem_reqs):
        """Create problem requirements section"""
        story = []
        
        title = Paragraph("1. Executive Summary", self.styles['CustomHeading2'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Executive summary
        exec_summary = problem_reqs.get('executive-summary', 'N/A')
        if exec_summary:
            p = Paragraph(exec_summary, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Problem definition
        title2 = Paragraph("2. Problem Definition", self.styles['CustomHeading2'])
        story.append(title2)
        story.append(Spacer(1, 0.2*inch))
        
        problem_def = problem_reqs.get('problem-definition', 'N/A')
        if problem_def:
            p = Paragraph(problem_def, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Requirements
        title3 = Paragraph("2.1 Key Requirements", self.styles['Heading3'])
        story.append(title3)
        story.append(Spacer(1, 0.2*inch))
        
        requirements = problem_reqs.get('problem-requirements', [])
        if isinstance(requirements, list):
            for i, req in enumerate(requirements, 1):
                p = Paragraph(f"• {req}", self.styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_technical_section(self, technical_plan):
        """Create technical plan section"""
        story = []
        
        title = Paragraph("3. Technical Approach & Architecture", self.styles['CustomHeading2'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Technical approach
        approach = technical_plan.get('technical-approach', 'N/A')
        if approach:
            p = Paragraph(approach, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Architecture overview
        title2 = Paragraph("3.1 Architecture Overview", self.styles['Heading3'])
        story.append(title2)
        story.append(Spacer(1, 0.2*inch))
        
        architecture = technical_plan.get('architecture-overview', 'N/A')
        if architecture:
            p = Paragraph(architecture, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Technology stack
        title3 = Paragraph("4. Technology Stack", self.styles['CustomHeading2'])
        story.append(title3)
        story.append(Spacer(1, 0.2*inch))
        
        tech_stack = technical_plan.get('technology-stack', {})
        if isinstance(tech_stack, dict):
            for category, technologies in tech_stack.items():
                cat_title = Paragraph(
                    f"<b>{category.replace('-', ' ').title()}:</b>",
                    self.styles['Normal']
                )
                story.append(cat_title)
                
                if isinstance(technologies, dict):
                    for key, value in technologies.items():
                        tech_item = Paragraph(
                            f"• <b>{key}:</b> {value}",
                            self.styles['Normal']
                        )
                        story.append(tech_item)
                        story.append(Spacer(1, 0.1*inch))
                else:
                    tech_item = Paragraph(f"• {technologies}", self.styles['Normal'])
                    story.append(tech_item)
                
                story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_deliverable_section(self, deliverable_plan):
        """Create deliverable plan section"""
        story = []
        
        title = Paragraph("5. Deliverable Plan & Milestones", self.styles['CustomHeading2'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Overview
        overview = deliverable_plan.get('deliverable-overview', 'N/A')
        if overview:
            p = Paragraph(overview, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Milestones
        title2 = Paragraph("5.1 Project Milestones", self.styles['Heading3'])
        story.append(title2)
        story.append(Spacer(1, 0.2*inch))
        
        milestones = deliverable_plan.get('key-milestones', [])
        if isinstance(milestones, list):
            for i, milestone in enumerate(milestones, 1):
                if isinstance(milestone, dict):
                    m_title = Paragraph(
                        f"<b>Milestone {i}: {milestone.get('milestone', 'N/A')}</b>",
                        self.styles['Normal']
                    )
                    story.append(m_title)
                    
                    timeline = Paragraph(
                        f"<i>Timeline: {milestone.get('timeline', 'N/A')}</i>",
                        self.styles['Normal']
                    )
                    story.append(timeline)
                    
                    deliverables = milestone.get('deliverables', [])
                    if isinstance(deliverables, list):
                        for d in deliverables:
                            d_item = Paragraph(f"• {d}", self.styles['Normal'])
                            story.append(d_item)
                    
                    story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Success criteria
        title3 = Paragraph("6. Success Criteria", self.styles['CustomHeading2'])
        story.append(title3)
        story.append(Spacer(1, 0.2*inch))
        
        criteria = deliverable_plan.get('success-criteria', [])
        if isinstance(criteria, list):
            for c in criteria:
                p = Paragraph(f"✓ {c}", self.styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_data_section(self, data_plan):
        """Create data plan section"""
        story = []
        
        title = Paragraph("7. Data Architecture", self.styles['CustomHeading2'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Data requirements
        req = data_plan.get('data-requirements', 'N/A')
        if req:
            p = Paragraph(req, self.styles['CustomBody'])
            story.append(p)
        
        story.append(Spacer(1, 0.3*inch))
        
        # Data schema
        title2 = Paragraph("7.1 Data Schema", self.styles['Heading3'])
        story.append(title2)
        story.append(Spacer(1, 0.2*inch))
        
        schema = data_plan.get('data-schema', {})
        if isinstance(schema, dict):
            for table_name, table_details in schema.items():
                table_title = Paragraph(
                    f"<b>{table_name.replace('-', ' ').title()}</b>",
                    self.styles['Normal']
                )
                story.append(table_title)
                
                if isinstance(table_details, dict):
                    fields = table_details.get('fields', {})
                    if isinstance(fields, dict):
                        for field_name, field_info in fields.items():
                            if isinstance(field_info, dict):
                                field_type = field_info.get('type', 'N/A')
                                field_text = Paragraph(
                                    f"• {field_name}: {field_type}",
                                    self.styles['Normal']
                                )
                            else:
                                field_text = Paragraph(
                                    f"• {field_name}: {field_info}",
                                    self.styles['Normal']
                                )
                            story.append(field_text)
                
                story.append(Spacer(1, 0.2*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Data governance
        title3 = Paragraph("8. Data Governance", self.styles['CustomHeading2'])
        story.append(title3)
        story.append(Spacer(1, 0.2*inch))
        
        governance = data_plan.get('data-governance', 'N/A')
        if governance:
            p = Paragraph(governance, self.styles['CustomBody'])
            story.append(p)
        
        return story
    
    def _create_architecture_section(self, image_url):
        """Create architecture diagram section with image from URL"""
        story = []
        
        title = Paragraph("4.5 System Architecture Diagram", self.styles['CustomHeading2'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        try:
            # Download image from URL
            import urllib.request
            from PIL import Image
            
            # Download image to bytes
            response = urllib.request.urlopen(image_url)
            image_bytes = io.BytesIO(response.read())
            
            # Get image dimensions
            img = Image.open(image_bytes)
            img_width, img_height = img.size
            
            # Calculate aspect ratio
            aspect_ratio = img_height / img_width
            
            # Set max width (6 inches for letter size with margins)
            max_width = 6 * inch
            img_width_pdf = max_width
            img_height_pdf = max_width * aspect_ratio
            
            # Reset buffer position
            image_bytes.seek(0)
            
            # Add image from bytes
            from reportlab.platypus import Image as RLImage
            
            rl_image = RLImage(image_bytes, width=img_width_pdf, height=img_height_pdf)
            story.append(rl_image)
            
            story.append(Spacer(1, 0.3*inch))
            
            caption = Paragraph(
                "<i>Figure 1: System Architecture Diagram - AI Generated</i>",
                self.styles['Normal']
            )
            story.append(caption)
            
        except Exception as e:
            # If image download fails, add error message instead
            error_text = Paragraph(
                f"<i>Architecture diagram could not be embedded. URL: {image_url}</i>",
                self.styles['Normal']
            )
            story.append(error_text)
        
        return story