#!/bin/bash

# Google TTS Server Usage Examples
# Make sure the server is running on http://localhost:3010

echo "🎙️ Google TTS Server - Usage Examples"
echo "====================================="

# Check server health
echo "📡 Checking server health..."
curl -s http://localhost:3010/health | python3 -m json.tool

echo -e "\n🎵 Getting available voices..."
curl -s http://localhost:3010/voices | python3 -m json.tool

# Create output directory
mkdir -p examples_output

# English examples
echo -e "\n🇺🇸 English Examples:"
echo "- Basic English (Female)..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world! This is a test of the Google Text-to-Speech API.", "voice": "en-US-Wavenet-A"}' \
  --output examples_output/english_female.mp3

echo "- English Male Voice..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to our text-to-speech service. Please enjoy the demonstration.", "voice": "en-US-Wavenet-B"}' \
  --output examples_output/english_male.mp3

echo "- Fast English..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is spoken at a faster rate for urgent announcements.", "voice": "en-US-Wavenet-A", "speed": 1.5}' \
  --output examples_output/english_fast.mp3

# Russian examples
echo -e "\n🇷🇺 Russian Examples:"
echo "- Basic Russian..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Раннее утро. Сквозь застёгнутую на все пуговицы куртку пробивался прохладный осенний ветер. Парк был почти пуст. Слышался лишь шорох золотистой листвы под ногами и редкие, но громкие крики сойки.", "voice": "ru-RU-Wavenet-A"}' \
  --output examples_output/russian_basic.mp3

echo "- Russian with custom pitch..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Добро пожаловать в наш сервис. Наслаждайтесь демонстрацией возможностей.", "voice": "ru-RU-Wavenet-B", "pitch": 2.0}' \
  --output examples_output/russian_high_pitch.mp3

# Hebrew examples
echo -e "\n🇮🇱 Hebrew Examples:"
echo "- Basic Hebrew..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "שלום עולם! זהו מבחן של מערכת המרת טקסט לדיבור של גוגל.", "voice": "he-IL-Wavenet-A"}' \
  --output examples_output/hebrew_basic.mp3

echo "- Hebrew slower speech..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "ברוכים הבאים לשירות המרת הטקסט לדיבור שלנו. אנא תיהנו מההדגמה.", "voice": "he-IL-Wavenet-B", "speed": 0.8}' \
  --output examples_output/hebrew_slow.mp3

# Mixed content examples
echo -e "\n🌍 Mixed Content Examples:"
echo "- Numbers and text..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "The temperature today is 25 degrees Celsius, with humidity at 60 percent.", "voice": "en-US-Wavenet-A"}' \
  --output examples_output/numbers_text.mp3

echo "- Long text..."
curl -X POST "http://localhost:3010/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a longer text example to demonstrate how the text-to-speech system handles extended content. The system should maintain consistent quality and pronunciation throughout the entire passage, regardless of length.", "voice": "en-US-Wavenet-C"}' \
  --output examples_output/long_text.mp3

echo -e "\n✅ Examples completed!"
echo "📁 Check the 'examples_output' directory for generated audio files."
echo ""
echo "🎧 To play the files (on systems with appropriate audio players):"
echo "   - On Linux: mpg123 examples_output/english_female.mp3"
echo "   - On macOS: afplay examples_output/english_female.mp3"
echo "   - On Windows: start examples_output/english_female.mp3"