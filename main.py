from generator import DeliverableGenerator


def main():
    """Main entry point for the AI Deliverable Generator CLI."""
    # Initialize the generator
    generator = DeliverableGenerator()
    
    # Get user input
    user_request = input(
        "\nWhat would you like to generate? "
        "(e.g., 'Executive summary for client'):\n"
    )
    
    try:
        # Generate deliverable
        output = generator.generate_deliverable(user_request)
        
        # Display result
        print("\nGenerated client-ready content:\n")
        print(output)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
