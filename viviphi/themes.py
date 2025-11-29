"""Theme system for defining visual styles and animations."""

from typing import Literal
from pydantic import BaseModel


class Theme(BaseModel):
    """Defines visual theme for graph animations."""

    primary_color: str = "#00ff99"
    background: str = "#1a1a1a"
    edge_style: Literal["neon", "clean", "hand-drawn"] = "neon"
    node_style: Literal["glass", "solid", "outlined"] = "glass"
    animation_duration: float = 1.5
    stagger_delay: float = 0.3

    def get_css_template(self) -> str:
        """Generate CSS template based on theme settings."""
        base_css = f"""
            /* Theme: {self.edge_style} / {self.node_style} */
            .anim-edge {{
                stroke-dasharray: var(--length);
                stroke-dashoffset: var(--length);
                animation: draw-flow-with-markers {self.animation_duration}s ease-out forwards;
                opacity: 0.8;
            }}
            
            /* The Draw Animation with marker reveal */
            @keyframes draw-flow-with-markers {{
                0% {{ 
                    stroke-dashoffset: var(--length);
                    marker-start: none;
                    marker-end: none;
                }}
                99% {{ 
                    stroke-dashoffset: 0;
                    marker-start: none;
                    marker-end: none;
                }}
                100% {{ 
                    stroke-dashoffset: 0;
                    marker-start: var(--marker-start, none);
                    marker-end: var(--marker-end, none);
                }}
            }}
            
            .anim-node {{
                opacity: 0;
                animation: fade-in 0.5s ease-out forwards;
            }}
            
            @keyframes fade-in {{
                to {{ opacity: 1; }}
            }}
        """

        if self.edge_style == "neon":
            base_css += f"""
            .neon-glow {{
                filter: drop-shadow(0 0 5px var(--glow-color, {self.primary_color})) 
                        drop-shadow(0 0 10px var(--glow-color, {self.primary_color})) 
                        drop-shadow(0 0 15px var(--glow-color, {self.primary_color}));
                stroke-width: 2px;
            }}
            """
        elif self.edge_style == "hand-drawn":
            base_css += """
            .hand-drawn {
                stroke-linecap: round;
                stroke-linejoin: round;
                filter: url(#rough);
            }
            """
        elif self.edge_style == "clean":
            base_css += """
            .clean-edge {
                stroke-width: 1.5px;
                opacity: 0.9;
            }
            """

        if self.node_style == "glass":
            base_css += f"""
            .glass-node {{
                fill: rgba(255, 255, 255, 0.1);
                stroke: {self.primary_color};
                stroke-width: 2px;
                backdrop-filter: blur(10px);
            }}
            """
        elif self.node_style == "outlined":
            base_css += f"""
            .outlined-node {{
                fill: none;
                stroke: {self.primary_color};
                stroke-width: 2px;
            }}
            """
        elif self.node_style == "solid":
            base_css += f"""
            .solid-node {{
                fill: {self.primary_color};
                stroke: none;
            }}
            """

        return base_css


# Predefined themes
CYBERPUNK = Theme(
    primary_color="#00ff99", background="#1a1a1a", edge_style="neon", node_style="glass"
)

CORPORATE = Theme(
    primary_color="#2563eb",
    background="#ffffff",
    edge_style="clean",
    node_style="solid",
    animation_duration=1.0,
    stagger_delay=0.2,
)

HAND_DRAWN = Theme(
    primary_color="#374151",
    background="#f9fafb",
    edge_style="hand-drawn",
    node_style="outlined",
    animation_duration=2.0,
    stagger_delay=0.4,
)
