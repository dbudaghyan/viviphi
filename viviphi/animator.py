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
        self._reversed_markers = set()  # Track created reversed markers

    def _create_reversed_marker(self, marker_id: str) -> None:
        """Create a reversed version of a marker by flipping its geometry.

        Args:
            marker_id: ID of the original marker to reverse
        """
        # Avoid creating duplicates
        reversed_id = f"{marker_id}_reversed"
        if reversed_id in self._reversed_markers:
            return

        # Find the original marker
        original_marker = self.root.find(
            f".//svg:defs/svg:marker[@id='{marker_id}']", self.ns
        )
        if original_marker is None:
            return

        # Create a copy of the original marker
        reversed_marker = ET.fromstring(ET.tostring(original_marker))
        reversed_marker.set("id", reversed_id)

        # Reverse the marker geometry by applying a transformation
        # For extension arrows, we need to flip them horizontally
        marker_paths = reversed_marker.findall(".//svg:path", self.ns)
        for path in marker_paths:
            d_attr = path.get("d", "")
            if d_attr:
                # For extension arrows, flip the path horizontally around x=9.5 (middle of 0-18 range)
                # This effectively reverses the arrow direction
                if "extension" in marker_id.lower():
                    # Simple horizontal flip for extension markers - reverse x coordinates around center
                    flipped_d = self._flip_path_horizontally(
                        d_attr, 18
                    )  # 18 is refX value
                    path.set("d", flipped_d)

        # Add the reversed marker to the defs section
        defs = self.root.find(".//svg:defs", self.ns)
        if defs is not None:
            defs.append(reversed_marker)
            self._reversed_markers.add(reversed_id)

    def _is_node_shape_path(self, path) -> bool:
        """Check if path defines a node shape rather than an edge.
        
        Args:
            path: SVG path element
            
        Returns:
            True if path is part of a node shape, False if it's an edge
        """
        # Check if path is inside a node group (not marker) by searching the tree
        # Find all groups and check their IDs
        all_groups = self.root.findall(".//svg:g", self.ns)
        
        for group in all_groups:
            group_id = group.get('id', '')
            if group_id.startswith('flowchart-'):
                # Check if this path is contained within this node group
                group_paths = group.findall(".//svg:path", self.ns)
                if path in group_paths:
                    return True
                
        return False

    def _flip_path_horizontally(self, path_d: str, width: float) -> str:
        """Flip a path horizontally around its center.

        Args:
            path_d: SVG path d attribute
            width: Width to flip around (usually marker width)

        Returns:
            Flipped path d attribute
        """
        import re

        # For simple extension markers like "M 1,7 L18,13 V 1 Z"
        # Flip x coordinates: x_new = width - x_old
        def flip_coords(match):
            x = float(match.group(1))
            y = match.group(2)
            flipped_x = width - x
            return f"{flipped_x},{y}"

        # Replace coordinate pairs (x,y)
        flipped = re.sub(r"(\d+(?:\.\d+)?),(\d+(?:\.\d+)?)", flip_coords, path_d)
        return flipped

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

        # Separate paths into lines (outside markers), arrow tips (inside markers), and node shapes
        line_paths = []
        arrow_tip_paths = []
        node_shape_paths = []

        for path in all_paths:
            if path in marker_path_set:
                arrow_tip_paths.append(path)
            elif self._is_node_shape_path(path):
                node_shape_paths.append(path)
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

                # Check semantic direction data to ensure proper animation flow
                flow_direction = path.get("data-flow-direction", "forward")
                marker_start = path.get("marker-start", "none")
                marker_end = path.get("marker-end", "none")

                # Determine if path needs reversal based on marker placement vs semantic direction
                needs_reversal = False
                if flow_direction == "forward":
                    # Forward flow should have marker at end of path animation
                    # If marker-start is set (arrow at beginning), path needs reversal
                    if marker_start != "none" and marker_end == "none":
                        needs_reversal = True
                elif flow_direction == "backward":
                    # Backward flow should have marker at start of path animation
                    # If marker-end is set (arrow at end), path needs reversal
                    if marker_end != "none" and marker_start == "none":
                        needs_reversal = True

                if needs_reversal:
                    # Reverse the path for proper tail-to-tip animation
                    path_obj = path_obj.reversed()
                    path.set("d", path_obj.d())
                    length = path_obj.length()

                    # Fix marker orientation by creating reversed marker definitions
                    if marker_start != "none":
                        marker_id = marker_start.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_start = f"url(#{marker_id}_reversed)"

                    if marker_end != "none":
                        marker_id = marker_end.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_end = f"url(#{marker_id}_reversed)"

                    # Swap marker attributes to match reversed path
                    path.set("marker-start", marker_end)
                    path.set("marker-end", marker_start)
                    # Update local variables
                    marker_start, marker_end = marker_end, marker_start

                # Use semantic animation order if available, otherwise fall back to index
                animation_order = path.get("data-animation-order")
                if animation_order is not None:
                    delay = int(animation_order) * 0.3
                else:
                    # Fallback to index-based timing
                    delay = i * 0.3

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

        # Separate paths into lines (outside markers), arrow tips (inside markers), and node shapes
        line_paths = []
        arrow_tip_paths = []
        node_shape_paths = []

        for path in all_paths:
            if path in marker_path_set:
                arrow_tip_paths.append(path)
            elif self._is_node_shape_path(path):
                node_shape_paths.append(path)
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

                # Check semantic direction data to ensure proper animation flow
                flow_direction = path.get("data-flow-direction", "forward")
                marker_start = path.get("marker-start", "none")
                marker_end = path.get("marker-end", "none")

                # Determine if path needs reversal based on marker placement vs semantic direction
                needs_reversal = False
                if flow_direction == "forward":
                    # Forward flow should have marker at end of path animation
                    # If marker-start is set (arrow at beginning), path needs reversal
                    if marker_start != "none" and marker_end == "none":
                        needs_reversal = True
                elif flow_direction == "backward":
                    # Backward flow should have marker at start of path animation
                    # If marker-end is set (arrow at end), path needs reversal
                    if marker_end != "none" and marker_start == "none":
                        needs_reversal = True

                if needs_reversal:
                    # Reverse the path for proper tail-to-tip animation
                    path_obj = path_obj.reversed()
                    path.set("d", path_obj.d())
                    length = path_obj.length()

                    # Fix marker orientation by creating reversed marker definitions
                    if marker_start != "none":
                        marker_id = marker_start.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_start = f"url(#{marker_id}_reversed)"

                    if marker_end != "none":
                        marker_id = marker_end.replace("url(#", "").replace(")", "")
                        self._create_reversed_marker(marker_id)
                        marker_end = f"url(#{marker_id}_reversed)"

                    # Swap marker attributes to match reversed path
                    path.set("marker-start", marker_end)
                    path.set("marker-end", marker_start)
                    # Update local variables
                    marker_start, marker_end = marker_end, marker_start

                # Use semantic animation order if available, otherwise fall back to theme-based delay
                animation_order = path.get("data-animation-order")
                if animation_order is not None:
                    delay = int(animation_order) * theme.stagger_delay
                else:
                    # Fallback to index-based timing
                    delay = i * theme.stagger_delay

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

            # More precise skip conditions for complex shapes
            node_tag = node.tag.split('}')[-1] if '}' in node.tag else node.tag
            has_transform = node.get("transform") is not None
            
            # Skip animation for shapes with ANY transform attributes
            # CSS animations with transform properties will override existing transforms
            skip_animation = False
            if has_transform and node_tag == "polygon":
                # Skip all polygon transforms - CSS transform animations conflict with positioning
                skip_animation = True
            elif node_tag == "path" and has_transform:
                # Always skip path nodes with transforms (these are shape definitions)
                skip_animation = True

            if not skip_animation:
                existing_style = node.get("style", "")
                new_style = f"{existing_style}; animation-delay: {delay}s;"
                node.set("style", new_style)

            # Apply theme-specific node classes
            if skip_animation:
                # For polygons with transforms, use static classes without animation
                if theme.node_style == "glass":
                    node.set("class", "glass-node")
                elif theme.node_style == "outlined":
                    node.set("class", "outlined-node")
                else:
                    node.set("class", "solid-node")
            else:
                # For normal nodes, use animated classes
                if theme.node_style == "glass":
                    node.set("class", "anim-node glass-node")
                elif theme.node_style == "outlined":
                    node.set("class", "anim-node outlined-node")
                else:
                    node.set("class", "anim-node solid-node")

        # 4. Process node-defining paths separately (like database shapes)
        for i, path in enumerate(node_shape_paths):
            delay = i * theme.stagger_delay * 0.5
            existing_style = path.get("style", "")
            new_style = f"{existing_style}; animation-delay: {delay}s;"
            path.set("style", new_style)
            
            # Apply theme-specific node classes for node shape paths
            if theme.node_style == "glass":
                path.set("class", "anim-node glass-node")
            elif theme.node_style == "outlined":
                path.set("class", "anim-node outlined-node")
            else:
                path.set("class", "anim-node solid-node")

        return ET.tostring(self.root, encoding="unicode")
