from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

SARVAM_URL = "https://api.sarvam.ai/speech-to-text"
@app.get("/")
def read_root():
    return {"message": "It's working!"}
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
        return JSONResponse({"request_id":None})

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

    try:
        response = requests.post(
            SARVAM_URL, headers=headers, data=data, files=files, verify=False
        )
        return JSONResponse(
            content=response.json(), status_code=response.status_code
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(e)}"
        )
