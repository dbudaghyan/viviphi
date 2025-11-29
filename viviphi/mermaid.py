"""Mermaid.js integration using headless browser for layout generation."""

from playwright.sync_api import sync_playwright
from typing import Optional


class MermaidRenderer:
    """Renders Mermaid definitions to static SVG using headless browser."""
    
    def __init__(self, headless: bool = True) -> None:
        """Initialize the renderer.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        
    def render_to_svg(self, mermaid_definition: str) -> str:
        """Render a Mermaid definition to static SVG.
        
        Args:
            mermaid_definition: Mermaid.js syntax string
            
        Returns:
            Static SVG content as string
            
        Raises:
            RuntimeError: If rendering fails
        """
        html_template = self._create_html_template(mermaid_definition)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            try:
                # Load the HTML with Mermaid
                page.set_content(html_template)
                
                # Wait for Mermaid to render
                page.wait_for_selector('#mermaid-output svg', timeout=10000)
                
                # Extract the SVG content
                svg_content = page.evaluate('''() => {
                    const svg = document.querySelector('#mermaid-output svg');
                    return svg ? svg.outerHTML : null;
                }''')
                
                if not svg_content:
                    raise RuntimeError("Failed to generate SVG from Mermaid definition")
                    
                return svg_content
                
            finally:
                browser.close()
    
    def _create_html_template(self, mermaid_definition: str) -> str:
        """Create HTML template with Mermaid.js and the definition.
        
        Args:
            mermaid_definition: Mermaid syntax string
            
        Returns:
            Complete HTML page content
        """
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mermaid Renderer</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        </head>
        <body>
            <div id="mermaid-output">
                <pre class="mermaid">{mermaid_definition}</pre>
            </div>
            
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'base',
                    themeVariables: {{
                        primaryColor: '#ffffff',
                        primaryTextColor: '#000000',
                        primaryBorderColor: '#000000',
                        lineColor: '#000000',
                        secondaryColor: '#ffffff',
                        tertiaryColor: '#ffffff'
                    }}
                }});
            </script>
        </body>
        </html>
        '''