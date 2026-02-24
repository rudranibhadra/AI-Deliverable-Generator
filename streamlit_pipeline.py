import streamlit as st
from generator import DeliverableGenerator
from pdf_generator import PDFGenerator 


st.set_page_config(page_title="AI Deliverable Generator", page_icon="🔄", layout="wide")

# Custom CSS for better formatting
st.markdown("""
<style>
    .step-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .content-box {
        background-color: #5b3c74;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .milestone-card {
        background: #75386d;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔄 AI Deliverable Generator")
st.markdown("*Transparent 6-step deliverable generation with AI*")

generator = DeliverableGenerator()

# Initialize PDF generator
pdf_gen = PDFGenerator()

# Sidebar inputs
with st.sidebar:
    # st.header("📝 Input Configuration")
    
    # deliverable_type = st.selectbox(
    #     "Deliverable Type",
    #     ["architecture", "summary", "roadmap", "data-schema"],
    #     help="Type of deliverable to generate"
    # )
    # Just show info about what will be generated
    st.info("""
    **Pipeline generates:**
    - Problem Requirements
    - Technical Plan
    - Deliverable Plan
    - Data Plan
    - Architecture Diagram
    """)
    
    st.markdown("---")
    
    business_problem = st.text_area(
        "Business Problem",
        value="Design a HIPAA-compliant telemedicine platform supporting 100K concurrent video consultations with 99.95% uptime. Must integrate with Epic/Cerner EHR systems and support real-time prescription routing.",
        height=150,
        help="Describe the business problem in detail"
    )
    
    tech_stack = st.text_area(
        "Tech Stack",
        value="Azure App Service, Azure Functions, Azure Health Data Services (FHIR), Azure Cosmos DB, Python 3.11 (FastAPI), React 18, WebRTC, Terraform",
        height=120,
        help="Technologies to be used"
    )
    
    time_constraint = st.text_input(
        "Time Constraint",
        "18 months in 5 agile phases: Discovery (3mo), MVP (5mo), Integrations (4mo), Security Audit (3mo), Rollout (3mo)"
    )
    
    resource_constraints = st.text_input(
        "Resource Constraints",
        "12-member team: 3 backend, 2 frontend, 2 integration specialists, 1 DevOps, 1 security architect, 2 QA, 1 product owner. Budget: $1.2M"
    )

# Main area
if st.button("🚀 Generate Pipeline Deliverable", type="primary", use_container_width=True):
    
    # Basic sanity checks
    if not business_problem.strip():
        st.error("❌ Business problem cannot be empty")
        st.stop()
    
    if not tech_stack.strip():
        st.error("❌ Tech stack cannot be empty")
        st.stop()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1
        status_text.text("⏳ Step 1/4: Generating Problem Requirements...")
        progress_bar.progress(10)
        
        problem_reqs = generator.generate_problem_requirements(
            business_problem, tech_stack, time_constraint, resource_constraints
        )
        progress_bar.progress(25)
        
        # Step 2
        status_text.text("⏳ Step 2/4: Generating Technical Plan...")
        technical_plan = generator.generate_technical_plan(problem_reqs)
        progress_bar.progress(50)
        
        # Step 3
        status_text.text("⏳ Step 3/4: Generating Deliverable Plan...")
        deliverable_plan = generator.generate_deliverable_plan(technical_plan)
        progress_bar.progress(75)
        
        # Step 4
        status_text.text("⏳ Step 4/4: Generating Data Plan...")
        data_plan = generator.generate_data_plan(technical_plan)
        progress_bar.progress(90)
        
        # Step 5
        status_text.text("⏳ Step 5/5: Generating Architecture Diagram...")
        technical_approach = technical_plan.get("technical-approach", "")
        architecture_diagram = None
        
        if technical_approach:
            image_prompt = generator._load_prompt(
                "prompts/step5_image_generation_prompt.txt",
                technical_approach=technical_approach
            )
            architecture_diagram = generator.generate_image(image_prompt)
        
        progress_bar.progress(100)
        status_text.text("✅ Generation Complete!")
        st.balloons()
        
        # Combine results
        content = {
            "problem-requirements": problem_reqs,
            "technical-plan": technical_plan,
            "deliverable-plan": deliverable_plan,
            "data-plan": data_plan
        }
        
        # Store in session state
        st.session_state['pipeline_content'] = content
        st.session_state['problem_reqs'] = problem_reqs
        st.session_state['technical_plan'] = technical_plan
        st.session_state['deliverable_plan'] = deliverable_plan
        st.session_state['data_plan'] = data_plan
        st.session_state['architecture_diagram'] = architecture_diagram
        st.session_state['pipeline_generated'] = True
        
    except Exception as e:
        st.error(f"❌ Pipeline generation failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

# ===========================
# DISPLAY RESULTS (OUTSIDE THE BUTTON CLICK)
# ===========================

if st.session_state.get('pipeline_generated'):
    
    # Retrieve from session state
    problem_reqs = st.session_state['problem_reqs']
    technical_plan = st.session_state['technical_plan']
    deliverable_plan = st.session_state['deliverable_plan']
    data_plan = st.session_state['data_plan']
    architecture_diagram = st.session_state.get('architecture_diagram')
    content = st.session_state['pipeline_content']
    
    st.markdown("---")
    
    # ===========================
    # STEP 1: PROBLEM REQUIREMENTS
    # ===========================
    st.markdown('<div class="step-header"><h2>📋 Step 1: Problem Requirements</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Executive Summary")
        st.markdown(f'<div class="content-box">{problem_reqs.get("executive-summary", "N/A")}</div>', unsafe_allow_html=True)
        
        st.markdown("### Problem Definition")
        st.markdown(f'<div class="content-box">{problem_reqs.get("problem-definition", "N/A")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Technical Solution")
        st.markdown(f'<div class="content-box">{problem_reqs.get("technical-solution", "N/A")}</div>', unsafe_allow_html=True)
        
        st.markdown("### Problem Requirements")
        requirements = problem_reqs.get("problem-requirements", [])
        if isinstance(requirements, list):
            req_html = "<div class='content-box'><ul>"
            for req in requirements:
                req_html += f"<li>{req}</li>"
            req_html += "</ul></div>"
            st.markdown(req_html, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="content-box">{requirements}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===========================
    # STEP 2: TECHNICAL PLAN
    # ===========================
    st.markdown('<div class="step-header"><h2>🔧 Step 2: Technical Plan</h2></div>', unsafe_allow_html=True)
    
    st.markdown("### Technical Approach")
    st.markdown(f'<div class="content-box">{technical_plan.get("technical-approach", "N/A")}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Architecture Overview")
        st.markdown(f'<div class="content-box">{technical_plan.get("architecture-overview", "N/A")}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Technology Stack")
        tech = technical_plan.get("technology-stack", {})
        if isinstance(tech, dict):
            for key, value in tech.items():
                st.markdown(f"**{key.replace('-', ' ').title()}:**")
                if isinstance(value, dict):
                    for k, v in value.items():
                        st.markdown(f"- *{k}:* {v}")
                else:
                    st.markdown(f'<div class="content-box">{value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="content-box">{tech}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===========================
    # STEP 3: DELIVERABLE PLAN
    # ===========================
    st.markdown('<div class="step-header"><h2>📦 Step 3: Deliverable Plan</h2></div>', unsafe_allow_html=True)
    
    st.markdown("### Deliverable Overview")
    st.markdown(f'<div class="content-box">{deliverable_plan.get("deliverable-overview", "N/A")}</div>', unsafe_allow_html=True)
    
    st.markdown("### Key Milestones")
    milestones = deliverable_plan.get("key-milestones", [])
    if isinstance(milestones, list):
        for i, milestone in enumerate(milestones, 1):
            if isinstance(milestone, dict):
                st.markdown(f"""
                <div class="milestone-card">
                    <h4>Milestone {i}: {milestone.get('milestone', 'N/A')}</h4>
                    <p><strong>Timeline:</strong> {milestone.get('timeline', 'N/A')}</p>
                    <p><strong>Deliverables:</strong></p>
                    <ul>
                """, unsafe_allow_html=True)
                
                deliverables = milestone.get('deliverables', [])
                if isinstance(deliverables, list):
                    for d in deliverables:
                        st.markdown(f"<li>{d}</li>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<li>{deliverables}</li>", unsafe_allow_html=True)
                
                st.markdown("</ul></div>", unsafe_allow_html=True)
    
    st.markdown("### Success Criteria")
    criteria = deliverable_plan.get("success-criteria", [])
    if isinstance(criteria, list):
        criteria_html = "<div class='content-box'><ul>"
        for c in criteria:
            criteria_html += f"<li>✅ {c}</li>"
        criteria_html += "</ul></div>"
        st.markdown(criteria_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===========================
    # STEP 4: DATA PLAN
    # ===========================
    st.markdown('<div class="step-header"><h2>📊 Step 4: Data Plan</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Data Requirements")
        st.markdown(f'<div class="content-box">{data_plan.get("data-requirements", "N/A")}</div>', unsafe_allow_html=True)
        
        st.markdown("### Data Sources")
        sources = data_plan.get("data-sources", "N/A")
        if isinstance(sources, list):
            sources_html = "<div class='content-box'><ul>"
            for s in sources:
                sources_html += f"<li>{s}</li>"
            sources_html += "</ul></div>"
            st.markdown(sources_html, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="content-box">{sources}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Data Schema")
        schema = data_plan.get("data-schema", {})
        
        import pandas as pd
        
        if isinstance(schema, dict):
            for entity_name, entity_details in schema.items():
                st.markdown(f"#### 📋 {entity_name.replace('-', ' ').replace('_', ' ').title()}")
                
                fields = None
                if isinstance(entity_details, dict):
                    fields = (entity_details.get('fields') or 
                             entity_details.get('columns') or 
                             entity_details.get('attributes') or 
                             entity_details.get('properties'))
                
                if fields and isinstance(fields, dict):
                    rows = []
                    for field_name, field_info in fields.items():
                        if isinstance(field_info, dict):
                            rows.append({
                                "Field": field_name,
                                "Type": field_info.get('type', 'N/A'),
                                "Required": "✓" if field_info.get('required') else "",
                                "Description": field_info.get('description', 'N/A')
                            })
                        else:
                            rows.append({
                                "Field": field_name,
                                "Type": str(field_info),
                                "Required": "",
                                "Description": "N/A"
                            })
                    
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("### Data Governance")
        st.markdown(f'<div class="content-box">{data_plan.get("data-governance", "N/A")}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===========================
    # STEP 5: ARCHITECTURE DIAGRAM
    # ===========================
    st.markdown('<div class="step-header"><h2>🎨 Step 5: Architecture Diagram</h2></div>', unsafe_allow_html=True)
    
    if architecture_diagram:
        st.image(architecture_diagram, caption="System Architecture Diagram", use_container_width=True)
        st.markdown(f"[🔗 Open Full Size]({architecture_diagram})")
    else:
        st.info("ℹ️ Architecture diagram was not generated")
    
    st.markdown("---")
    
    # ===========================
    # EXPORT OPTIONS
    # ===========================
    st.markdown("## 📊 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Slide Deck", use_container_width=True):
            with st.spinner("AI is creating your presentation slides... (~15 seconds)"):
                try:
                    slides = generator.generate_slides(content)
                    
                    st.success(f"✅ Generated {len(slides)} presentation slides!")
                    
                    tab_labels = [f"Slide {s.get('slide_number', i)}" for i, s in enumerate(slides, 1)]
                    tabs = st.tabs(tab_labels)
                    
                    for tab, slide in zip(tabs, slides):
                        with tab:
                            st.markdown(f"## {slide.get('title', 'Untitled')}")
                            st.markdown(slide.get('content', ''))
                            
                            if slide.get('speaker_notes'):
                                st.markdown("---")
                                st.caption("🎤 **Speaker Notes:**")
                                st.caption(slide['speaker_notes'])
                    
                    st.session_state['pipeline_slides'] = slides
                    
                    import json
                    slides_json = json.dumps(slides, indent=2)
                    st.download_button(
                        label="📥 Download Slides (JSON)",
                        data=slides_json,
                        file_name="presentation_slides.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Slide generation failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with col2:
        import json
        json_str = json.dumps(content, indent=2)
        st.download_button(
            label="💾 Download Pipeline Output",
            data=json_str,
            file_name="pipeline_deliverable.json",
            mime="application/json",
            use_container_width=True
        )

    with col3:
        if st.button("📄 Download PDF", use_container_width=True):
            with st.spinner("Generating PDF... (~5 seconds)"):
                try:
                    # Get the architecture diagram URL from session state
                    architecture_diagram = st.session_state.get('architecture_diagram')
                    
                    # Pass image URL to PDF generator
                    pdf_bytes = pdf_gen.generate_pdf(
                        content,
                        image_url=architecture_diagram
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name="pipeline_deliverable.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ PDF generation failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())