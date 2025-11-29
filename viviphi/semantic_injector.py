"""Injects semantic direction metadata into SVG files for proper animation."""

import re
import xml.etree.ElementTree as ET
from typing import List, NamedTuple


class EdgeSemantics(NamedTuple):
    """Represents semantic information about a graph edge."""
    source: str
    target: str
    direction: str  # 'forward', 'backward', 'bidirectional'
    edge_type: str  # 'arrow', 'extension', 'aggregation', etc.


class SemanticInjector:
    """Injects semantic direction metadata into Mermaid-generated SVGs."""
    
    def __init__(self, mermaid_definition: str) -> None:
        """Initialize with the original Mermaid definition.
        
        Args:
            mermaid_definition: Original Mermaid graph syntax
        """
        self.mermaid_definition = mermaid_definition
        self.edge_semantics = self._parse_edge_semantics()
    
    def inject_metadata(self, svg_content: str) -> str:
        """Add semantic direction data attributes to SVG paths.
        
        Args:
            svg_content: Original SVG content from Mermaid
            
        Returns:
            SVG with semantic metadata injected
        """
        # Parse SVG
        root = ET.fromstring(svg_content)
        ns = {"svg": "http://www.w3.org/2000/svg"}
        
        # Find all edge paths (not in markers)
        edge_paths = []
        marker_paths = root.findall(".//svg:marker//svg:path", ns)
        marker_path_set = set(marker_paths)
        
        for path in root.findall(".//svg:path", ns):
            if path not in marker_path_set:
                edge_paths.append(path)
        
        # Inject semantic data for each edge
        for i, path in enumerate(edge_paths):
            if i < len(self.edge_semantics):
                semantics = self.edge_semantics[i]
                self._add_semantic_attributes(path, semantics)
        
        return ET.tostring(root, encoding="unicode")
    
    def _parse_edge_semantics(self) -> List[EdgeSemantics]:
        """Parse Mermaid definition to extract edge semantics."""
        edges = []
        
        # Patterns for different edge types
        patterns = [
            # Class diagram patterns
            (r"(\w+)\s*\|\|\--\|\|\s*(\w+)", "aggregation", "forward"),  # ||--||
            (r"(\w+)\s*\}\|\.\.--\>\|\{\s*(\w+)", "composition", "forward"),  # }|..-->|{
            (r"(\w+)\s*\<\|--\s*(\w+)", "extension", "forward"),  # <|-- (Parent <|-- Child)
            (r"(\w+)\s*--\>\s*(\w+)", "dependency", "forward"),  # -->
            
            # Flowchart patterns  
            (r"(\w+)\s*-->\s*(\w+)", "arrow", "forward"),  # -->
            (r"(\w+)\s*<-->\s*(\w+)", "arrow", "bidirectional"),  # <-->
            (r"(\w+)\s*-\.->\s*(\w+)", "dotted_arrow", "forward"),  # -.->
            (r"(\w+)\s*<-\.->\s*(\w+)", "dotted_arrow", "bidirectional"),  # <-.->
            (r"(\w+)\s*==>\s*(\w+)", "thick_arrow", "forward"),  # ==>
            (r"(\w+)\s*--o\s*(\w+)", "circle", "forward"),  # --o
            (r"(\w+)\s*--x\s*(\w+)", "cross", "forward"),  # --x
        ]
        
        lines = self.mermaid_definition.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):  # Skip comments
                continue
                
            for pattern, edge_type, direction in patterns:
                match = re.search(pattern, line)
                if match:
                    source, target = match.groups()
                    # Handle special case for extension: Parent <|-- Child means Child extends Parent
                    if edge_type == "extension":
                        source, target = target, source  # Swap for inheritance direction
                    # Handle special case for backward arrows
                    elif direction == "backward":
                        source, target = target, source
                        direction = "forward"
                    
                    edges.append(EdgeSemantics(
                        source=source,
                        target=target,
                        direction=direction,
                        edge_type=edge_type
                    ))
                    break
        
        return edges
    
    def _add_semantic_attributes(self, path_element: ET.Element, semantics: EdgeSemantics) -> None:
        """Add semantic data attributes to a path element."""
        path_element.set("data-flow-direction", semantics.direction)
        path_element.set("data-source-node", semantics.source)
        path_element.set("data-target-node", semantics.target)
        path_element.set("data-edge-type", semantics.edge_type)