"""Tests for Theme system."""

from viviphi.themes import (
    Theme,
    CYBERPUNK,
    CORPORATE,
    HAND_DRAWN,
    MANIM_CLASSIC,
    MANIM_LIGHT,
    MANIM_AQUA,
    MANIM_ORANGE,
    MANIM_PROOF,
)


class TestTheme:
    """Test Theme functionality."""

    def test_default_theme_creation(self):
        """Test creating a theme with default values."""
        theme = Theme()
        assert theme.primary_color == "#00ff99"
        assert theme.background.color == "#1a1a1a"
        assert theme.edge_style == "clean"  # Updated default
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
            stagger_delay=0.5,
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
        copy = original.model_copy(deep=True)
        # Modify the animation component instead of the legacy property
        copy.animation.duration = 3.0

        assert original.animation_duration == 1.5  # Original unchanged
        assert copy.animation_duration == 3.0  # Copy modified

    def test_manim_classic_theme_preset(self):
        """Test MANIM_CLASSIC preset theme."""
        assert MANIM_CLASSIC.primary_color == "#58c4dd"
        assert MANIM_CLASSIC.background.color == "#0c0c0c"
        assert MANIM_CLASSIC.edge_style == "clean"
        assert MANIM_CLASSIC.node_style == "solid"
        assert MANIM_CLASSIC.animation_duration == 1.2
        assert MANIM_CLASSIC.stagger_delay == 0.25

    def test_manim_light_theme_preset(self):
        """Test MANIM_LIGHT preset theme."""
        assert MANIM_LIGHT.primary_color == "#1f4e79"
        assert MANIM_LIGHT.background.color == "#fefefe"
        assert MANIM_LIGHT.edge_style == "clean"
        assert MANIM_LIGHT.node_style == "solid"

    def test_manim_aqua_theme_preset(self):
        """Test MANIM_AQUA preset theme."""
        assert MANIM_AQUA.primary_color == "#83d0c9"
        assert MANIM_AQUA.background.color == "#0c0c0c"
        assert MANIM_AQUA.node_style == "glass"
        assert MANIM_AQUA.animation_duration == 1.4

    def test_manim_orange_theme_preset(self):
        """Test MANIM_ORANGE preset theme."""
        assert MANIM_ORANGE.primary_color == "#fc6255"
        assert MANIM_ORANGE.background.color == "#0c0c0c"
        assert MANIM_ORANGE.node_style == "solid"
        assert MANIM_ORANGE.animation_duration == 1.0

    def test_manim_proof_theme_preset(self):
        """Test MANIM_PROOF preset theme."""
        assert MANIM_PROOF.primary_color == "#c59df5"
        assert MANIM_PROOF.background.color == "#0c0c0c"
        assert MANIM_PROOF.node_style == "glass"
        assert MANIM_PROOF.animation_duration == 1.8
        assert MANIM_PROOF.stagger_delay == 0.35

    def test_enhanced_theme_components(self):
        """Test new theme component structure."""
        from viviphi.themes import (
            NodeStyling,
            EdgeStyling,
            BackgroundStyling,
            AnimationStyling,
        )

        # Test creating a theme with component objects
        theme = Theme(
            primary_color="#ff0000",
            background=BackgroundStyling(color="#000000", pattern="grid"),
            edges=EdgeStyling(style="dashed", width=3.0, glow_enabled=True),
            nodes=NodeStyling(style="rounded", border_radius=8.0, shadow=True),
            animation=AnimationStyling(duration=2.5, easing="ease-in"),
        )

        assert theme.primary_color == "#ff0000"
        assert theme.background.color == "#000000"
        assert theme.background.pattern == "grid"
        assert theme.edges.style == "dashed"
        assert theme.edges.width == 3.0
        assert theme.edges.glow_enabled == True
        assert theme.nodes.style == "rounded"
        assert theme.nodes.border_radius == 8.0
        assert theme.nodes.shadow == True
        assert theme.animation.duration == 2.5
        assert theme.animation.easing == "ease-in"

    def test_advanced_themes(self):
        """Test advanced themed examples."""
        from viviphi.themes import CYBERPUNK_GRID, GRADIENT_SUNSET, DOTTED_MINIMAL

        # Test CYBERPUNK_GRID theme
        assert CYBERPUNK_GRID.background.pattern == "grid"
        assert CYBERPUNK_GRID.edges.glow_enabled == True
        assert CYBERPUNK_GRID.nodes.shadow == True

        # Test GRADIENT_SUNSET theme
        assert GRADIENT_SUNSET.background.gradient_enabled == True
        assert GRADIENT_SUNSET.background.gradient_start == "#ff6b6b"
        assert GRADIENT_SUNSET.nodes.style == "rounded"

        # Test DOTTED_MINIMAL theme
        assert DOTTED_MINIMAL.background.pattern == "dots"
        assert DOTTED_MINIMAL.edges.style == "dotted"
        assert DOTTED_MINIMAL.font_weight == "bold"
