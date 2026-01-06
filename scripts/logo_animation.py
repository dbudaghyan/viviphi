#!/usr/bin/env python3
"""Create an animated logo for the viviphi library using itself."""

from pathlib import Path
from viviphi import Graph, CYBERPUNK, GRADIENT_SUNSET, MANIM_CLASSIC


def create_viviphi_logo():
    """Create an animated logo with 'vivi' and phi symbol using Mermaid."""

    # Mermaid diagram representing the viviphi logo
    logo_mermaid = """
    graph LR
        V1["v"] --> I1["i"]
        I1 --> V2["v"]
        V2 --> I2["i"]
        I2 --> PHI["φ"]
        
        style V1 fill:#ff6b6b,stroke:#333,stroke-width:3px,color:#fff
        style I1 fill:#4ecdc4,stroke:#333,stroke-width:3px,color:#fff
        style V2 fill:#ff6b6b,stroke:#333,stroke-width:3px,color:#fff
        style I2 fill:#4ecdc4,stroke:#333,stroke-width:3px,color:#fff
        style PHI fill:#ffd93d,stroke:#333,stroke-width:4px,color:#333,font-size:24px
    """

    # Output directory
    output_dir = Path("examples/outputs")
    output_dir.mkdir(exist_ok=True)

    # Create the graph
    graph = Graph(logo_mermaid)

    # Create animations with different themes
    themes = {
        "cyberpunk": CYBERPUNK,
        "gradient_sunset": GRADIENT_SUNSET,
        "classic": MANIM_CLASSIC,
    }

    print("Creating viviphi animated logos...")

    for theme_name, theme in themes.items():
        output_file = output_dir / f"viviphi_logo_{theme_name}.svg"

        print(f"  • Generating {theme_name} theme -> {output_file.name}")

        graph.animate(theme=theme, speed="normal", output=str(output_file))

    print(f"\nAnimated logos created in {output_dir}/")
    print("Logo files:")
    for theme_name in themes.keys():
        print(f"  - viviphi_logo_{theme_name}.svg")


if __name__ == "__main__":
    create_viviphi_logo()
