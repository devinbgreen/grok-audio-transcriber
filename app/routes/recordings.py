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

def group_by_speaker(words):
    """Convert Grok STT words into clickable speaker segments"""
    if not words:
        return []
    
    segments = []
    current_speaker = None
    current_text = []
    current_start = None
    
    for word in words:
        speaker = word.get("speaker", 0)
        word_start = word.get("start")
        
        if speaker != current_speaker and current_text:
            segments.append({
                "speaker": current_speaker,
                "text": " ".join(current_text),
                "start": current_start,
                "end": word_start or (current_start + 2)
            })
            current_text = []
        
        if not current_text:
            current_start = word_start
        
        current_speaker = speaker
        current_text.append(word.get("text", ""))
    
    # Last segment
    if current_text:
        segments.append({
            "speaker": current_speaker,
            "text": " ".join(current_text),
            "start": current_start,
            "end": words[-1].get("end", current_start + 2) if words else current_start
        })
    
    return segments

@router.post("/upload")
async def upload_recording(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(('.webm', '.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # Save audio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{file.filename}"
    file_path = os.path.join(AUDIO_STORAGE, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Get duration
    audio = AudioSegment.from_file(file_path)
    duration = len(audio) // 1000

    # Transcription with Grok STT + diarization
    transcript, raw_metadata, segments = await transcribe_with_grok(file_path)

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
        "segments": segments,
        "duration": duration,
        "message": "Recording saved and transcribed!"
    })

async def transcribe_with_grok(audio_path: str):
    if not XAI_API_KEY or XAI_API_KEY == "your_xai_api_key_here":
        return "STT API key not configured. Please add XAI_API_KEY to .env", None, []

    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.x.ai/v1/stt",                    # Correct Grok STT endpoint
                headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                files={"file": audio_data},
                data={
                    "model": "grok-stt",
                    "diarize": "true",
                    "response_format": "verbose_json"
                }
            )
            
            if response.status_code != 200:
                error_text = response.text[:200]
                print(f"STT API Error: {response.status_code} - {error_text}")
                return f"STT Error: {error_text}", None, []

            result = response.json()
            transcript = result.get("text", "")
            raw_metadata = json.dumps(result)
            
            words = result.get("words", [])
            segments = group_by_speaker(words)
            
            return transcript, raw_metadata, segments
            
    except Exception as e:
        print(f"Transcription exception: {e}")
        return f"Transcription failed: {str(e)}", None, []

@router.get("/")
async def list_recordings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recordings = db.query(Recording).filter(
        Recording.owner_id == current_user.id
    ).order_by(Recording.created_at.desc()).all()
    
    return [{
        "id": r.id,
        "filename": r.filename,
        "transcript": (r.transcript or "")[:150] + "..." if r.transcript else "",
        "duration": r.duration,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    } for r in recordings]