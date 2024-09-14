from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import modal

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'rabbit_hole',
    'host': 'localhost',
    'port': 27017
}
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
db = MongoEngine(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# Initialize Modal
modal.init()

class User(db.Document):
    username = db.StringField(unique=True, required=True)
    password = db.StringField(required=True)

class Interest(db.Document):
    user = db.ReferenceField(User)
    topic = db.StringField(required=True)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    new_user.save()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.objects(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/add_interest', methods=['POST'])
@jwt_required()
def add_interest():
    current_user_id = get_jwt_identity()
    data = request.json
    user = User.objects(id=current_user_id).first()
    new_interest = Interest(user=user, topic=data['topic'])
    new_interest.save()
    return jsonify({"message": "Interest added successfully"}), 201

@app.route('/get_interests', methods=['GET'])
@jwt_required()
def get_interests():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    user_interests = Interest.objects(user=user)
    interests = [interest.topic for interest in user_interests]
    return jsonify({"interests": interests}), 200

@app.route('/search', methods=['POST'])
@jwt_required()
def personalized_search():
    current_user_id = get_jwt_identity()
    user = User.objects(id=current_user_id).first()
    user_interests = Interest.objects(user=user)
    interests = [interest.topic for interest in user_interests]
    
    data = request.json
    query = data['query']
    
    # Call the Modal function
    personalized_content = generate_personalized_content.call(query, interests)
    
    return jsonify({
        "content": personalized_content,
        "interests": interests
    }), 200

# Define the Modal function for content generation
@modal.function
def generate_personalized_content(query, interests):
    import openai
    
    # Set up OpenAI API key (you should use environment variables for this in production)
    openai.api_key = 'your-openai-api-key'  # Replace with your actual OpenAI API key
    
    prompt = f"Generate a personalized response for the query: '{query}'. Consider the user's interests: {', '.join(interests)}. Include relevant subtopics and potential follow-up topics, prefixing them with '#'."
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    
    return response.choices[0].text.strip()

if __name__ == '__main__':
    app.run(debug=True)