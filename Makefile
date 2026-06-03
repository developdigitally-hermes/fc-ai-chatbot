.PHONY: up down logs restart pull verify-audio verify-stt verify-tts shell

# ── Lifecycle ────────────────────────────────────────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart hermes

logs:
	docker compose logs -f hermes

pull:
	docker compose pull && docker compose up -d

# ── Audio verification ────────────────────────────────────────────────────────

verify-audio: verify-stt verify-tts
	@echo ""
	@echo "✅ Audio pipeline ready."
	@echo "   Send a voice message to your Telegram bot to test end-to-end."

verify-stt:
	@echo "→ Checking faster-whisper (STT)..."
	@docker compose exec hermes python3 -c \
		"from faster_whisper import WhisperModel; print('  ✅ faster-whisper OK')" \
		2>&1 || (echo "  ❌ faster-whisper not available"; exit 1)
	@echo "→ Checking STT config..."
	@docker compose exec hermes python3 -c \
		"from hermes_cli.config import load_config; c=load_config(); \
		 stt=c.get('stt',{}); print(f'  provider: {stt.get(\"provider\",\"local\")}'); \
		 print(f'  model:    {stt.get(\"local\",{}).get(\"model\",\"base\")}'); \
		 print('  ✅ STT config OK')"

verify-tts:
	@echo "→ Checking edge-tts (TTS)..."
	@docker compose exec hermes python3 -c \
		"import edge_tts; print('  ✅ edge-tts OK')" \
		2>&1 || (echo "  ❌ edge-tts not available"; exit 1)
	@echo "→ Checking TTS voice..."
	@docker compose exec hermes python3 -c \
		"from hermes_cli.config import load_config; c=load_config(); \
		 tts=c.get('tts',{}); \
		 print(f'  provider: {tts.get(\"provider\",\"edge\")}'); \
		 print(f'  voice:    {tts.get(\"edge\",{}).get(\"voice\",\"(default)\")}'); \
		 print('  ✅ TTS config OK')"
	@echo "→ Synthesising test phrase..."
	@docker compose exec hermes python3 -c \
		"import asyncio, edge_tts, tempfile, os; \
		 async def test(): \
		     c = edge_tts.Communicate('Wah gwaan, farmer. Mi name is Clara.', voice='en-JM-OrlaNeural'); \
		     f = tempfile.mktemp(suffix='.mp3'); \
		     await c.save(f); \
		     size = os.path.getsize(f); os.unlink(f); \
		     print(f'  ✅ TTS synthesis OK ({size} bytes generated)'); \
		 asyncio.run(test())"

# ── Utilities ─────────────────────────────────────────────────────────────────

shell:
	docker compose exec hermes bash

config:
	docker compose exec hermes cat /opt/data/config.yaml

soul:
	docker compose exec hermes cat /opt/data/SOUL.md
