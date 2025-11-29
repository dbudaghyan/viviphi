"""Integration tests without browser dependencies."""

import pytest
from unittest.mock import Mock, patch
from viviphi import Graph, CYBERPUNK


class TestGraphIntegration:
    """Integration tests for Graph class."""
    
    @patch('viviphi.graph.MermaidRenderer')
    def test_graph_animate_workflow(self, mock_renderer_class):
        """Test the complete animation workflow without browser."""
        # Mock the renderer
        mock_renderer = Mock()
        mock_svg = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        # Test the workflow
        graph = Graph("graph TD; A --> B")
        result = graph.animate(theme=CYBERPUNK, speed="normal")
        
        # Verify renderer was called
        mock_renderer.render_to_svg.assert_called_once_with("graph TD; A --> B")
        
        # Verify animation was applied
        assert "<style>" in result
        assert "neon-glow" in result
        assert CYBERPUNK.primary_color in result
        assert "@keyframes" in result
    
    @patch('viviphi.graph.MermaidRenderer')
    def test_graph_speed_adjustment(self, mock_renderer_class):
        """Test that speed setting affects animation timing."""
        mock_renderer = Mock()
        mock_svg = """
        <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
            <path d="M 10 50 L 190 50" stroke="black" fill="none"/>
        </svg>
        """
        mock_renderer.render_to_svg.return_value = mock_svg
        mock_renderer_class.return_value = mock_renderer
        
        graph = Graph("graph LR; A --> B")
        
        # Test different speeds
        slow_result = graph.animate(speed="slow")
        fast_result = graph.animate(speed="fast")
        
        # Speeds should affect the CSS timing values
        # (We can't easily test exact values without parsing CSS, 
        # but we can ensure different outputs)
        assert slow_result != fast_result
    
    def test_graph_initialization(self):
        """Test Graph initialization."""
        mermaid_def = "graph TD; A[Start] --> B[End]"
        graph = Graph(mermaid_def)
        assert graph.mermaid_definition == mermaid_def