# Farm Credibly — AI Agricultural Assistant

A Telegram-based AI assistant for Jamaican farmers, powered by [Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous Research).

Farmers send voice or text messages. Clara — the assistant — replies in Jamaican Creole with grounded, practical agricultural advice: crop disease, pest management, soil health, market prices, weather adaptation, and more.

---

## What's In This Repo

This repository contains **only the Farm Credibly customisations**. The Hermes Agent framework itself is pulled directly from the official Docker image — no fork, no divergence, no maintenance burden.

| File | Purpose |
|---|---|
| `SOUL.md` | Clara's persona — Jamaican Creole voice, domain knowledge, example conversations |
| `config.yaml` | Farm Credibly configuration — Jamaican TTS voice, STT, model, Telegram gateway |
| `docker-compose.yml` | Pulls official Hermes image, mounts config |
| `.env.example` | Template for API keys (copy to `.env`, never commit) |

---

## Quick Start

### 1. Prerequisites

- Docker + Docker Compose on a VPS (tested on Ubuntu 24.04, 2GB+ RAM)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An [OpenRouter](https://openrouter.ai) API key

### 2. Deploy

```bash
git clone https://github.com/developdigitally-hermes/fc-ai-chatbot.git
cd fc-ai-chatbot

# Configure secrets
cp .env.example .env
nano .env   # fill in TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY,
           # TELEGRAM_ALLOWED_USER_ID and TELEGRAM_ALLOWED_USERS (same value for both)

# Start
docker compose up -d

# Check logs
docker compose logs -f
```

### 3. Test

Send a message to your Telegram bot. Clara will respond.

Send a **voice message** — Clara will transcribe it and reply with audio in a Jamaican English voice.

---

## Updating Hermes

Hermes releases updates frequently. To update:

```bash
docker compose pull
docker compose up -d
```

That's it. Your SOUL.md, config.yaml, and all farmer data are preserved in the `hermes-data` volume.

---

## Customising Clara

### Change the persona
Edit `SOUL.md`. Changes take effect immediately — no restart needed.

### Change the model, voice, or STT
Edit `config.yaml`, then restart:
```bash
docker compose restart hermes
```

### Add custom skills
Create a `skills/` directory and mount it in `docker-compose.yml`:
```yaml
volumes:
  - ./skills:/opt/data/skills/custom
```

---

## Voice Configuration

| Provider | Cost | Quality | Setup |
|---|---|---|---|
| Edge TTS (`en-JM-OrlaNeural`) | Free | Good — native Jamaican English voice | Already configured |
| ElevenLabs | ~$0.30/1K chars | Excellent — can voice-clone | Add `ELEVENLABS_API_KEY` to `.env`, set `tts.provider: elevenlabs` in `config.yaml` |
| faster-whisper (local STT) | Free | Good | Default — auto-downloads ~150MB model on first use |
| Groq STT | Free tier | Fast | Add `GROQ_API_KEY` to `.env`, set `stt.provider: groq` in `config.yaml` |

---

## Architecture

```
Telegram farmer message
        ↓
  Hermes Gateway (nousresearch/hermes-agent Docker image)
        ↓
  [voice] → faster-whisper STT → transcript
        ↓
  Clara persona (SOUL.md) + Farm Credibly config (config.yaml)
        ↓
  LLM (Claude Haiku via OpenRouter)
        ↓
  [voice input] → Edge TTS (en-JM-OrlaNeural) → audio reply
        ↓
  Telegram reply (text + optional voice bubble)
```

---

## Upstream

Hermes Agent is developed by [Nous Research](https://nousresearch.com).
Upstream repo: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
Docker image: `nousresearch/hermes-agent:latest`
