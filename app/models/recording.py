# Inside the upload_recording function - improved STT call
try:
    with open(file_path, "rb") as audio_file:
        files = {"file": audio_file}
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.x.ai/v1/stt",   # Updated endpoint
                headers=headers,
                files=files,
                data={
                    "model": "grok-stt",      # or grok-2-audio if needed
                    "diarize": "true",        # ← Enable diarization
                    "response_format": "verbose_json",
                    "language": "en"          # Optional: helps with formatting
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("text")
                raw_metadata = json.dumps(result)  # Store everything (words + speakers)
                
                # Optional: Pretty diarized transcript
                if "words" in result:
                    diarized_text = group_by_speaker(result["words"])
                    # You can save this too
            else:
                ...
except Exception as e:
    ...