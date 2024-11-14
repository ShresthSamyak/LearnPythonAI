from flask import Flask, render_template, request, jsonify, session
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Define learning paths and topics
LEARNING_PATHS = {
    'beginner': [
        'Introduction to Python',
        'Variables and Data Types',
        'Basic Operators',
        'Control Flow (if/else)',
        'Loops (for/while)',
    ],
    'intermediate': [
        'Functions',
        'Lists and Tuples',
        'Dictionaries',
        'Sets',
        'File Handling',
    ],
    'advanced': [
        'Object-Oriented Programming',
        'Modules and Packages',
        'Error Handling',
        'Decorators',
        'Generators',
    ]
}

TUTOR_CONTEXT = """You are a Python programming tutor. Follow these rules:
1. Give short, focused explanations (max 3-4 paragraphs)
2. Always include a simple code example
3. End with a practice exercise
4. Use markdown formatting
5. Be encouraging and friendly
6. Wait for the student to complete the current topic before moving to the next
7. If the student asks a question, answer it briefly and clearly
8. Always start with the absolute basics, assuming the student is a complete beginner"""

WELCOME_MESSAGE = """Welcome to Python AI Tutor! 👋

I'm your personal Python programming tutor. I'll guide you through your learning journey from beginner to advanced concepts. We'll start with the absolute basics and progress step by step.

Current topic: '{current_topic}'

Feel free to:
- Ask questions at any time
- Request examples
- Practice with exercises
- Move to the next topic when you're ready

Let's begin! Would you like me to explain '{current_topic}'?"""

@app.route('/')
def home():
    try:
        # Always start from beginner level and first topic
        session['current_level'] = 'beginner'
        session['current_topic_index'] = 0
        
        # Get current topic for welcome message
        current_topic = LEARNING_PATHS[session['current_level']][session['current_topic_index']]
        welcome_msg = WELCOME_MESSAGE.format(current_topic=current_topic)
        
        print("Debug - Sending variables:", {  # Debug logging
            'learning_paths': LEARNING_PATHS,
            'current_level': session['current_level'],
            'current_topic_index': session['current_topic_index'],
            'welcome_message': welcome_msg
        })
        
        return render_template('index.html', 
                            learning_paths=LEARNING_PATHS,
                            current_level=session['current_level'],
                            current_topic_index=session['current_topic_index'],
                            welcome_message=welcome_msg)
    except Exception as e:
        print("Debug - Error in home route:", str(e))  # Debug logging
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_message = request.json.get('message', '')
        current_level = session.get('current_level', 'beginner')
        current_topic_index = session.get('current_topic_index', 0)
        
        print("Debug - Ask route:", {  # Debug logging
            'user_message': user_message,
            'current_level': current_level,
            'current_topic_index': current_topic_index
        })
        
        # Create context for current lesson
        current_topic = LEARNING_PATHS[current_level][current_topic_index]
        context = f"""Current topic: {current_topic}. Level: {current_level}. {TUTOR_CONTEXT}
        Remember to explain this topic assuming the student is new to programming."""
        
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        response = chat_completion.choices[0].message.content
        print("Debug - API Response:", response[:100] + "...")  # Debug logging
        return jsonify({"response": response})
    
    except Exception as e:
        print("Debug - Error in ask route:", str(e))  # Debug logging
        return jsonify({"error": str(e)}), 500

@app.route('/next_topic', methods=['POST'])
def next_topic():
    try:
        current_level = session.get('current_level', 'beginner')
        current_topic_index = session.get('current_topic_index', 0)
        
        print("Debug - Next topic route (before):", {  # Debug logging
            'current_level': current_level,
            'current_topic_index': current_topic_index
        })
        
        # Progress through topics
        if current_topic_index + 1 < len(LEARNING_PATHS[current_level]):
            session['current_topic_index'] = current_topic_index + 1
        elif current_level == 'beginner':
            session['current_level'] = 'intermediate'
            session['current_topic_index'] = 0
        elif current_level == 'intermediate':
            session['current_level'] = 'advanced'
            session['current_topic_index'] = 0
        
        print("Debug - Next topic route (after):", {  # Debug logging
            'current_level': session['current_level'],
            'current_topic_index': session['current_topic_index']
        })
            
        return jsonify({
            'current_level': session['current_level'],
            'current_topic_index': session['current_topic_index']
        })
    except Exception as e:
        print("Debug - Error in next_topic route:", str(e))  # Debug logging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)