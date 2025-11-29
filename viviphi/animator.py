"""SVG Animation engine for transforming static SVGs into animated ones."""

import xml.etree.ElementTree as ET
from typing import Optional, TYPE_CHECKING
from svgpathtools import parse_path

if TYPE_CHECKING:
    from .themes import Theme


class SVGAnimator:
    """Transforms static SVG content into CSS-animated SVG."""
    
    def __init__(self, static_svg_content: str) -> None:
        """Initialize with static SVG content.
        
        Args:
            static_svg_content: Raw SVG string content
        """
        # Register namespace to prevent ns0: prefixes in output
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        self.root = ET.fromstring(static_svg_content)
        self.ns = {'svg': 'http://www.w3.org/2000/svg'}

    def _get_css_template(self) -> str:
        """Returns the CSS block for the animations."""
        return """
            /* Base Line Style */
            .anim-edge {
                stroke-dasharray: var(--length);
                stroke-dashoffset: var(--length);
                animation: draw-flow 1.5s ease-out forwards;
                opacity: 0.8;
            }
            
            /* The Draw Animation */
            @keyframes draw-flow {
                to { stroke-dashoffset: 0; }
            }
            
            /* Node Entrance Animation */
            .anim-node {
                opacity: 0;
                animation: fade-in 0.5s ease-out forwards;
            }
            
            @keyframes fade-in {
                to { opacity: 1; }
            }
            
            /* Glow Filter Effect */
            .neon-glow {
                filter: drop-shadow(0 0 5px var(--glow-color, #00ffcc));
            }
        """

    def process(self, color: str = "#00ffcc") -> str:
        """Process the SVG to add animations.
        
        Args:
            color: Primary color for animations and glow effects
            
        Returns:
            Animated SVG as string
        """
        # 1. Inject CSS
        style_el = ET.Element('style')
        style_el.text = self._get_css_template()
        self.root.insert(0, style_el)

        # 2. Process Paths (Edges)
        paths = self.root.findall('.//svg:path', self.ns)
        for i, path in enumerate(paths):
            d_string = path.get('d')
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()
                
                # Logic: Nodes appear, then lines draw connecting them
                # Delay based on index to create "waterfall"
                delay = i * 0.3 
                
                existing_style = path.get('style', '')
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {color}; "
                    f"animation-delay: {delay}s;"
                )
                
                path.set('style', new_style)
                path.set('class', 'anim-edge neon-glow')
                
                # Enforce styling overrides for consistency
                path.set('stroke', color)
                path.set('fill', 'none')
                
            except Exception as e:
                print(f"Skipping complex path {i}: {e}")

        return ET.tostring(self.root, encoding='unicode')
    
    def process_with_theme(self, theme: "Theme") -> str:
        """Process the SVG with a specific theme.
        
        Args:
            theme: Theme object containing styling preferences
            
        Returns:
            Animated SVG as string
        """
        # 1. Inject theme CSS
        style_el = ET.Element('style')
        style_el.text = theme.get_css_template()
        self.root.insert(0, style_el)

        # 2. Process Paths (Edges)
        paths = self.root.findall('.//svg:path', self.ns)
        for i, path in enumerate(paths):
            d_string = path.get('d')
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()
                
                # Apply theme-based delay
                delay = i * theme.stagger_delay
                
                existing_style = path.get('style', '')
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {theme.primary_color}; "
                    f"animation-delay: {delay}s;"
                )
                
                path.set('style', new_style)
                
                # Apply theme-specific classes
                if theme.edge_style == "neon":
                    path.set('class', 'anim-edge neon-glow')
                elif theme.edge_style == "hand-drawn":
                    path.set('class', 'anim-edge hand-drawn')
                else:
                    path.set('class', 'anim-edge clean-edge')
                
                # Enforce styling overrides for consistency
                path.set('stroke', theme.primary_color)
                path.set('fill', 'none')
                
            except Exception as e:
                print(f"Skipping complex path {i}: {e}")

        # 3. Process nodes (rectangles, circles, etc.)
        nodes = (
            self.root.findall('.//svg:rect', self.ns) +
            self.root.findall('.//svg:circle', self.ns) +
            self.root.findall('.//svg:ellipse', self.ns) +
            self.root.findall('.//svg:polygon', self.ns)
        )
        
        for i, node in enumerate(nodes):
            delay = i * theme.stagger_delay * 0.5  # Nodes appear before edges
            
            existing_style = node.get('style', '')
            new_style = f"{existing_style}; animation-delay: {delay}s;"
            node.set('style', new_style)
            
            # Apply theme-specific node classes
            if theme.node_style == "glass":
                node.set('class', 'anim-node glass-node')
            elif theme.node_style == "outlined":
                node.set('class', 'anim-node outlined-node')
            else:
                node.set('class', 'anim-node solid-node')

        return ET.tostring(self.root, encoding='unicode')