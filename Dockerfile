FROM python:3.10-slim-bullseye AS base

# System deps for audio + TTS
RUN echo "deb [trusted=yes] http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://deb.debian.org/debian-security bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb [trusted=yes] http://deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        libpulse-dev \
        portaudio19-dev \
        espeak-ng \
        alsa-utils \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt
RUN pip list

COPY app/ .

# Create non-root user
RUN useradd -ms /bin/bash runner
USER runner

ENTRYPOINT ["python", "voice_exec.py"]