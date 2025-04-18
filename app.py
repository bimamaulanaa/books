from flask import Flask, render_template, request, jsonify, session
import os
import openai
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='.')
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24)  # Secret key for session

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client based on version
try:
    # Try v1 style initialization
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_VERSION = 1
except TypeError:
    # Fall back to v0 style initialization
    client = openai
    OPENAI_VERSION = 0

@app.route('/')
def index():
    """Render the main page."""
    # Generate a unique session ID if not already present
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['messages'] = []  # Initialize empty message history
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Process the chat request and return the response."""
    try:
        # Get user input from the request
        user_input = request.json.get('message', '')
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize messages array if not present in session
        if 'messages' not in session:
            session['messages'] = []
        
        # Read the sources of knowledge from list.txt
        try:
            with open('list.txt', 'r', encoding='utf-8') as file:
                sources_of_knowledge = file.read()
        except Exception as e:
            # If file reading fails, use a fallback message
            sources_of_knowledge = "Error reading sources: " + str(e)
        
        # Define the system message for the AI
        system_message = f"""
        You are Aitawfiq, an expert comparative tafsir and Qur'anic sciences model, fine-tuned from Jais.
        Your responses are strictly based on the following sources of knowledge:

        {sources_of_knowledge}

        ---

        ### TASK
        You will:
        - Answer only based on the above sources
        - Reject any question that does not relate to these texts
        - Compare interpretations of specific ayahs or surahs from at least two of the tafsir works
        - Include **direct thematic or linguistic comparisons**
        - Highlight **reconciliation points** between different interpretations when possible
        - Respond only in **Arabic or English**
        
        ### IMPORTANT INSTRUCTION
        If the user asks about what knowledge you have or what sources you're based on, specifically list the sources from the above knowledge base. Do not summarize the categories; instead, provide the actual titles and authors of the works listed. You can organize them by their categories as shown in the knowledge base.

        ### FORMAT
        1. Tafsir 1: [Author]
        - [Extract or summarize the author's interpretation]
        2. Tafsir 2: [Author]
        - [Extract or summarize the author's interpretation]
        3. Comparison
        - [Key differences]
        4. Reconciliation Point
        - [Where interpretations align]
        """
        
        # Add the new user message to the conversation history
        session['messages'].append({"role": "user", "content": user_input})
        
        # Prepare the messages for the API call
        # First, add the system message
        messages = [{"role": "system", "content": system_message}]
        
        # Then add the conversation history (limited to last 10 messages to avoid token limits)
        conversation_history = session['messages'][-10:]
        messages.extend(conversation_history)
        
        # Call the OpenAI API with the full conversation context
        if OPENAI_VERSION == 1:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            ai_response = response.choices[0].message.content
        else:
            response = client.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            ai_response = response.choices[0].message.content
        
        # Add the AI response to the conversation history
        session['messages'].append({"role": "assistant", "content": ai_response})
        
        # Save the updated session
        session.modified = True
        
        return jsonify({"response": ai_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    """Clear the conversation history."""
    if 'messages' in session:
        session['messages'] = []
        session.modified = True
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True) 