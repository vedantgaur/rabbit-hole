import os
from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import io
import modal

app = Flask(__name__)

users = {
    "user@example.com": {
        "password": generate_password_hash("password123"),
        "interests": ["AI", "Machine Learning", "Web Development"]
    }
}

# Modal setup
stub = modal.Stub("manim-renderer")
manim_function = modal.Function.lookup("manim-renderer", "render_manim")

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    if email in users and check_password_hash(users[email]['password'], password):
        return jsonify({"message": "Login successful", "email": email}), 200
    return jsonify({"message": "Bad username or password"}), 401

@app.route('/interests', methods=['GET', 'POST'])
def user_interests():
    email = request.args.get('email')
    if email not in users:
        return jsonify({"message": "User not found"}), 404
    
    if request.method == 'GET':
        return jsonify(interests=users[email]['interests']), 200
    
    elif request.method == 'POST':
        new_interest = request.json.get('interest')
        if not new_interest:
            return jsonify({"message": "Missing interest"}), 400
        
        users[email]['interests'].append(new_interest)
        return jsonify({"message": "Interest added successfully"}), 200

@app.route('/search', methods=['POST'])
def search():
    email = request.json.get('email')
    if email not in users:
        return jsonify({"message": "User not found"}), 404
    
    user_interests = users[email]['interests']
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

@app.route('/render_manim', methods=['POST'])
def render_manim():
    manim_code = request.json.get('manim_code')
    if not manim_code:
        return jsonify({"message": "Missing Manim code"}), 400

    try:
        rendered_content = manim_function.call(manim_code)
        return send_file(
            io.BytesIO(rendered_content),
            mimetype='image/gif',
            as_attachment=True,
            download_name='animation.gif'
        )
    except Exception as e:
        return jsonify({"message": f"Error rendering Manim: {str(e)}"}), 500

def generate_personalized_content(query, interests):
    # Placeholder function - replace with actual implementation
    return f"Personalized content for query: {query}, considering interests: {', '.join(interests)}"

def generate_manim_code(query):
    # Placeholder function - replace with actual implementation
    return f"""
from manim import *

class ManimDemo(Scene):
    def construct(self):
        text = Text("{query}")
        self.play(Write(text))
        self.wait()
    """

def generate_music_snippet(query):
    # Placeholder function - replace with actual implementation
    return "URL_to_generated_music_snippet"

def is_stem_query(query):
    stem_keywords = [
        'math', 'mathematics', 'algebra', 'geometry', 'calculus', 'statistics', 'probability',
        'physics', 'mechanics', 'thermodynamics', 'electromagnetism', 'quantum', 'relativity',
        'chemistry', 'organic', 'inorganic', 'biochemistry', 'molecular', 'atomic',
        'biology', 'genetics', 'ecology', 'evolution', 'cell', 'organism', 'anatomy',
        'engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'software',
        'computer science', 'algorithm', 'data structure', 'programming', 'coding',
        'artificial intelligence', 'machine learning', 'neural network', 'deep learning',
        'robotics', 'automation', 'cybernetics', 'nanotechnology', 'biotechnology',
        'astronomy', 'astrophysics', 'cosmology', 'planet', 'star', 'galaxy',
        'environmental science', 'climate', 'geology', 'meteorology', 'oceanography',
        'neuroscience', 'cognitive science', 'psychology', 'behavioral science',
        'data science', 'big data', 'analytics', 'visualization', 'modeling',
        'cryptography', 'information theory', 'network theory', 'graph theory',
        'optimization', 'linear algebra', 'differential equations', 'number theory',
        'topology', 'set theory', 'logic', 'discrete mathematics', 'combinatorics',
        'operations research', 'systems engineering', 'control theory', 'signal processing',
        'materials science', 'polymer', 'metallurgy', 'ceramics', 'composites',
        'bioinformatics', 'genomics', 'proteomics', 'systems biology', 'synthetic biology'
    ]
    return any(keyword in query.lower() for keyword in stem_keywords)

def is_music_query(query):
    music_keywords = [
        'music', 'song', 'melody', 'rhythm', 'harmony', 'composer', 'singer', 'musician',
        'band', 'orchestra', 'symphony', 'concert', 'opera', 'jazz', 'blues', 'rock',
        'pop', 'hip hop', 'rap', 'classical', 'baroque', 'romantic', 'contemporary',
        'electronic', 'dance', 'techno', 'house', 'ambient', 'folk', 'country',
        'reggae', 'ska', 'punk', 'metal', 'alternative', 'indie', 'r&b', 'soul',
        'funk', 'disco', 'gospel', 'choral', 'acapella', 'instrumental', 'vocal',
        'lyrics', 'chord', 'scale', 'key', 'tempo', 'time signature', 'pitch',
        'timbre', 'tone', 'note', 'staff', 'clef', 'octave', 'interval', 'triad',
        'arpeggio', 'progression', 'cadence', 'modulation', 'transposition',
        'counterpoint', 'fugue', 'sonata', 'concerto', 'suite', 'etude', 'nocturne',
        'prelude', 'overture', 'aria', 'recitative', 'libretto', 'score', 'arrangement',
        'orchestration', 'instrumentation', 'ensemble', 'quartet', 'quintet', 'sextet',
        'conductor', 'virtuoso', 'improvisation', 'jam', 'gig', 'tour', 'album',
        'single', 'EP', 'remix', 'cover', 'sample', 'loop', 'beat', 'bassline',
        'riff', 'hook', 'verse', 'chorus', 'bridge', 'coda', 'intro', 'outro',
        'crescendo', 'diminuendo', 'forte', 'piano', 'staccato', 'legato', 'vibrato',
        'tremolo', 'glissando', 'portamento', 'syncopation', 'polyrhythm', 'ostinato',
        'leitmotif', 'tone row', 'atonality', 'microtonality', 'serialism', 'minimalism'
    ]
    return any(keyword in query.lower() for keyword in music_keywords)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))