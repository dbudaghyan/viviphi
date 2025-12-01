#!/usr/bin/env python3
"""Example script to animate the sample Mermaid graphs using viviphi."""

from pathlib import Path
from viviphi import (
    Graph,
    CYBERPUNK,
    CORPORATE,
    HAND_DRAWN,
    MANIM_CLASSIC,
    MANIM_LIGHT,
    MANIM_AQUA,
    MANIM_ORANGE,
    MANIM_PROOF,
    CYBERPUNK_GRID,
    GRADIENT_SUNSET,
    DOTTED_MINIMAL,
)


def animate_mermaid_files():
    """Process all sample Mermaid files and create animated SVGs."""
    samples_dir = Path(__file__).parent.parent / "resources" / "mermaid_graphs"
    output_dir = Path(__file__).parent.parent / "temp" / "sample_outputs"
    output_dir.mkdir(exist_ok=True)

    # Define themes to try
    themes = {
        "cyberpunk": CYBERPUNK,
        "corporate": CORPORATE,
        "hand_drawn": HAND_DRAWN,
        "manim_classic": MANIM_CLASSIC,
        "manim_light": MANIM_LIGHT,
        "manim_aqua": MANIM_AQUA,
        "manim_orange": MANIM_ORANGE,
        "manim_proof": MANIM_PROOF,
        "cyberpunk_grid": CYBERPUNK_GRID,
        "gradient_sunset": GRADIENT_SUNSET,
        "dotted_minimal": DOTTED_MINIMAL,
    }

    # Process each .mmd file
    for mmd_file in sorted(samples_dir.glob("*.mmd")):
        if "broken_syntax" in mmd_file.name:
            print(f"Skipping {mmd_file.name} (known broken syntax)")
            continue

        print(f"Processing {mmd_file.name}...")

        # Read the Mermaid definition
        mermaid_content = mmd_file.read_text(encoding="utf-8")

        # Create graph instance
        graph = Graph(mermaid_content)

        # Generate animated SVGs for each theme
        for theme_name, theme in themes.items():
            try:
                output_file = output_dir / f"{mmd_file.stem}_{theme_name}.svg"

                # Create animated SVG
                graph.animate(theme=theme, speed="normal", output=str(output_file))

                print(f"  ✅ Created {output_file.name}")

            except Exception as e:
                print(f"  ❌ Failed to create {theme_name} version: {e}")

    print(f"\nAnimated SVGs saved to: {output_dir}")


if __name__ == "__main__":
    animate_mermaid_files()
