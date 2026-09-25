from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

SARVAM_URL = "https://api.sarvam.ai"
@app.post("/multilingual")
async def multilingual(
    key: str = Form(None),
    audio_file: UploadFile = File(...),  # Uploaded audio file
    model: str = Form("saaras:v4"),
    language_code: str = Form("unknown"),
    mode: str = Form("translate"),
    sample_rate: str = Form("16000"),
):
    # Use provided key from form field, otherwise fallback to the hardcoded token
    api_token = key if key else None
    if not api_token:
        return JSONResponse({'error': {'message': 'Invalid or missing authentication credentials', 'code': 'invalid_api_key_error', 'request_id': '20260925_7d1bd534-4747-4772-9e24-b66720291dc3'}})

    headers = {
        "Authorization":api_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://indus.sarvam.ai",
        "Referer": "https://indus.sarvam.ai/",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
    }

    data = {
        "model": model,
        "language_code": language_code,
        "mode": mode,
        "sample_rate": sample_rate,
    }

    # Read the audio bytes directly from FastAPI UploadFile
    audio_bytes = await audio_file.read()

    files = {
        "file": (
            audio_file.filename,
            audio_bytes,
            audio_file.content_type or "audio/wav",
        )
    }
    transcribe_api=f"{SARVAM_URL}/speech-to-text"
    try:
        response = requests.post(
            transcribe_api, headers=headers, data=data, files=files, verify=False
        )
        return JSONResponse(
            content=response.json(), status_code=response.status_code
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(e)}"
        )

@app.post("/translate")
async def translate(
    key: str = Form(None),
    input: str = Form(...),  # Text to translate
    source_language_code: str = Form("auto"),
    target_language_code: str = Form("hi-IN"),
    model: str = Form("mayura:v1"),
    numerals_format: str = Form("native"),
    mode: str = Form("formal"),
    output_script: str = Form("roman"),
):
    # Use provided key from form field, otherwise return auth error
    api_token = key if key else None
    if not api_token:
        return JSONResponse(
            status_code=401,
            content={
                'error': {
                    'message': 'Invalid or missing authentication credentials',
                    'code': 'invalid_api_key_error',
                    'request_id': '20260925_7d1bd534-4747-4772-9e24-b66720291dc3'
                }
            }
        )

    # Ensure Authorization header is properly prefixed
    authorization_header = api_token if api_token.startswith("Bearer ") else f"Bearer {api_token}"

    headers = {
        "Authorization": authorization_header,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://indus.sarvam.ai",
        "Referer": "https://indus.sarvam.ai/",
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua": '"Chromium";v="154", "Google Chrome";v="154", "Not A(Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
    }

    payload = {
        "input": input,
        "source_language_code": source_language_code,
        "target_language_code": target_language_code,
        "model": model,
        "numerals_format": numerals_format,
        "mode": mode,
        "output_script": output_script
    }
    SARVAM_TRANSLATE_URL=f"{SARVAM_URL}/translate"
    try:
        response = requests.post(
            SARVAM_TRANSLATE_URL, headers=headers, json=payload, verify=False
        )
        return JSONResponse(
            content=response.json(), status_code=response.status_code
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(e)}"
        )
