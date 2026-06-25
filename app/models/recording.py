from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import json
from datetime import datetime
from pydub import AudioSegment
import httpx

from app.models.base import get_db
from app.models.recording import Recording
from app.models.user import User
from app.routes.auth import get_current_user

router = APIRouter(prefix="/recordings", tags=["recordings"])

XAI_API_KEY = os.getenv("XAI_API_KEY")
AUDIO_STORAGE = "audio_storage"

os.makedirs(AUDIO_STORAGE, exist_ok=True)

@router.post("/upload")
async def upload_recording(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(('.webm', '.wav', '.mp3')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # Save audio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(AUDIO_STORAGE, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Get duration
    audio = AudioSegment.from_file(file_path)
    duration = len(audio) // 1000  # in seconds

    # Call Grok STT
    transcript = None
    raw_metadata = None
    
    try:
        with open(file_path, "rb") as audio_file:
            files = {"file": audio_file}
            headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.x.ai/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data={"model": "grok-2-audio", "response_format": "verbose_json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get("text")
                    raw_metadata = json.dumps(result)  # Full metadata (diarization, timestamps)
                else:
                    transcript = "Transcription failed. Check API key."
    except Exception as e:
        transcript = f"STT Error: {str(e)}"

    # Save to database
    recording = Recording(
        filename=filename,
        file_path=file_path,
        transcript=transcript,
        raw_metadata=raw_metadata,
        duration=duration,
        owner_id=current_user.id
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)

    return JSONResponse({
        "id": recording.id,
        "filename": filename,
        "transcript": transcript,
        "duration": duration,
        "message": "Recording saved and transcribed successfully!"
    })