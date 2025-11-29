#!/usr/bin/env python3
"""Test the semantic direction fix for class diagram arrows."""

from viviphi import Graph
from pathlib import Path


def test_class_diagram_fix():
    """Test that class diagram extension arrows animate correctly."""
    
    # Read the problematic class diagram
    mermaid_file = Path("resources/mermaid_graphs/06_class_diagram.mmd")
    mermaid_content = mermaid_file.read_text()
    
    print("Original Mermaid definition:")
    print(mermaid_content)
    print("\n" + "="*50 + "\n")
    
    # Generate animated SVG with semantic fixes
    graph = Graph(mermaid_content)
    animated_svg = graph.animate()
    
    # Save output for inspection
    output_file = Path("temp/semantic_test_output.svg")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(animated_svg)
    
    print(f"Generated animated SVG: {output_file}")
    
    # Check if semantic attributes were injected
    if "data-flow-direction" in animated_svg:
        print("✅ Semantic direction attributes successfully injected!")
    else:
        print("❌ Semantic direction attributes not found")
    
    if "data-source-node" in animated_svg:
        print("✅ Source node metadata successfully injected!")
    else:
        print("❌ Source node metadata not found")
    
    # Look for specific patterns that should be fixed
    extension_patterns = animated_svg.count("data-edge-type=\"extension\"")
    print(f"Found {extension_patterns} extension edges with metadata")
    
    return animated_svg


if __name__ == "__main__":
    test_class_diagram_fix()