# Grok Audio Transcriber

A full-stack web application for recording short audio clips, transcribing them using xAI's Grok STT API, and managing transcripts with user authentication.

## Features
- **Audio Recording**: Record short audio clips (up to ~1 minute) directly in the browser.
- **Transcription**: Powered by Grok STT with speaker diarization, word-level timestamps.
- **Playback**: Play back audio sentence-by-sentence, highlighted transcript.
- **User Management**: Secure login/register to save personal audio clips and transcripts.
- **UI**: Modern, pleasant, responsive design.
- **Deployment**: Docker support for easy self-hosting.

## Tech Stack
- **Backend**: Python with FastAPI
- **Frontend**: HTML/CSS/JS + HTMX + Tailwind CSS
- **Database**: SQLite (easy to swap to Postgres)
- **Auth**: FastAPI Users + JWT
- **STT**: xAI Grok Speech-to-Text API
- **Audio**: ffmpeg/pydub for processing

## Why Python/FastAPI?
Excellent balance of speed of development, audio libs, and production readiness.

## Project Structure (planned)
grok-audio-transcriber/
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── audio_storage/
├── database/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
