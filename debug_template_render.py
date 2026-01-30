"""
تست rendering template
"""
import sys
from pathlib import Path
from flask import Flask, render_template_string

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_ui import get_audit_tests_with_custom

tests = get_audit_tests_with_custom()

# تست template با Jinja2
template = """
{% if audit_tests.get('custom') %}
<div>
    <h3>✅ دسته custom موجود است</h3>
    <p>نام: {{ audit_tests.custom.name }}</p>
    <p>تعداد آزمون‌ها: {{ audit_tests.custom.tests|length }}</p>
    <ul>
    {% for test in audit_tests.custom.tests %}
        <li>{{ test.name }} ({{ test.id }})</li>
    {% endfor %}
    </ul>
</div>
{% else %}
<div>
    <h3>❌ دسته custom موجود نیست</h3>
</div>
{% endif %}
"""

app = Flask(__name__)
with app.app_context():
    result = render_template_string(template, audit_tests=tests)
    print(result)
