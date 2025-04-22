from flask import Flask, render_template, request, jsonify
import sys
import json
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from graph_rag.graph_rag import GraphRAG
from evaluation.evaluate import evaluate_graphrag
from config.config import *

def create_app():
    app = Flask(__name__)
    app.graph_rag = GraphRAG()
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/query', methods=['POST'])
    def query():
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        try:
            response = app.graph_rag.generate_response(question)
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/evaluate', methods=['POST'])
    def evaluate():
        try:
            results = evaluate_graphrag()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
