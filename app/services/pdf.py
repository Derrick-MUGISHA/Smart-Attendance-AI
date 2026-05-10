from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os

def generate_attendance_pdf(session_data: dict) -> bytes:
    """Render HTML template to PDF bytes."""
    # Ensure templates directory exists
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('attendance_report.html')
    html_content = template.render(**session_data)
    return HTML(string=html_content).write_pdf()
