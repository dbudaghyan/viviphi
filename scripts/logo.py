#!/usr/bin/env python3
"""Create the viviphi logo - fast network design with neon theme."""

from pathlib import Path
from viviphi import (
    Graph,
    Theme,
    BackgroundStyling,
    EdgeStyling,
    NodeStyling,
    AnimationStyling,
)


def create_logo():
    """Create the viviphi logo with fast network neon design."""

    output_dir = Path("examples/outputs")
    output_dir.mkdir(exist_ok=True)

    # Network design with v,i,v,i,φ structure
    logo_mermaid = """
    graph LR
        V1["v"] 
        I1["i"]
        V2["v"]
        I2["i"]
        PHI["φ"]
        
        V1 --> I1
        V1 --> V2
        V1 --> PHI
        I1 --> V2
        I1 --> I2
        I1 --> PHI
        V2 --> I2
        V2 --> PHI
        I2 --> PHI
        
        style V1 fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
        style I1 fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
        style V2 fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
        style I2 fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
        style PHI fill:#ffd93d,stroke:#333,stroke-width:4px,color:#333,font-size:28px
    """

    # Fast neon theme
    theme = Theme(
        primary_color="#00ffff",
        secondary_color="#ff00ff",
        text_color="#ffffff",
        background=BackgroundStyling(
            color="#000011",
            pattern="grid",
            pattern_color="rgba(0, 255, 255, 0.05)",
            pattern_size=20.0,
        ),
        edges=EdgeStyling(
            style="neon", width=1.5, glow_enabled=True, glow_intensity=8.0, opacity=0.8
        ),
        nodes=NodeStyling(
            style="glass",
            border_width=2.0,
            shadow=True,
            shadow_color="rgba(0, 255, 255, 0.4)",
            opacity=0.9,
        ),
        animation=AnimationStyling(duration=0.8, stagger_delay=0.08, easing="ease-out"),
    )

    # Create the logo
    graph = Graph(logo_mermaid)
    output_file = output_dir / "viviphi_logo.svg"

    graph.animate(theme=theme, speed="normal", output=str(output_file), delay=1)
    print(f"Logo created: {output_file}")


if __name__ == "__main__":
    create_logo()
