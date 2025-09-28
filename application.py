from flask import Flask, render_template, request, jsonify
import os
import re
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Store transcripts and chat history
sessions = {}

def extract_video_id(youtube_url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL format.")

def get_youtube_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi().fetch(video_id)
        full_transcript = " ".join([item.text for item in transcript_list])
        return full_transcript
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")

def simple_search(transcript: str, query: str):
    words = query.lower().split()
    sentences = transcript.split('.')
    relevant_parts = []
    
    for i, sentence in enumerate(sentences):
        if any(word in sentence.lower() for word in words):
            start = max(0, i-2)
            end = min(len(sentences), i+3)
            context = '. '.join(sentences[start:end])
            relevant_parts.append(context)
    
    return relevant_parts[:3]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'success': False, 'error': 'No URL provided'})
            
        youtube_url = data['url']
        session_id = str(uuid.uuid4())
        
        video_id = extract_video_id(youtube_url)
        transcript = get_youtube_transcript(video_id)
        
        sessions[session_id] = {
            'transcript': transcript,
            'llm': ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-latest",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7,
            )
        }
        
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'question' not in data:
            return jsonify({'success': False, 'error': 'Missing data'})
            
        session_id = data['session_id']
        question = data['question']
        
        if session_id not in sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = sessions[session_id]
        transcript = session['transcript']
        llm = session['llm']
        
        # Find relevant parts
        relevant_parts = simple_search(transcript, question)
        context = "\n".join(relevant_parts) if relevant_parts else transcript[:2000]
        
        # Create prompt
        prompt = f"""Based on the following video transcript context, answer the user's question.
If the context doesn't contain enough information, you can supplement with your general knowledge.

Video Context:
{context}

Question: {question}

Answer:"""
        
        response = llm.invoke(prompt)
        
        return jsonify({'success': True, 'answer': response.content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5001)