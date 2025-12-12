import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Endpoint Judge0 مستقر
JUDGE0_URL = "https://ce.judge0.com/submissions/?base64_encoded=false&wait=true"

LANGUAGE_IDS = {
    "python": 71,
    "javascript": 63,
    "cpp": 54,
    "csharp": 51,
    "java": 62,
}

@csrf_exempt
def code_editor(request):
    if request.method == "GET":
        return render(request, "Code_editor/editor.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            code = data.get("code", "")
            lang = data.get("lang", "python")
            language_id = LANGUAGE_IDS.get(lang, 71)

            payload = {
                "source_code": code,
                "language_id": language_id,
                "redirect_stderr": True
            }

            res = requests.post(JUDGE0_URL, json=payload, timeout=20)
            result = res.json()

            output_parts = [
                result.get("stdout"),
                result.get("stderr"),
                result.get("compile_output"),
                result.get("message")
            ]
            output = "\n".join([p for p in output_parts if p]) or "لا يوجد ناتج"

            return JsonResponse({"output": output})

        except Exception as e:
            # عرض الخطأ الحقيقي لتصحيح المشاكل
            return JsonResponse({"output": f"حدث خطأ حقيقي: {str(e)}"}, status=500)
