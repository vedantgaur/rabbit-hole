import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from openai import OpenAI
import requests

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-fallback-secret-key')
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))
db = client[os.environ.get('DB_NAME', 'your_database_name')]

# Collections
users = db.users
interests = db.interests

# OpenAI client setup
API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key')
BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1')

openai_client = OpenAI(api_key=API_KEY)
openai_client.base_url = BASE_URL

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    
    if users.find_one({"email": email}):
        return jsonify({"msg": "Email already registered"}), 400
    
    hashed_password = generate_password_hash(password)
    users.insert_one({"email": email, "password": hashed_password})
    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = users.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/interests', methods=['GET', 'POST'])
@jwt_required()
def user_interests():
    current_user_id = get_jwt_identity()
    
    if request.method == 'GET':
        user_interests = get_user_interests(current_user_id)
        return jsonify(interests=user_interests), 200
    
    elif request.method == 'POST':
        new_interest = request.json.get('interest')
        if not new_interest:
            return jsonify({"msg": "Missing interest"}), 400
        
        add_user_interest(current_user_id, new_interest)
        return jsonify({"msg": "Interest added successfully"}), 200

@app.route('/search', methods=['POST'])
@jwt_required()
def search():
    current_user_id = get_jwt_identity()
    user_interests = get_user_interests(current_user_id)
    query = request.json['query']
    
    content = generate_personalized_content(query, user_interests)
    manim_code = generate_manim_code(query) if is_stem_query(query) else None
    music_snippet = generate_music_snippet(query) if is_music_query(query) else None
    
    return jsonify({
        "content": content,
        "interests": user_interests,
        "manim_code": manim_code,
        "music_snippet": music_snippet
    }), 200

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    message = request.json['message']
    context = request.json['context']
    
    prompt = f"Given the context: '{context}', answer the following question: '{message}'"
    
    completion = openai_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on given context."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return jsonify({"message": completion.choices[0].message.content.strip()}), 200

def generate_personalized_content(query, interests):
    prompt = f"""Generate a personalized response for the query: '{query}'. 
    Consider the user's interests: {', '.join(interests)}. 
    Include relevant subtopics and potential follow-up topics, prefixing them with '#'.
    If the query is STEM-related, include LaTeX formulas where appropriate.
    Limit the response to 500 words."""

    completion = openai_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates personalized content."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

def generate_manim_code(query):
    prompt = f"Generate Manim code for the following query: {query}"
    completion = openai_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Manim code."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()

def generate_music_snippet(query):
    suno_api_url = "https://api.suno.com/generate"
    suno_api_key = os.environ.get('SUNO_API_KEY')
    
    response = requests.post(suno_api_url, 
                             json={"prompt": query}, 
                             headers={"Authorization": f"Bearer {suno_api_key}"})
    
    if response.status_code == 200:
        return response.json().get('audio_url')
    else:
        return None

def get_user_interests(user_id):
    user_interests = interests.find({"user_id": user_id})
    return [interest['topic'] for interest in user_interests]

def add_user_interest(user_id, interest):
    if not interests.find_one({"user_id": user_id, "topic": interest}):
        interests.insert_one({"user_id": user_id, "topic": interest})

def is_stem_query(query):
    stem_keywords = ['math', 'physics', 'chemistry', 'biology', 'engineering']
    return any(keyword in query.lower() for keyword in stem_keywords)

def is_music_query(query):
    music_keywords = ['music', 'song', 'melody', 'rhythm', 'harmony', 'composer', 'singer']
    return any(keyword in query.lower() for keyword in music_keywords)

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))