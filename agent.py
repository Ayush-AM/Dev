import os
import re
from typing import List
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# YouTube transcript API
from youtube_transcript_api import YouTubeTranscriptApi

# Pinecone
from pinecone import Pinecone

# Load environment variables
load_dotenv()

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL format.")



def get_youtube_transcript(video_id: str) -> str:
    """Fetch transcript from YouTube video"""
    try:
        # Get transcript using youtube-transcript-api
        transcript_list = YouTubeTranscriptApi().fetch(video_id)

        # Combine all transcript text
        full_transcript = " ".join([item.text for item in transcript_list])

        return full_transcript

    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")


def create_text_chunks(
    text: str, chunk_size: int = 2000, chunk_overlap: int = 400
) -> List[Document]:
    """Split text into chunks using RecursiveCharacterTextSplitter"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    # Split text and create Document objects
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]

    return documents


def setup_pinecone_vectorstore(
    documents: List[Document], video_id: str
) -> PineconeVectorStore:
    """Create and populate Pinecone vector store with embeddings"""

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # Initialize embeddings (using Gemini embedding model)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Create index name based on video ID
    index_name = os.getenv("PINECONE_INDEX_NAME", "youtube-rag-demo")

    # Add metadata to documents
    for i, doc in enumerate(documents):
        doc.metadata = {
            "video_id": video_id,
            "chunk_id": i,
            "source": f"youtube_video_{video_id}",
        }

    # Create vector store from documents
    vectorstore = PineconeVectorStore.from_documents(
        documents=documents, embedding=embeddings, index_name=index_name
    )

    return vectorstore


def create_conversation_chain(
    vectorstore: PineconeVectorStore,
) -> ConversationalRetrievalChain:
    """Create conversational retrieval chain with memory"""

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
    )

    # Create custom prompt template
    custom_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""Use the following pieces of context from the video to answer the question. 
If the context contains relevant information, use it to provide a detailed answer.
If the context doesn't contain enough information to fully answer the question, you can supplement with your general knowledge while clearly indicating what comes from the video vs. your general knowledge.

Context from video:
{context}

Question: {question}

Answer:"""
    )

    # Create memory for conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="answer"
    )

    # Create conversational retrieval chain with custom prompt
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt}
    )

    return conversation_chain


def process_youtube_video(youtube_url: str) -> ConversationalRetrievalChain:
    """Main function to process YouTube video and create RAG chain"""

    print(f"Processing YouTube video: {youtube_url}")

    # Step 1: Extract video ID
    video_id = extract_video_id(youtube_url)
    print(f"Video ID: {video_id}")

    # Step 2: Get transcript
    print("Fetching transcript...")
    transcript = get_youtube_transcript(video_id)
    print(f"Transcript length: {len(transcript)} characters")

    # Step 3: Create text chunks
    print("Creating text chunks...")
    documents = create_text_chunks(transcript)
    print(f"Created {len(documents)} chunks")

    # Step 4: Setup vector store
    print("Setting up vector store...")
    vectorstore = setup_pinecone_vectorstore(documents, video_id)
    print("Vector store created successfully")

    # Step 5: Create conversation chain
    print("Creating conversation chain...")
    conversation_chain = create_conversation_chain(vectorstore)
    print("Conversation chain ready!")

    return conversation_chain


def chat_with_video(conversation_chain: ConversationalRetrievalChain):
    """Interactive chat loop"""
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
            # Get response from conversation chain
            response = conversation_chain({"question": user_input})

            print(f"\nBot: {response['answer']}\n")

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    # Example usage
    youtube_url = input("Enter YouTube URL: ").strip()

    try:
        # Process the video and create conversation chain
        conversation_chain = process_youtube_video(youtube_url)

        # Start interactive chat
        chat_with_video(conversation_chain)

    except Exception as e:
        print(f"Error: {str(e)}")
