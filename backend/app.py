from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
jwt = JWTManager(app)

API_KEY = "super-secret-token"
BASE_URL = "https://hackmit--example-vllm-openai-compatible-serve.modal.run/v1"

client = OpenAI(api_key=API_KEY)
client.base_url = BASE_URL

# In-memory storage for user interests (replace with a database in a real application)
user_interests = {}

@app.route('/login', methods=['POST'])
def login():
    # Implement your login logic here
    # For demonstration purposes, we'll use a dummy user
    access_token = create_access_token(identity='user123')
    return jsonify(token=access_token), 200

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
    return user_interests.get(user_id, [])

def add_user_interest(user_id, interest):
    if user_id not in user_interests:
        user_interests[user_id] = []
    if interest not in user_interests[user_id]:
        user_interests[user_id].append(interest)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)