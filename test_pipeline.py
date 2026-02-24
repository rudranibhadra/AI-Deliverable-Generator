from generator import DeliverableGenerator

generator = DeliverableGenerator()

try:
    result = generator.generate_full_deliverable_pipeline(
        deliverable_type="architecture",
        business_problem="Design a telemedicine platform supporting 100K users",
        tech_stack="Azure, Python, React",
        time_constraint="12 months",
        resource_constraints="8 developers"
    )
    
    print("\n" + "="*80)
    print("SUCCESS! Pipeline output:")
    print("="*80)
    print(f"Keys: {result.keys()}")
    print("\nProblem Requirements:", result.get("problem-requirements", {}).keys())
    print("Technical Plan:", result.get("technical-plan", {}).keys())
    print("Deliverable Plan:", result.get("deliverable-plan", {}).keys())
    print("Data Plan:", result.get("data-plan", {}).keys())
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")