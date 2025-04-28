#!/usr/bin/env python3
"""
SmartSDLC: An Agent-Based UML Generator and SDLC Model Advisor
Command-line interface to run the application without Streamlit
Using locally installed Qwen 2.5:3B model via Ollama
"""

import argparse
import json
import os
from PIL import Image

# Import local modules
from model_api import call_model
from crew_orchestration import run_crew_task
from diagram_renderer import generate_plantuml_url, render_diagram

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="SmartSDLC: Generate UML diagrams and get SDLC recommendations"
    )
    
    parser.add_argument(
        "--description", "-d",
        type=str, 
        required=True,
        help="Software product description"
    )
    
    parser.add_argument(
        "--diagram-type", "-t",
        type=str,
        choices=["Use Case", "Class", "Sequence", "Component", "Communication", "State Machine"],
        default="Class",
        help="UML diagram type (default: Class)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Output directory for results (default: 'output')"
    )
    
    parser.add_argument(
        "--save-image", "-i",
        action="store_true",
        help="Save the rendered diagram image"
    )
    
    parser.add_argument(
        "--temperature", 
        type=float,
        default=0.7,
        help="Temperature for model generation (default: 0.7)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2000,
        help="Maximum tokens to generate (default: 2000)"
    )
    
    return parser.parse_args()

def main():
    """Main function to run the application"""
    args = parse_arguments()
    
    print(f"Processing request for {args.diagram_type} diagram...\n")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Run crew task
    result = run_crew_task(
        args.description, 
        args.diagram_type,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    if result and 'sdlc_recommendation' in result and 'plantuml_code' in result:
        # Save SDLC recommendation
        sdlc_file = os.path.join(args.output_dir, "sdlc_recommendation.txt")
        with open(sdlc_file, "w") as f:
            f.write(result['sdlc_recommendation'])
        print(f"SDLC recommendation saved to {sdlc_file}")
        
        # Save PlantUML code
        uml_file = os.path.join(args.output_dir, "plantuml_code.txt")
        with open(uml_file, "w") as f:
            f.write(result['plantuml_code'])
        print(f"PlantUML code saved to {uml_file}")
        
        # Generate PlantUML URL
        plantuml_url = generate_plantuml_url(result['plantuml_code'])
        print(f"PlantUML URL: {plantuml_url}")
        
        # Save image if requested
        if args.save_image:
            try:
                image = render_diagram(result['plantuml_code'])
                image_file = os.path.join(args.output_dir, "diagram.png")
                image.save(image_file)
                print(f"Diagram image saved to {image_file}")
            except Exception as e:
                print(f"Error rendering diagram: {str(e)}")
        
        # Save full results as JSON
        json_file = os.path.join(args.output_dir, "results.json")
        with open(json_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Full results saved to {json_file}")
        
        # Print summary
        print("\n===== SDLC Recommendation =====")
        print(result['sdlc_recommendation'][:500] + "..." if len(result['sdlc_recommendation']) > 500 else result['sdlc_recommendation'])
        
    else:
        print("Error: Failed to generate results")

if __name__ == "__main__":
    main()