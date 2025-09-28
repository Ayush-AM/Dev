# Complex RAG implementation with Pinecone and embeddings
# This is kept for future development
# Use application.py for the current working version

from flask import Flask, render_template, request, jsonify, session
import os
from agent import process_youtube_video
import uuid
import asyncio
import nest_asyncio

# Fix for event loop issues in Flask threads
nest_asyncio.apply()

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Store conversation chains in memory (use Redis in production)
conversation_chains = {}

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
        
        # Ensure event loop exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Process video and create conversation chain
        conversation_chain = process_youtube_video(youtube_url)
        conversation_chains[session_id] = conversation_chain
        
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        print(f"Error in process_video: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'question' not in data:
            return jsonify({'success': False, 'error': 'Missing data'})
            
        session_id = data['session_id']
        question = data['question']
        
        if session_id not in conversation_chains:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        # Ensure event loop exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        conversation_chain = conversation_chains[session_id]
        response = conversation_chain({"question": question})
        
        return jsonify({'success': True, 'answer': response['answer']})
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)