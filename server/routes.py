from flask import Blueprint, render_template, jsonify, request
from .gmail_helper import search_messages, get_message_content, get_credentials, logout
import os
import sys

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/auth_status')
def auth_status():
    # Check if token.json exists and is valid
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
    token_path = os.path.join(base_path, 'token.json')
    if os.path.exists(token_path):
         return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@bp.route('/api/login', methods=['POST'])
def login():
    try:
        # This will open the browser window for auth
        get_credentials() 
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/logout', methods=['POST'])
def logout_route():
    success = logout()
    return jsonify({'success': success})

@bp.route('/api/search')
def search():
    recipient = request.args.get('recipient')
    keyword = request.args.get('keyword', '')
    
    if not recipient:
        return jsonify([])
    
    # Construct query
    # "from:recipient OR to:recipient" AND keyword
    # We want conversation with this person.
    query = f"(from:{recipient} OR to:{recipient})"
    if keyword:
        query += f" {keyword}"
        
    results = search_messages(query)
    return jsonify(results)

@bp.route('/api/message/<msg_id>')
def message(msg_id):
    content = get_message_content(msg_id)
    return jsonify({'content': content})

@bp.route('/api/batch_content', methods=['POST'])
def batch_content():
    data = request.get_json()
    ids = data.get('ids', [])
    
    results = []
    # Fetch sequentially (could be parallelized but simple is safer for rate limits)
    for msg_id in ids:
        content = get_message_content(msg_id)
        results.append(content)
        
    return jsonify({'contents': results})
