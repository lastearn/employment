"""Generate neural voice MP3s for the trainer (run in Google Cloud Shell).
Usage: pip3 install -q edge-tts && python3 tts.py
"""
import asyncio, json, os
import edge_tts

VOICE = "en-GB-SoniaNeural"  # pleasant British voice
OUT = "audio"


async def one(item, sem):
    path = os.path.join(OUT, item["k"] + ".mp3")
    if os.path.exists(path) and os.path.getsize(path) > 500:
        return
    async with sem:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(item["t"], VOICE, rate="-5%").save(path)
                return
            except Exception as e:  # retry on network hiccups
                print("retry", item["k"], e)
                await asyncio.sleep(2)


async def main():
    os.makedirs(OUT, exist_ok=True)
    items = json.load(open("tts_texts.json", encoding="utf-8"))
    sem = asyncio.Semaphore(6)
    await asyncio.gather(*(one(i, sem) for i in items))
    done = sorted(f[:-4] for f in os.listdir(OUT) if f.endswith(".mp3") and os.path.getsize(os.path.join(OUT, f)) > 500)
    json.dump(done, open(os.path.join(OUT, "index.json"), "w"))
    print(f"OK: {len(done)} of {len(items)} audio files ready")


asyncio.run(main())
