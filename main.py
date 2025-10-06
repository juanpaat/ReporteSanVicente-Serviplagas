"""
Original report generation script - now uses the refactored report_generator module
This script maintains backward compatibility while leveraging the new modular structure
"""

from report_generator import generate_report_for_locations


def main():
    """
    Main function to generate reports for both locations
    Maintains the same behavior as the original script
    """
    try:
        print("🚀 Starting report generation...")
        print("📍 Processing both locations: Medellín and Rionegro")
        
        # Generate report for both locations (same as original behavior)
        filename = generate_report_for_locations(
            locations=["Medellín", "Rionegro"],
            mes_excluir='Oct 2025',
            template_path='Plantilla.docx',
            return_buffer=False  # Save to file instead of returning buffer
        )
        
        print(f"✅ Report generation completed successfully!")
        print(f"📄 Output file: {filename}")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        raise


if __name__ == "__main__":
    main()