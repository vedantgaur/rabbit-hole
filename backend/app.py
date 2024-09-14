from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)

@app.route('/add_interest', methods=['POST'])
def add_interest():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        user = User(username=data['username'])
        db.session.add(user)
        db.session.commit()
    
    interest = Interest(user_id=user.id, topic=data['topic'])
    db.session.add(interest)
    db.session.commit()
    return jsonify({"message": "Interest added successfully"}), 201

@app.route('/get_interests/<username>', methods=['GET'])
def get_interests(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    interests = Interest.query.filter_by(user_id=user.id).all()
    return jsonify({"interests": [interest.topic for interest in interests]}), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)