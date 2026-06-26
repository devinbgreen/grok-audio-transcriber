from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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
    """Group words into speaker turns for display"""
    if not words:
        return ""
    turns = []
    current_speaker = None
    current_text = []
    
    for word in words:
        speaker = word.get("speaker", 0)
        if speaker != current_speaker and current_text:
            turns.append((current_speaker, " ".join(current_text)))
            current_text = []
        current_speaker = speaker
        current_text.append(word.get("text", ""))
    
    if current_text:
        turns.append((current_speaker, " ".join(current_text)))
    
    colors = ["#1e40af", "#166534", "#9f1239", "#854d0e"]
    formatted = []
    for s, text in turns:
        color = colors[s % len(colors)]
        formatted.append(f'<span style="color:{color};font-weight:500;">Speaker {s+1}:</span> {text}')
    return "<br>".join(formatted)

@router.post("/upload")
async def upload_recording(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(('.webm', '.wav', '.mp3', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    # Save original recording
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = f"{current_user.id}_{timestamp}_{file.filename}"
    original_path = os.path.join(AUDIO_STORAGE, original_filename)
    
    with open(original_path, "wb") as buffer:
        buffer.write(await file.read())

    # Convert to WAV (Grok STT prefers this)
    wav_path = original_path.rsplit('.', 1)[0] + ".wav"
    audio = AudioSegment.from_file(original_path)
    audio.export(wav_path, format="wav")

    # Use WAV for transcription
    transcript, raw_metadata, diarized_html = await transcribe_with_grok(wav_path)

    duration = len(audio) // 1000

    # Save to DB
    recording = Recording(
        filename=original_filename,
        file_path=wav_path,
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
        "filename": original_filename,
        "transcript": transcript,
        "diarized_html": diarized_html,
        "duration": duration,
        "message": "Recording transcribed successfully!"
    })

async def transcribe_with_grok(audio_path: str):
    if not XAI_API_KEY:
        return "STT API key not configured", None, None

    try:
        # Use proper filename with extension
        filename = os.path.basename(audio_path)
        
        with open(audio_path, "rb") as f:
            files = {"file": (filename, f, "audio/wav")}
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.x.ai/v1/stt",
                    headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                    files=files,
                    data={
                        "model": "grok-stt",
                        "diarize": "true",
                        "response_format": "verbose_json"
                    }
                )
                
                if response.status_code != 200:
                    err = f"STT Error: {response.text[:400]}"
                    print(err)
                    return err, None, err

                result = response.json()
                transcript = result.get("text", "")
                raw_metadata = json.dumps(result)
                
                words = result.get("words", [])
                diarized_html = group_by_speaker(words)
                
                return transcript, raw_metadata, diarized_html
    except Exception as e:
        err = f"Transcription failed: {str(e)}"
        print(err)
        return err, None, err
        