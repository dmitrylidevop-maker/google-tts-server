# Google TTS Server

A FastAPI-based Text-to-Speech server using Google Cloud Text-to-Speech API. Supports multiple languages and voices with streaming audio responses.

## Features

- 🎙️ **Text-to-Speech**: Convert text to high-quality speech
- 🌐 **Multi-language**: Supports Russian (RU), Hebrew (HE), and English (EN)
- 🎵 **Voice Selection**: Choose from various Google TTS voices
4. Set environment variable (do NOT commit the key file):
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/your/service-account.json"
  ```

## Quick Start

### Prerequisites

1. **Google Cloud Account**: Enable Text-to-Speech API
2. **Service Account**: Create and download JSON credentials
3. **Docker** (optional): For containerized deployment
# (Recommended) Create virtual environment to avoid "externally-managed-environment" error:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies inside the venv
pip install -r requirements.txt

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Text-to-Speech API
3. Create a Service Account and download the JSON key
4. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/your/service-account.json"
   ```

### 2. Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd google-tts-server

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### 3. Docker Deployment

```bash
# Build the image
docker build -t google-tts-server .

# Recommended approach: Load credentials from .env and run with your user/group ID
source .env
docker run -d \
  -p 3010:3010 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v "${GOOGLE_APPLICATION_CREDENTIALS}:/app/credentials.json:ro" \
  --user 1000:10 \
  --name tts-server \
  google-tts-server

# Alternative: Run with explicit path (replace with your credentials path)
docker run -d \
  -p 3010:3010 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v "/absolute/path/to/credentials.json:/app/credentials.json:ro" \
  --user 1000:10 \
  --name tts-server \
  google-tts-server

# Or run as root if you encounter permission issues (less secure)
docker run -d \
  -p 3010:3010 \
  --env-file .env \
  --user root \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v "/absolute/path/to/credentials.json:/app/credentials.json:ro" \
  --name tts-server \
  google-tts-server

# Or run with individual environment variables (no .env file needed)
docker run -d \
  -p 3010:3010 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -e PG_HOST=192.168.31.129 \
  -e PG_PORT=5435 \
  -e PG_USER=postgres \
  -e PG_PASS=yourpassword \
  -e PG_DB=postgres \
  -v "/absolute/path/to/your/credentials.json:/app/credentials.json:ro" \
  --name tts-server \
  google-tts-server
```

## API Documentation

### Base URL
```
http://localhost:3010
```

### Endpoints

#### 1. Health Check
```bash
GET /health
4. **Restrict access**: Run behind an authenticated reverse proxy if public
5. **Rate limiting**: Add throttling for abuse prevention in production

**Response:**
```json
{
  "status": "healthy",
  "tts_client": "connected",
  "google_credentials": true
}
```

#### 2. List Available Voices
```bash
GET /voices
```

**Response:**
```json
[
  {
    "name": "en-US-Wavenet-A",
    "language_code": "en-US",
    "gender": "MALE",
    "natural_sample_rate": 24000
  },
  {
    "name": "ru-RU-Wavenet-A",
    "language_code": "ru-RU",
    "gender": "FEMALE",
    "natural_sample_rate": 24000
  }
]
```

#### 3. Text-to-Speech Synthesis
```bash
POST /tts
Content-Type: application/json

{
  "text": "Hello world",
  "voice": "en-US-Wavenet-A",
  "speed": 1.0,
  "pitch": 0.0
}
```

**Parameters:**
- `text` (required): Text to synthesize (1-5000 characters)
- `voice` (required): Voice ID (get from `/voices` endpoint)
- `speed` (optional): Speech speed (0.25-4.0, default: 1.0)
- `pitch` (optional): Voice pitch (-20.0 to 20.0, default: 0.0)

**Response:** MP3 audio stream

## Usage Examples

### Using curl

#### Basic TTS Request (English)
```bash
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "en-US-Wavenet-A"}' \
  --output audio.mp3
```

#### Russian TTS
```bash
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет мир", "voice": "ru-RU-Wavenet-A"}' \
  --output russian_audio.mp3
```

#### Hebrew TTS
```bash
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "שלום עולם", "voice": "he-IL-Wavenet-A"}' \
  --output hebrew_audio.mp3
```

#### Custom Speed and Pitch
```bash
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test with custom settings",
    "voice": "en-US-Wavenet-B",
    "speed": 1.5,
    "pitch": 2.0
  }' \
  --output custom_audio.mp3
```

### Using Python

```python
import requests

# Get available voices
voices_response = requests.get("http://localhost:3010/voices")
voices = voices_response.json()
print("Available voices:", voices)

# Synthesize speech
tts_data = {
    "text": "Hello from Python!",
    "voice": "en-US-Wavenet-A",
    "speed": 1.0
}

response = requests.post(
    "http://localhost:3010/tts",
    json=tts_data
)

if response.status_code == 200:
    with open("python_audio.mp3", "wb") as f:
        f.write(response.content)
    print("Audio saved successfully!")
else:
    print("Error:", response.json())
```

### Using JavaScript/Fetch

```javascript
// Get voices
fetch('http://localhost:3010/voices')
  .then(response => response.json())
  .then(voices => console.log('Available voices:', voices));

// Synthesize speech
fetch('http://localhost:3010/tts', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Hello from JavaScript!',
    voice: 'en-US-Wavenet-A'
  })
})
.then(response => response.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
});
```

## Supported Languages

The server supports voices for these languages:
- **English (EN)**: en-US, en-GB, en-AU, etc.
- **Russian (RU)**: ru-RU
- **Hebrew (HE)**: he-IL

Use the `/voices` endpoint to get the complete list of available voices.

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account JSON file (required)
- `PORT`: Server port (default: 3010)
- `HOST`: Server host (default: 0.0.0.0)

### Voice Parameters

- **Speed**: Controls speech rate (0.25 = very slow, 4.0 = very fast)
- **Pitch**: Adjusts voice pitch (-20.0 = very low, 20.0 = very high)

## Security & Privacy

⚠️ **Important for GitHub repositories:**

1. **Never commit credentials**: The `.gitignore` file excludes credential files
2. **Use environment variables**: Credentials are loaded from environment
3. **No audio storage**: Audio is streamed directly, not saved on server
4. **Rate limiting**: Consider implementing rate limiting for production

## Error Handling

The API provides detailed error responses:

```json
{
  "detail": "Error description",
  "error": "error_code"
}
```

Common errors:
- `400`: Invalid input parameters
- `503`: Google TTS API unavailable or credentials issue
- `500`: Internal server error

## Production Deployment

For production deployment:

1. **Use HTTPS**: Deploy behind a reverse proxy (nginx, Traefik)
2. **Environment variables**: Store credentials securely
3. **Resource limits**: Set appropriate memory/CPU limits
4. **Monitoring**: Add logging and metrics collection
5. **Rate limiting**: Implement API rate limiting
6. **Scaling**: Use multiple container instances

## Development

### Project Structure
```
google-tts-server/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container definition
├── docker-compose.yml  # Local development setup
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Make sure to comply with Google Cloud TTS API terms of service.

## Support

For issues and questions:
1. Check the [Google Cloud TTS documentation](https://cloud.google.com/text-to-speech/docs)
2. Review API error responses
3. Verify your Google Cloud credentials and quotas