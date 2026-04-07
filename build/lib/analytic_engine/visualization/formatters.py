"""Output formatters for visualization engine"""

from typing import Any, Dict, Optional
from io import BytesIO
import base64
import json


class OutputFormatter:
    """Format visualizations for display"""

    @staticmethod
    def to_base64_png(figure: Any) -> str:
        """Convert figure to base64 PNG"""
        buf = BytesIO()
        if hasattr(figure, "savefig"):
            figure.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()
        return ""

    @staticmethod
    def to_html(figure: Any) -> str:
        """Convert figure to HTML"""
        if hasattr(figure, "to_html"):
            return figure.to_html()
        return f"<pre>{figure}</pre>"

    @staticmethod
    def to_json(figure: Any) -> str:
        """Convert figure to JSON"""
        if hasattr(figure, "to_json"):
            return figure.to_json()
        return json.dumps({"type": "unknown"})

    @staticmethod
    def format_for_display(figure: Any, format: str = "png") -> Dict[str, Any]:
        """Format figure for display"""
        if format == "html":
            return {"type": "html", "content": OutputFormatter.to_html(figure)}
        elif format == "json":
            return {"type": "json", "content": OutputFormatter.to_json(figure)}
        elif format == "png":
            return {
                "type": "base64",
                "content": OutputFormatter.to_base64_png(figure),
                "mime": "image/png",
            }
        return {"type": "unknown"}

    @staticmethod
    def wrap_in_html(content: str, title: str = "Visualization") -> str:
        """Wrap content in HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>body {{ font-family: sans-serif; padding: 20px; }}</style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
