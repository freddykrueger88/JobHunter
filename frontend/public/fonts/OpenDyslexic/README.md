# OpenDyslexic Font

Lizenz: SIL Open Font License 1.1 (OFL)
Quelle: https://opendyslexic.org
Version: 0.91.12

Dateien:
- OpenDyslexic-Regular.woff2
- OpenDyslexic-Bold.woff2
- OpenDyslexic-Italic.woff2

## Einbindung
Die Font-Dateien müssen einmalig von https://opendyslexic.org heruntergeladen
und in diesen Ordner gelegt werden. Sie sind bewusst nicht im Git-Repo
enthalten (Dateigröße), werden aber von `index.css` referenziert.

```bash
# Automatischer Download beim Docker-Build (siehe Dockerfile):
RUN curl -L https://github.com/antijingoist/opendyslexic/releases/latest/download/OpenDyslexic-Regular.woff2 \
    -o /app/public/fonts/OpenDyslexic/OpenDyslexic-Regular.woff2
```

## Lizenztext
This Font Software is licensed under the SIL Open Font License, Version 1.1.
Commercial use, redistribution and modification are permitted.
