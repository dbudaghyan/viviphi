#!/usr/bin/env python3
"""Example script to animate the sample Mermaid graphs using viviphi."""

import multiprocessing as mp
from pathlib import Path
from typing import Any, Tuple
from viviphi import (
    Graph,
    OrderType,
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


def process_file_theme(args: Tuple[Path, str, Any, Path]) -> Tuple[str, bool, str]:
    """Worker function to process a single file-theme combination."""
    mmd_file, theme_name, theme, output_dir = args

    try:
        # Read the Mermaid definition
        mermaid_content = mmd_file.read_text(encoding="utf-8")

        # Create graph instance
        graph = Graph(mermaid_content)

        # Create output filename
        output_file = output_dir / f"{mmd_file.stem}_{theme_name}.svg"

        # Create animated SVG
        graph.animate(
            theme=theme,
            speed="fast",
            output=str(output_file),
            order_type=OrderType.RANDOM,
        )

        return f"{mmd_file.name} - {theme_name}", True, f"✅ Created {output_file.name}"

    except Exception as e:
        return (
            f"{mmd_file.name} - {theme_name}",
            False,
            f"❌ Failed to create {theme_name} version: {e}",
        )


def animate_mermaid_files():
    """Process all sample Mermaid files and create animated SVGs using multiprocessing."""
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

    # Collect all file-theme combinations to process
    tasks = []
    valid_files = []

    for mmd_file in sorted(samples_dir.glob("*.mmd")):
        if "broken_syntax" in mmd_file.name:
            print(f"Skipping {mmd_file.name} (known broken syntax)")
            continue
        valid_files.append(mmd_file)

        for theme_name, theme in themes.items():
            tasks.append((mmd_file, theme_name, theme, output_dir))

    print(f"Processing {len(valid_files)} files with {len(themes)} themes each...")
    print(f"Total tasks: {len(tasks)}")

    # Process tasks in parallel
    cpu_count = mp.cpu_count()
    with mp.Pool(processes=cpu_count) as pool:
        results = pool.map(process_file_theme, tasks)

    # Display results
    success_count = 0
    for task_name, success, message in results:
        if success:
            success_count += 1
        print(f"  {message}")

    print(f"\nCompleted: {success_count}/{len(tasks)} animations")
    print(f"Animated SVGs saved to: {output_dir}")


if __name__ == "__main__":
    animate_mermaid_files()
