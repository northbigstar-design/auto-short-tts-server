
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import edge_tts

app = FastAPI()

VOICES = {
    "남성1": "ko-KR-InJoonNeural",
    "남성2": "ko-KR-HyunsuMultilingualNeural",
    "여성1": "ko-KR-SunHiNeural",
    "여성2": "ko-KR-JiMinNeural",
}

class Narration(BaseModel):
    text: str
    voice: str = "AI가 선택"

@app.get("/")
def home():
    return {"status": "ok", "service": "자동숏츠제작 음성서버"}

@app.post("/tts")
async def make_voice(data: Narration):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="대본을 입력하세요")

    voice = VOICES.get(data.voice, "ko-KR-SunHiNeural")

    try:
        audio = bytearray()
        tts = edge_tts.Communicate(data.text, voice)
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])

        if not audio:
            raise RuntimeError("음성 생성 실패")

        return Response(
            content=bytes(audio),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="narration.mp3"'
            }
        )
    except Exception:
        raise HTTPException(status_code=502, detail="음성 생성 서버 오류")
