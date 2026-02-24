def _format_tech_stack(tech_stack):
    """Format technology stack dictionary into readable text"""
    if not isinstance(tech_stack, dict):
        return str(tech_stack)
    
    formatted = []
    for category, technologies in tech_stack.items():
        formatted.append(f"\n**{category.replace('-', ' ').title()}:**")
        if isinstance(technologies, dict):
            for key, value in technologies.items():
                formatted.append(f"  • {key}: {value}")
        else:
            formatted.append(f"  • {technologies}")
    
    return "\n".join(formatted)

def _format_milestones(milestones):
    """Format milestones array into readable text"""
    if not isinstance(milestones, list):
        return str(milestones)
    
    formatted = []
    for i, milestone in enumerate(milestones, 1):
        if isinstance(milestone, dict):
            formatted.append(f"\n**Milestone {i}: {milestone.get('milestone', 'N/A')}**")
            formatted.append(f"Timeline: {milestone.get('timeline', 'N/A')}")
            
            deliverables = milestone.get('deliverables', [])
            if isinstance(deliverables, list):
                formatted.append("Deliverables:")
                for d in deliverables:
                    formatted.append(f"  • {d}")
            else:
                formatted.append(f"Deliverables: {deliverables}")
        else:
            formatted.append(f"• {milestone}")
    
    return "\n".join(formatted)

def _format_data_schema(data_schema):
    """Format data schema into readable text"""
    if not isinstance(data_schema, dict):
        return str(data_schema)
    
    formatted = []
    for table_name, table_details in data_schema.items():
        formatted.append(f"\n**{table_name.replace('-', ' ').replace('_', ' ').title()}**")
        
        if isinstance(table_details, dict):
            # Get description if exists
            if table_details.get('description'):
                formatted.append(f"  {table_details['description']}")
            
            # Get fields
            fields = table_details.get('fields') or table_details.get('columns') or table_details.get('attributes')
            if isinstance(fields, dict):
                formatted.append("  Fields:")
                for field_name, field_info in list(fields.items())[:5]:  # Limit to 5 fields
                    if isinstance(field_info, dict):
                        field_type = field_info.get('type', 'N/A')
                        formatted.append(f"    • {field_name}: {field_type}")
                    else:
                        formatted.append(f"    • {field_name}: {field_info}")
        else:
            formatted.append(f"  {table_details}")
    
    return "\n".join(formatted)