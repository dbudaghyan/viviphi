"""Tests for Theme system."""

import pytest
from viviphi.themes import Theme, CYBERPUNK, CORPORATE, HAND_DRAWN


class TestTheme:
    """Test Theme functionality."""
    
    def test_default_theme_creation(self):
        """Test creating a theme with default values."""
        theme = Theme()
        assert theme.primary_color == "#00ff99"
        assert theme.background == "#1a1a1a"
        assert theme.edge_style == "neon"
        assert theme.node_style == "glass"
        assert theme.animation_duration == 1.5
        assert theme.stagger_delay == 0.3
    
    def test_custom_theme_creation(self):
        """Test creating a theme with custom values."""
        theme = Theme(
            primary_color="#ff5722",
            background="#ffffff",
            edge_style="clean",
            node_style="outlined",
            animation_duration=2.0,
            stagger_delay=0.5
        )
        assert theme.primary_color == "#ff5722"
        assert theme.edge_style == "clean"
        assert theme.node_style == "outlined"
        assert theme.animation_duration == 2.0
        assert theme.stagger_delay == 0.5
    
    def test_cyberpunk_theme_preset(self):
        """Test CYBERPUNK preset theme."""
        assert CYBERPUNK.primary_color == "#00ff99"
        assert CYBERPUNK.edge_style == "neon"
        assert CYBERPUNK.node_style == "glass"
    
    def test_corporate_theme_preset(self):
        """Test CORPORATE preset theme."""
        assert CORPORATE.primary_color == "#2563eb"
        assert CORPORATE.edge_style == "clean"
        assert CORPORATE.node_style == "solid"
        assert CORPORATE.animation_duration == 1.0
    
    def test_hand_drawn_theme_preset(self):
        """Test HAND_DRAWN preset theme."""
        assert HAND_DRAWN.edge_style == "hand-drawn"
        assert HAND_DRAWN.node_style == "outlined"
        assert HAND_DRAWN.animation_duration == 2.0
        assert HAND_DRAWN.stagger_delay == 0.4
    
    def test_get_css_template_neon(self):
        """Test CSS generation for neon theme."""
        theme = Theme(edge_style="neon", primary_color="#00ff99")
        css = theme.get_css_template()
        
        assert "neon-glow" in css
        assert "drop-shadow" in css
        assert "#00ff99" in css
    
    def test_get_css_template_clean(self):
        """Test CSS generation for clean theme."""
        theme = Theme(edge_style="clean", node_style="solid")
        css = theme.get_css_template()
        
        assert "clean-edge" in css
        assert "solid-node" in css
    
    def test_get_css_template_hand_drawn(self):
        """Test CSS generation for hand-drawn theme."""
        theme = Theme(edge_style="hand-drawn", node_style="outlined")
        css = theme.get_css_template()
        
        assert "hand-drawn" in css
        assert "stroke-linecap: round" in css
        assert "outlined-node" in css
    
    def test_theme_model_copy(self):
        """Test that themes can be copied and modified."""
        original = CYBERPUNK
        copy = original.model_copy()
        copy.animation_duration = 3.0
        
        assert original.animation_duration == 1.5  # Original unchanged
        assert copy.animation_duration == 3.0  # Copy modified