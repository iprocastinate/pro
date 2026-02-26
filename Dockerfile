FROM python:3.10-slim-bookworm

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Update and install dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git wget pv jq python3-dev mediainfo gcc \
    libsm6 libxext6 libfontconfig1 libxrender1 libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Copy FFmpeg binaries from static build
COPY --from=mwader/static-ffmpeg:6.1 /ffmpeg /bin/ffmpeg
COPY --from=mwader/static-ffmpeg:6.1 /ffprobe /bin/ffprobe

# Copy project files
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p encode thumbs downloads

# Run the bot
CMD ["python3", "-m", "bot"]
