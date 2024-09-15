from flask import Flask, render_template, request, jsonify, send_from_directory
from modal import App, web_endpoint
from modal_inference import generate
import base64
import modal
import uuid
import os

ANIMATION_DIR = "animations"
os.makedirs(ANIMATION_DIR, exist_ok=True)

app = Flask(__name__, static_folder='static')

# Initialize Modal stubs
generate_manim_animation = modal.Function.lookup("manim-renderer", "generate_manim_animation")
generate_manim_animation.keep_warm(2)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        return process_query(query)
    return render_template('index.html')

@app.route('/process_query', methods=['POST'])
def process_query():
    try:
        query = request.json['query']
        
        # Call the Modal function for LLM inference
        result = generate(f"Provide a detailed explanation about: {query}")
        
        content = result['main_content']
        subtopics = result['subtopics']
        
        # Check if it's a STEM query
        animation_path = None
        if is_stem_query(query):
            # Generate Manim animation
            animation_data = generate_manim_animation.remote(content)
            if animation_data:
                animation_path = save_animation_to_file(animation_data)
    
        return jsonify({
            'content': content,
            'subtopics': subtopics,
            'animation': animation_path,  # This will be the file path or None
        })
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_subtopic', methods=['POST'])
def get_subtopic():
    try:
        subtopic = request.json['subtopic']
        result = generate(f"Provide detailed information about the subtopic: {subtopic}", is_subtopic=True)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing subtopic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json['message']
        highlighted_text = request.json.get('highlighted_text')
        response = chat_with_assistant(message, highlighted_text)
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error processing chat: {e}")
        return jsonify({'error': 'An error occurred while processing your chat.'}), 500

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

def chat_with_assistant(message, highlighted_text=None):
    prompt = f"User message: {message}\n"
    if highlighted_text:
        prompt += f"Highlighted text: {highlighted_text}\n"
    prompt += "Please provide a helpful response."
    return generate(prompt)

def save_animation_to_file(animation_data: str) -> str:
    """
    Save the base64-encoded animation data to a file and return the file path.
    """
    filename = f"animation_{uuid.uuid4()}.gif"
    filepath = os.path.join(ANIMATION_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(animation_data))
    
    return filepath

if __name__ == '__main__':
    app.run(port=4001, debug=True)
