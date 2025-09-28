# YouTube Video Chat App

A simple web application that allows you to chat with YouTube videos by extracting their transcripts and using Google's Gemini AI for intelligent conversations.

## Features

- 🎥 Extract transcripts from any YouTube video with captions
- 💬 Chat with video content using Google Gemini AI
- 🔍 Smart text search to find relevant video segments
- 🌐 Clean web interface with real-time chat
- ⚡ Fast processing without complex vector databases
- 🚀 No quota limits or embedding costs

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd youtube_chat_app
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY="your_google_api_key_here"
```

**Get your Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it in your `.env` file

### 5. Run the Application
```bash
python application.py
```

### 6. Open in Browser
Navigate to: `http://127.0.0.1:5001`

## How to Use

1. **Enter YouTube URL**: Paste any YouTube video URL that has captions/subtitles
2. **Process Video**: Click "Process Video" and wait for transcript extraction
3. **Start Chatting**: Ask questions about the video content
4. **Get Answers**: Receive intelligent responses based on video content and general knowledge

## Example Usage

```
Enter URL: https://youtu.be/dQw4w9WgXcQ
Process Video → Wait for "Video processed successfully!"
Ask: "What is the main topic of this video?"
Get: Intelligent answer based on video transcript
```

## Project Structure

```
youtube_chat_app/
├── application.py          # Main web app (CURRENT VERSION)
├── app.py                 # Complex RAG version (for future development)
├── agent.py               # RAG implementation with Pinecone
├── templates/
│   └── index.html         # Web interface
├── requirements.txt       # All dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## Technical Details

- **Frontend**: HTML/CSS/JavaScript with clean UI
- **Backend**: Flask web framework
- **AI Model**: Google Gemini 1.5 Flash for chat responses
- **Transcript**: YouTube Transcript API for video text extraction
- **Search**: Simple text-based search (no vector embeddings)
- **Processing**: Fast in-memory processing without databases

## Troubleshooting

### Common Issues

**"No transcript available"**
- Video must have captions/subtitles enabled
- Try a different video with auto-generated captions

**"API Key Error"**
- Ensure your Google API key is correctly set in `.env`
- Check if the API key has proper permissions

**"Port already in use"**
- Change port in `application.py`: `app.run(port=5002)`
- Or kill the existing process

**"Module not found"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## Development

### Current Version (application.py)
- ✅ Simple and fast
- ✅ No quota limits
- ✅ Works immediately
- ✅ Basic text search

### Future Version (app.py)
- 🔄 Advanced RAG with Pinecone
- 🔄 Vector embeddings for better search
- 🔄 More sophisticated retrieval
- 🔄 Requires additional setup

## Requirements

- Python 3.8+
- Google AI API key (free tier available)
- Internet connection for YouTube access
- YouTube videos with captions/subtitles

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

If you encounter any issues:
1. Check the troubleshooting section
2. Ensure all requirements are installed
3. Verify your API key is working
4. Try with a different YouTube video

---

**Note**: This application uses the simple approach (`application.py`) for immediate functionality. The complex RAG version (`app.py`) is available for advanced users who want to implement vector-based search with Pinecone.