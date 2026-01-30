from test_generator import load_prompt_template

try:
    template = load_prompt_template()
    print(f"Template loaded: {len(template)} characters")
    
    # تست format کردن
    result = template.format(user_description="این یک تست است")
    print(f"Format successful: {len(result)} characters")
    print("✅ همه چیز درست است")
except Exception as e:
    print(f"❌ خطا: {str(e)}")
    import traceback
    traceback.print_exc()
