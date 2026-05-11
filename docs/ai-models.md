# 🤖 AI Models / KI-Modelle

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter uses **Ollama** to run AI models completely locally – no internet connection required, no data leaves your machine.

## Supported Models

| Model | Size | RAM (min) | Speed | German quality | Best for |
|---|---|---|---|---|---|
| **mistral** | 4.1 GB | 8 GB | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Very good | Cover letters, analysis |
| **llama3** | 4.7 GB | 8 GB | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent | Interview prep, coaching |
| **phi3** | 2.3 GB | 4 GB | ⚡⚡⚡⚡ Very fast | ⭐⭐⭐ Good | Quick analysis, low-RAM systems |
| **tinyllama** | 637 MB | 2 GB | ⚡⚡⚡⚡⚡ Fastest | ⭐⭐ Basic | Emergency fallback, very old hardware |
| **llama3.1** | 4.9 GB | 8 GB | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent | Best overall quality |
| **gemma2** | 5.4 GB | 10 GB | ⚡⚡ Medium | ⭐⭐⭐⭐ Very good | Creative texts |

## Recommendation by Use Case

| Use Case | Recommended Model |
|---|---|
| Cover letter generation (German) | `mistral` or `llama3.1` |
| Interview preparation | `llama3` or `llama3.1` |
| ATS score checker | `mistral` (fast + precise) |
| Salary negotiation coach | `llama3` (best reasoning) |
| Low RAM (≤ 8 GB system RAM) | `phi3` |
| Very old hardware / Raspberry Pi | `tinyllama` |

## Install Model

### With Docker (recommended)
```bash
docker exec -it jobhunter-ollama ollama pull mistral
docker exec -it jobhunter-ollama ollama pull llama3
docker exec -it jobhunter-ollama ollama pull phi3
```

### Without Docker
```bash
ollama pull mistral
ollama pull llama3
ollama pull phi3
```

## List Installed Models
```bash
# Docker:
docker exec jobhunter-ollama ollama list
# Manual:
ollama list
```

## Delete Model (free up space)
```bash
docker exec jobhunter-ollama ollama rm tinyllama
```

## GPU Acceleration (NVIDIA)

With NVIDIA GPU, models run **5–10x faster**.

Uncomment in `docker-compose.yml`:
```yaml
# ollama:
#   deploy:
#     resources:
#       reservations:
#         devices:
#           - driver: nvidia
#             count: 1
#             capabilities: [gpu]
```

Then restart:
```bash
docker compose up -d
```

Verify GPU is being used:
```bash
docker exec jobhunter-ollama ollama run mistral "Hello" --verbose
```

## Troubleshooting

#### Model not responding / timeout
1. `docker ps | grep ollama` – is container running?
2. `docker exec jobhunter-ollama ollama list` – is model installed?
3. `docker logs jobhunter-ollama --tail 30` – any errors?
4. `docker compose restart ollama`

#### `Error: model not found`
```bash
docker exec -it jobhunter-ollama ollama pull mistral
```

#### Not enough RAM – system crashes
Switch to smaller model in Settings → 🤖 AI → Model: `phi3` or `tinyllama`

---
---

## Deutsch

JobHunter nutzt **Ollama** um KI-Modelle vollständig lokal auszuführen – keine Internetverbindung nötig, keine Daten verlassen dein Gerät.

## Unterstützte Modelle

| Modell | Größe | RAM (min) | Geschwindigkeit | Deutsch-Qualität | Bestes für |
|---|---|---|---|---|---|
| **mistral** | 4,1 GB | 8 GB | ⚡⚡⚡ Schnell | ⭐⭐⭐⭐ Sehr gut | Anschreiben, Analysen |
| **llama3** | 4,7 GB | 8 GB | ⚡⚡ Mittel | ⭐⭐⭐⭐⭐ Ausgezeichnet | Interview-Vorbereitung |
| **phi3** | 2,3 GB | 4 GB | ⚡⚡⚡⚡ Sehr schnell | ⭐⭐⭐ Gut | Schwache Hardware |
| **tinyllama** | 637 MB | 2 GB | ⚡⚡⚡⚡⚡ Schnellste | ⭐⭐ Basis | älteste Hardware |
| **llama3.1** | 4,9 GB | 8 GB | ⚡⚡ Mittel | ⭐⭐⭐⭐⭐ Ausgezeichnet | Beste Gesamtqualität |
| **gemma2** | 5,4 GB | 10 GB | ⚡⚡ Mittel | ⭐⭐⭐⭐ Sehr gut | Kreative Texte |

## Empfehlung nach Anwendungsfall

| Anwendungsfall | Empfohlenes Modell |
|---|---|
| Anschreiben auf Deutsch | `mistral` oder `llama3.1` |
| Interview-Vorbereitung | `llama3` oder `llama3.1` |
| ATS-Score-Checker | `mistral` (schnell + präzise) |
| Gehaltsnegotiations-Coach | `llama3` (bestes Reasoning) |
| Wenig RAM (≤ 8 GB) | `phi3` |
| Sehr alte Hardware | `tinyllama` |

## Modell installieren

```bash
# Docker:
docker exec -it jobhunter-ollama ollama pull mistral
# Manuell:
ollama pull mistral
```

## GPU-Beschleunigung (NVIDIA)

In `docker-compose.yml` den `deploy`-Block einkommentieren, dann `docker compose up -d`.

## Troubleshooting

- Modell antwortet nicht → `docker compose restart ollama`
- `model not found` → `docker exec -it jobhunter-ollama ollama pull mistral`
- Zu wenig RAM → in Einstellungen auf `phi3` oder `tinyllama` wechseln
