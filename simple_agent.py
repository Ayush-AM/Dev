import os
import re
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

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

def simple_search(transcript: str, query: str, context_size: int = 500):
    """Simple text search to find relevant parts"""
    words = query.lower().split()
    transcript_lower = transcript.lower()
    
    # Find sentences containing query words
    sentences = transcript.split('.')
    relevant_parts = []
    
    for i, sentence in enumerate(sentences):
        if any(word in sentence.lower() for word in words):
            # Get context around the sentence
            start = max(0, i-2)
            end = min(len(sentences), i+3)
            context = '. '.join(sentences[start:end])
            relevant_parts.append(context)
    
    return relevant_parts[:3]  # Return top 3 matches

def chat_with_transcript(transcript: str):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
    )
    
    print("\n" + "=" * 50)
    print("YouTube Video Chat is ready!")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 50 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
            
        try:
            # Find relevant parts of transcript
            relevant_parts = simple_search(transcript, user_input)
            
            # Create context from relevant parts
            context = "\n".join(relevant_parts) if relevant_parts else transcript[:2000]
            
            # Create prompt
            prompt = f"""Based on the following video transcript context, answer the user's question.
If the context doesn't contain enough information, you can supplement with your general knowledge.

Video Context:
{context}

Question: {user_input}

Answer:"""
            
            response = llm.invoke(prompt)
            print(f"\nBot: {response.content}\n")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    youtube_url = input("Enter YouTube URL: ").strip()
    
    try:
        print(f"Processing YouTube video: {youtube_url}")
        video_id = extract_video_id(youtube_url)
        print(f"Video ID: {video_id}")
        
        print("Fetching transcript...")
        transcript = get_youtube_transcript(video_id)
        print(f"Transcript length: {len(transcript)} characters")
        
        print("Ready for chat!")
        chat_with_transcript(transcript)
        
    except Exception as e:
        print(f"Error: {str(e)}")