"""Tests for SVGAnimator class."""

import pytest
from viviphi.animator import SVGAnimator
from viviphi.themes import CYBERPUNK, CORPORATE


class TestSVGAnimator:
    """Test SVGAnimator functionality."""
    
    def test_init_with_simple_svg(self):
        """Test initialization with a simple SVG."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 Q 200 50 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        assert animator.root is not None
        assert animator.ns == {'svg': 'http://www.w3.org/2000/svg'}
    
    def test_process_adds_css_and_animations(self):
        """Test that process method adds CSS and animation attributes."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process(color="#ff0000")
        
        # Check that CSS is injected
        assert "<style>" in result
        assert "@keyframes draw-flow" in result
        assert "stroke-dasharray" in result
        
        # Check that path has animation attributes
        assert 'class="anim-edge neon-glow"' in result
        assert 'stroke="#ff0000"' in result
        assert "--length:" in result
        assert "animation-delay:" in result
    
    def test_process_with_theme_cyberpunk(self):
        """Test processing with cyberpunk theme."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
            <rect x="40" y="140" width="20" height="20" fill="white"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process_with_theme(CYBERPUNK)
        
        # Check theme-specific styling
        assert CYBERPUNK.primary_color in result
        assert "neon-glow" in result
        assert "glass-node" in result
    
    def test_process_with_theme_corporate(self):
        """Test processing with corporate theme."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process_with_theme(CORPORATE)
        
        # Check corporate theme styling
        assert CORPORATE.primary_color in result
        assert "clean-edge" in result
    
    def test_process_handles_empty_paths(self):
        """Test that paths without 'd' attribute are skipped gracefully."""
        svg_content = """
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <path stroke="black" fill="none"/>
            <path d="M 50 150 L 350 150" stroke="black" fill="none"/>
        </svg>
        """
        animator = SVGAnimator(svg_content)
        result = animator.process()
        
        # Should not raise error and should process the valid path
        assert result is not None
        assert "stroke-dasharray" in result