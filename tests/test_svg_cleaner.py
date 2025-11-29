"""Test SVG cleaner functionality."""

import pytest
from viviphi.svg_cleaner import SVGCleaner


class TestSVGCleaner:
    """Test SVGCleaner functionality."""
    
    def test_simple_svg_passthrough(self):
        """Test that simple SVGs pass through unchanged."""
        simple_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <circle cx="50" cy="50" r="25" fill="blue"/>
        </svg>'''
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(simple_svg)
        
        assert '<svg' in result
        assert '<circle' in result
        assert 'fill="blue"' in result
    
    def test_remove_foreign_objects_with_html(self):
        """Test that foreign objects with HTML content are cleaned."""
        svg_with_html = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:html="http://www.w3.org/1999/xhtml" width="200" height="100">
            <foreignObject x="10" y="10" width="100" height="50">
                <html:div style="display: inline-block;">
                    <html:span class="nodeLabel">Test Text</html:span>
                </html:div>
            </foreignObject>
        </svg>'''
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(svg_with_html)
        
        # Should not contain HTML elements
        assert 'html:div' not in result
        assert 'html:span' not in result
        assert 'foreignObject' not in result
        
        # Should contain converted text element
        assert '<text' in result
        assert 'Test Text' in result
    
    def test_clean_html_namespace_references(self):
        """Test that HTML namespace references are removed."""
        svg_with_ns = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:html="http://www.w3.org/1999/xhtml">
            <circle cx="50" cy="50" r="25"/>
        </svg>'''
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(svg_with_ns)
        
        # Should not contain HTML namespace declaration
        assert 'xmlns:html' not in result
    
    def test_preserve_valid_svg_elements(self):
        """Test that valid SVG elements are preserved."""
        valid_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <style>
                .edge { stroke: red; }
                @keyframes draw { to { stroke-dashoffset: 0; } }
            </style>
            <path d="M 10 10 L 100 100" class="edge" stroke="red"/>
            <rect x="50" y="50" width="30" height="20" fill="blue"/>
        </svg>'''
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(valid_svg)
        
        # All valid elements should be preserved
        assert '<style>' in result
        assert '@keyframes' in result
        assert '<path' in result
        assert '<rect' in result
        assert 'stroke="red"' in result
        assert 'fill="blue"' in result
    
    def test_handle_malformed_svg(self):
        """Test that malformed SVG is handled gracefully."""
        malformed_svg = '<svg><path d="invalid"/>'  # Missing closing tag
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(malformed_svg)
        
        # Should return original content if parsing fails
        assert result == malformed_svg
    
    def test_extract_text_from_complex_html(self):
        """Test text extraction from nested HTML elements."""
        complex_svg = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:html="http://www.w3.org/1999/xhtml">
            <foreignObject x="0" y="0" width="100" height="50">
                <html:div style="display: inline-block; white-space: nowrap;">
                    <html:span class="nodeLabel">Complex Text</html:span>
                </html:div>
            </foreignObject>
        </svg>'''
        
        cleaner = SVGCleaner()
        result = cleaner.clean_svg(complex_svg)
        
        # Should extract and preserve the text content
        assert 'Complex Text' in result
        assert '<text' in result