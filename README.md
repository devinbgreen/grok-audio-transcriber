# Grok Audio Transcriber

A full-stack web application for recording short audio clips, transcribing them using xAI's Grok STT API, and managing transcripts with user authentication.

## Motivation

This project is a stepping stone to near real-time, automatic Reverse Speech Metaphor disclosure. 
Who would want the pwer of truth, straight from the subconscious, conveniently at their finger tips?

## Usage

Log in and record =]

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

## Quick Start

1. Copy `.env.example` to `.env` and add your `XAI_API_KEY` (get one from [x.ai](https://x.ai))
2. `docker compose up --build` (recommended) or run locally with `uvicorn app.main:app --reload`
3. Open http://localhost:8000
4. Register / Login
5. Click the big mic 🎤 to record short clips (~60s max)
6. Grok STT transcribes with speaker diarization (different colors)
7. Click colored speaker segments in transcript to play that portion of audio
8. All recordings saved securely per user. History supports replay and delete.

**Note**: The xAI STT endpoint and response format may require API key with appropriate access. Check xAI docs for latest `grok-stt` model details.

## Features Delivered
- ✅ Browser audio recording (WebM)
- ✅ Secure user auth (register/login with JWT)
- ✅ Grok STT transcription with diarization
- ✅ Sentence-by-sentence / speaker-turn playback with visual highlight
- ✅ Persistent storage of audio + transcripts
- ✅ Pleasant Tailwind UI with animations and responsive design
- ✅ Docker support
- ✅ History with delete

## Development
- Backend: FastAPI + SQLAlchemy + Pydub
- Frontend: Vanilla JS + Tailwind + custom CSS
- Database: SQLite (`./database/app.db`)
- Audio stored in `./audio_storage/`

## Contributing
- Needs some bug fixing honestly

For production, use a strong `SECRET_KEY`, HTTPS, and consider Postgres + volume backups.
