from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from openai import OpenAI
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'om-is-a-fatty'  # Change this to a secure secret key
jwt = JWTManager(app)

API_KEY = "super-secret-token"
BASE_URL = "https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1"

client = OpenAI(api_key=API_KEY)
client.base_url = BASE_URL

# In-memory storage for user interests (replace with a database in a real application)
user_interests = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rabbit_hole_user:your_password@localhost/rabbit_hole_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    interests = db.relationship('Interest', backref='user', lazy=True)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(token=access_token), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/search', methods=['POST'])
@jwt_required()
def search():
    current_user_id = get_jwt_identity()
    interests = get_user_interests(current_user_id)
    query = request.json['query']
    
    content = generate_personalized_content(query, interests)
    
    return jsonify({
        "content": content,
        "interests": interests
    }), 200

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    message = request.json['message']
    context = request.json['context']
    
    prompt = f"Given the context: '{context}', answer the following question: '{message}'"
    
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on given context."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return jsonify({"message": completion.choices[0].message.content.strip()}), 200

@app.route('/interests', methods=['GET', 'POST'])
@jwt_required()
def interests():
    current_user_id = get_jwt_identity()
    
    if request.method == 'GET':
        interests = get_user_interests(current_user_id)
        return jsonify({"interests": interests}), 200
    
    elif request.method == 'POST':
        new_interest = request.json['interest']
        add_user_interest(current_user_id, new_interest)
        return jsonify({"message": "Interest added successfully"}), 200

def generate_personalized_content(query, interests):
    prompt = f"""Generate a personalized response for the query: '{query}'. 
    Consider the user's interests: {', '.join(interests)}. 
    Include relevant subtopics and potential follow-up topics, prefixing them with '#'.
    If the query is STEM-related, include LaTeX formulas where appropriate.
    Limit the response to 500 words."""

    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates personalized content."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

def get_user_interests(user_id):
    user = User.query.get(user_id)
    return [interest.topic for interest in user.interests]

def add_user_interest(user_id, interest):
    user = User.query.get(user_id)
    if not any(i.topic == interest for i in user.interests):
        new_interest = Interest(topic=interest, user_id=user_id)
        db.session.add(new_interest)
        db.session.commit()

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=8080)