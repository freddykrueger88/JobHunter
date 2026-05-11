#!/bin/bash
# JobHunter – Ersteinrichtung
set -e

echo "🎯 JobHunter Setup"
echo "=================="

# .env aus Beispiel erstellen falls noch nicht vorhanden
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ .env erstellt aus .env.example"

  # Automatisch SECRET_KEY generieren
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  sed -i "s|changeme_very_long_random_secret_key_here|$SECRET|" .env
  echo "✅ SECRET_KEY generiert"

  # Automatisch ENCRYPTION_KEY generieren
  ENC_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
  sed -i "s|changeme_fernet_key_here|$ENC_KEY|" .env
  echo "✅ ENCRYPTION_KEY generiert"

  echo ""
  echo "⚠️  Bitte DB_PASSWORD in .env anpassen!"
else
  echo "ℹ️  .env existiert bereits – wird nicht überschrieben"
fi

echo ""
echo "🐳 Starte Docker..."
docker compose up -d --build

echo ""
echo "✅ JobHunter läuft!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
