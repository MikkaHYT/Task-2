from flask import Flask, request, jsonify, render_template
import json
import os
import base64
import uuid

app = Flask(__name__)

# File where messages will be stored
messages_file = 'messages.json'

# Directory to store uploaded images
image_upload_dir = 'static/uploads'
os.makedirs(image_upload_dir, exist_ok=True)

# Function to load messages from the file
def load_messages():
    if os.path.exists(messages_file):
        with open(messages_file, 'r') as f:
            return json.load(f)
    return []

# Function to save messages to the file
def save_messages(messages):
    with open(messages_file, 'w') as f:
        json.dump(messages, f, indent=4)

# Load existing messages when the server starts
messages = load_messages()

# Route to serve the chat page
@app.route('/')
def chat():
    return render_template('chat.html')

# Route to handle sending a message
@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    if 'username' in data and 'message' in data:
        # Assign a unique ID to each message based on the length of the messages list
        new_message = {
            'id': len(messages),  # Ensure every message has a unique ID
            'username': data['username'],
            'profilePic': data.get('profilePic', ''),
            'message': data['message'],
            'image': data.get('image', '')  # Optional image URL
        }
        messages.append(new_message)
        save_messages(messages)  # Save updated messages to the file
        return jsonify({'status': 'success', 'message': new_message}), 200
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

# Route to retrieve messages
@app.route('/get-messages', methods=['GET'])
def get_messages():
    last_id = request.args.get('last_id', None)
    try:
        if last_id is not None:
            # Convert last_id to an integer
            last_id = int(last_id)
            # Filter messages to return only those with an ID greater than last_id
            new_messages = [msg for msg in messages if 'id' in msg and msg['id'] > last_id]
            return jsonify(new_messages)
    except ValueError:
        # If last_id is invalid, return all messages
        pass
    # Return all messages if no valid last_id is provided
    return jsonify(messages)

# Route to handle image uploads
@app.route('/upload-image', methods=['POST'])
def upload_image():
    image_data = request.json.get('image')
    if image_data:
        try:
            # Check if the image data is base64 encoded
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            # Decode the base64 image
            image_bytes = base64.b64decode(image_data)
            # Generate a unique filename
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.abspath(os.path.join(image_upload_dir, filename))
            # Save the image to the upload directory
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            # Return the URL of the uploaded image
            return jsonify({'url': f'/static/uploads/{filename}'}), 200
        except (ValueError, IndexError, OSError) as e:
            print(f"Error saving image: {e}")  # Log the error for debugging
            return jsonify({'status': 'error', 'message': 'Invalid image data'}), 400
    return jsonify({'status': 'error', 'message': 'No image data provided'}), 400

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)