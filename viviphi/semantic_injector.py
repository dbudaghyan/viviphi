"""Injects semantic direction metadata into SVG files for proper animation."""

import re
import xml.etree.ElementTree as ET
from typing import List, NamedTuple, Dict, Set
from collections import defaultdict, deque


class EdgeSemantics(NamedTuple):
    """Represents semantic information about a graph edge."""
    source: str
    target: str
    direction: str  # 'forward', 'backward', 'bidirectional'
    edge_type: str  # 'arrow', 'extension', 'aggregation', etc.
    order: int = 0  # Animation order based on graph topology


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
                
            # Split line by semicolons to handle multiple edges per line
            edge_parts = [part.strip() for part in line.split(';') if part.strip()]
            
            for edge_part in edge_parts:
                for pattern, edge_type, direction in patterns:
                    match = re.search(pattern, edge_part)
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
        
        # Calculate animation order based on graph topology
        edges_with_order = self._calculate_animation_order(edges)
        return edges_with_order
    
    def _calculate_animation_order(self, edges: List[EdgeSemantics]) -> List[EdgeSemantics]:
        """Calculate animation order based on sequential edge traversal following graph flow.
        
        Args:
            edges: List of edges without order information
            
        Returns:
            List of edges with calculated animation order
        """
        if not edges:
            return edges
        
        # Build graph representations
        edge_graph: Dict[str, List[int]] = defaultdict(list)  # node -> list of outgoing edge indices
        edge_targets: Dict[str, List[int]] = defaultdict(list)  # node -> list of incoming edge indices
        all_nodes: Set[str] = set()
        
        # Map edges and build adjacency structures
        for i, edge in enumerate(edges):
            all_nodes.add(edge.source)
            all_nodes.add(edge.target)
            edge_graph[edge.source].append(i)
            edge_targets[edge.target].append(i)
        
        # Track which edges have been assigned an order
        edge_order_assigned = [False] * len(edges)
        ordered_edges = [None] * len(edges)
        current_order = 0
        
        # Find starting nodes (nodes with no incoming edges or minimal incoming edges)
        start_nodes = []
        for node in all_nodes:
            if not edge_targets[node]:  # No incoming edges
                start_nodes.append(node)
        
        # If no clear start nodes (cycles), start with nodes that have minimum incoming edges
        if not start_nodes:
            min_incoming = min(len(edge_targets[node]) for node in all_nodes)
            start_nodes = [node for node in all_nodes if len(edge_targets[node]) == min_incoming]
        
        # Use breadth-first traversal to assign edge orders sequentially
        visited_nodes: Set[str] = set()
        queue = deque(start_nodes)
        
        while queue:
            current_node = queue.popleft()
            
            if current_node in visited_nodes:
                continue
            visited_nodes.add(current_node)
            
            # Process all outgoing edges from this node
            outgoing_edge_indices = edge_graph[current_node]
            
            for edge_idx in outgoing_edge_indices:
                if not edge_order_assigned[edge_idx]:
                    edge = edges[edge_idx]
                    ordered_edges[edge_idx] = EdgeSemantics(
                        source=edge.source,
                        target=edge.target,
                        direction=edge.direction,
                        edge_type=edge.edge_type,
                        order=current_order
                    )
                    edge_order_assigned[edge_idx] = True
                    current_order += 1
                    
                    # Add target node to queue for further traversal
                    target_node = edge.target
                    if target_node not in visited_nodes:
                        # Check if all incoming edges to target have been processed
                        incoming_edges = edge_targets[target_node]
                        all_incoming_processed = all(edge_order_assigned[idx] for idx in incoming_edges)
                        
                        # Add to queue if all dependencies are satisfied or if we need to break cycles
                        if all_incoming_processed or target_node not in queue:
                            queue.append(target_node)
        
        # Handle any remaining unprocessed edges (in cycles or disconnected components)
        for i, assigned in enumerate(edge_order_assigned):
            if not assigned:
                edge = edges[i]
                ordered_edges[i] = EdgeSemantics(
                    source=edge.source,
                    target=edge.target,
                    direction=edge.direction,
                    edge_type=edge.edge_type,
                    order=current_order
                )
                current_order += 1
        
        return ordered_edges

    def _add_semantic_attributes(self, path_element: ET.Element, semantics: EdgeSemantics) -> None:
        """Add semantic data attributes to a path element."""
        path_element.set("data-flow-direction", semantics.direction)
        path_element.set("data-source-node", semantics.source)
        path_element.set("data-target-node", semantics.target)
        path_element.set("data-edge-type", semantics.edge_type)
        path_element.set("data-animation-order", str(semantics.order))