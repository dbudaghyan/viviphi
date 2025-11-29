"""SVG Animation engine for transforming static SVGs into animated ones."""

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING
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
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        self.root = ET.fromstring(static_svg_content)
        self.ns = {"svg": "http://www.w3.org/2000/svg"}

    def _get_css_template(self) -> str:
        """Returns the CSS block for the animations."""
        return """
            /* Base Line Style - hide markers initially */
            .anim-edge {
                stroke-dasharray: var(--length);
                stroke-dashoffset: var(--length);
                animation: draw-flow-with-markers 1.5s ease-out forwards;
                opacity: 0.8;
            }
            
            /* The Draw Animation with marker reveal */
            @keyframes draw-flow-with-markers {
                0% { 
                    stroke-dashoffset: var(--length);
                    marker-start: none;
                    marker-end: none;
                }
                99% { 
                    stroke-dashoffset: 0;
                    marker-start: none;
                    marker-end: none;
                }
                100% { 
                    stroke-dashoffset: 0;
                    marker-start: var(--marker-start, none);
                    marker-end: var(--marker-end, none);
                }
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
        style_el = ET.Element("style")
        style_el.text = self._get_css_template()
        self.root.insert(0, style_el)

        # 2. Process Paths (Edges) - separate line paths from arrow tip paths
        all_paths = self.root.findall(".//svg:path", self.ns)

        # Find paths inside markers (arrow tips)
        marker_paths = self.root.findall(".//svg:marker//svg:path", self.ns)
        marker_path_set = set(marker_paths)

        # Separate paths into lines (outside markers) and arrow tips (inside markers)
        line_paths = []
        arrow_tip_paths = []

        for path in all_paths:
            if path in marker_path_set:
                arrow_tip_paths.append(path)
            else:
                line_paths.append(path)

        # Process line paths first
        for i, path in enumerate(line_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Logic: Nodes appear, then lines draw connecting them
                # Delay based on index to create "waterfall"
                delay = i * 0.3

                # Store original marker attributes and remove them temporarily
                marker_start = path.get("marker-start", "none")
                marker_end = path.get("marker-end", "none")

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {color}; "
                    f"--marker-start: {marker_start}; "
                    f"--marker-end: {marker_end}; "
                    f"animation-delay: {delay}s;"
                )

                path.set("style", new_style)
                path.set("class", "anim-edge neon-glow")

                # Remove marker attributes so they start hidden
                if marker_start != "none":
                    path.attrib.pop("marker-start", None)
                if marker_end != "none":
                    path.attrib.pop("marker-end", None)

                # Enforce styling overrides for consistency
                path.set("stroke", color)
                path.set("fill", "none")

            except Exception as e:
                print(f"Skipping complex line path {i}: {e}")

        # Process arrow tip paths after lines with additional delay
        for i, path in enumerate(arrow_tip_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Arrow tips animate after lines finish
                # Add extra delay so arrow tips appear after lines are drawn
                base_line_delay = len(line_paths) * 0.3
                arrow_delay = base_line_delay + (i * 0.1)  # Faster stagger for tips

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {color}; "
                    f"animation-delay: {arrow_delay}s;"
                )

                path.set("style", new_style)
                path.set("class", "anim-edge neon-glow")

                # Enforce styling overrides for consistency
                path.set("stroke", color)
                path.set("fill", "none")

            except Exception as e:
                print(f"Skipping complex arrow tip path {i}: {e}")

        # Process non-path arrow tip elements (circles, rects, etc.) after lines
        marker_elements = (
            self.root.findall(".//svg:marker//svg:rect", self.ns)
            + self.root.findall(".//svg:marker//svg:circle", self.ns)
            + self.root.findall(".//svg:marker//svg:ellipse", self.ns)
            + self.root.findall(".//svg:marker//svg:polygon", self.ns)
        )

        for i, element in enumerate(marker_elements):
            # Arrow tip elements animate after lines and path arrow tips
            base_delay = len(line_paths) * 0.3 + len(arrow_tip_paths) * 0.1
            arrow_delay = base_delay + (
                i * 0.05
            )  # Even faster stagger for non-path tips

            existing_style = element.get("style", "")
            new_style = f"{existing_style}; animation-delay: {arrow_delay}s;"
            element.set("style", new_style)

            # Apply edge class for arrow tips (not node class)
            element.set("class", "anim-edge neon-glow")

        return ET.tostring(self.root, encoding="unicode")

    def process_with_theme(self, theme: "Theme") -> str:
        """Process the SVG with a specific theme.

        Args:
            theme: Theme object containing styling preferences

        Returns:
            Animated SVG as string
        """
        # 1. Inject theme CSS
        style_el = ET.Element("style")
        style_el.text = theme.get_css_template()
        self.root.insert(0, style_el)

        # 2. Process Paths (Edges) - separate line paths from arrow tip paths
        all_paths = self.root.findall(".//svg:path", self.ns)

        # Find paths inside markers (arrow tips)
        marker_paths = self.root.findall(".//svg:marker//svg:path", self.ns)
        marker_path_set = set(marker_paths)

        # Separate paths into lines (outside markers) and arrow tips (inside markers)
        line_paths = []
        arrow_tip_paths = []

        for path in all_paths:
            if path in marker_path_set:
                arrow_tip_paths.append(path)
            else:
                line_paths.append(path)

        # Process line paths first
        for i, path in enumerate(line_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Apply theme-based delay for lines
                delay = i * theme.stagger_delay

                # Store original marker attributes and remove them temporarily
                marker_start = path.get("marker-start", "none")
                marker_end = path.get("marker-end", "none")

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {theme.primary_color}; "
                    f"--marker-start: {marker_start}; "
                    f"--marker-end: {marker_end}; "
                    f"animation-delay: {delay}s;"
                )

                path.set("style", new_style)

                # Apply theme-specific classes
                if theme.edge_style == "neon":
                    path.set("class", "anim-edge neon-glow")
                elif theme.edge_style == "hand-drawn":
                    path.set("class", "anim-edge hand-drawn")
                else:
                    path.set("class", "anim-edge clean-edge")

                # Remove marker attributes so they start hidden
                if marker_start != "none":
                    path.attrib.pop("marker-start", None)
                if marker_end != "none":
                    path.attrib.pop("marker-end", None)

                # Enforce styling overrides for consistency
                path.set("stroke", theme.primary_color)
                path.set("fill", "none")

            except Exception as e:
                print(f"Skipping complex line path {i}: {e}")

        # Process arrow tip paths after lines with additional delay
        for i, path in enumerate(arrow_tip_paths):
            d_string = path.get("d")
            if not d_string:
                continue

            try:
                # Calculate geometry using svgpathtools
                path_obj = parse_path(d_string)
                length = path_obj.length()

                # Arrow tips animate after lines finish
                # Add extra delay so arrow tips appear after lines are drawn
                base_line_delay = len(line_paths) * theme.stagger_delay
                arrow_delay = base_line_delay + (
                    i * theme.stagger_delay * 0.2
                )  # Faster stagger for tips

                existing_style = path.get("style", "")
                new_style = (
                    f"{existing_style}; "
                    f"--length: {length:.2f}; "
                    f"--glow-color: {theme.primary_color}; "
                    f"animation-delay: {arrow_delay}s;"
                )

                path.set("style", new_style)

                # Apply theme-specific classes
                if theme.edge_style == "neon":
                    path.set("class", "anim-edge neon-glow")
                elif theme.edge_style == "hand-drawn":
                    path.set("class", "anim-edge hand-drawn")
                else:
                    path.set("class", "anim-edge clean-edge")

                # Enforce styling overrides for consistency
                path.set("stroke", theme.primary_color)
                path.set("fill", "none")

            except Exception as e:
                print(f"Skipping complex arrow tip path {i}: {e}")

        # Process non-path arrow tip elements (circles, rects, etc.) after lines
        marker_elements = (
            self.root.findall(".//svg:marker//svg:rect", self.ns)
            + self.root.findall(".//svg:marker//svg:circle", self.ns)
            + self.root.findall(".//svg:marker//svg:ellipse", self.ns)
            + self.root.findall(".//svg:marker//svg:polygon", self.ns)
        )

        for i, element in enumerate(marker_elements):
            # Arrow tip elements animate after lines and path arrow tips
            base_delay = (
                len(line_paths) * theme.stagger_delay
                + len(arrow_tip_paths) * theme.stagger_delay * 0.2
            )
            arrow_delay = base_delay + (
                i * theme.stagger_delay * 0.1
            )  # Even faster stagger for non-path tips

            existing_style = element.get("style", "")
            new_style = f"{existing_style}; animation-delay: {arrow_delay}s;"
            element.set("style", new_style)

            # Apply theme-specific classes for arrow tips (use edge classes, not node classes)
            if theme.edge_style == "neon":
                element.set("class", "anim-edge neon-glow")
            elif theme.edge_style == "hand-drawn":
                element.set("class", "anim-edge hand-drawn")
            else:
                element.set("class", "anim-edge clean-edge")

        # 3. Process nodes (rectangles, circles, etc.) - exclude arrow tip elements inside markers
        all_rects = self.root.findall(".//svg:rect", self.ns)
        all_circles = self.root.findall(".//svg:circle", self.ns)
        all_ellipses = self.root.findall(".//svg:ellipse", self.ns)
        all_polygons = self.root.findall(".//svg:polygon", self.ns)

        # Find elements inside markers (arrow tips) to exclude from node processing
        marker_rects = self.root.findall(".//svg:marker//svg:rect", self.ns)
        marker_circles = self.root.findall(".//svg:marker//svg:circle", self.ns)
        marker_ellipses = self.root.findall(".//svg:marker//svg:ellipse", self.ns)
        marker_polygons = self.root.findall(".//svg:marker//svg:polygon", self.ns)

        marker_elements_set = set(
            marker_rects + marker_circles + marker_ellipses + marker_polygons
        )

        # Filter out marker elements from nodes
        nodes = []
        for element_list in [all_rects, all_circles, all_ellipses, all_polygons]:
            for element in element_list:
                if element not in marker_elements_set:
                    nodes.append(element)

        for i, node in enumerate(nodes):
            delay = i * theme.stagger_delay * 0.5  # Nodes appear before edges

            existing_style = node.get("style", "")
            new_style = f"{existing_style}; animation-delay: {delay}s;"
            node.set("style", new_style)

            # Apply theme-specific node classes
            if theme.node_style == "glass":
                node.set("class", "anim-node glass-node")
            elif theme.node_style == "outlined":
                node.set("class", "anim-node outlined-node")
            else:
                node.set("class", "anim-node solid-node")

        return ET.tostring(self.root, encoding="unicode")
