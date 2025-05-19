from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

def process_meeting_string(string_parse):
    correct_string = [i.strip() for i in string_parse.split("\n\n")]
    
    # Process title
    title = correct_string[0]
    
    # Process name
    name_line = correct_string[1]
    name = name_line.split(":")[1].strip() if ":" in name_line else name_line
    
    # Process members
    members = correct_string[2]
    get_json_open = members.index("{")
    get_json_close = members.index("}")
    members_json = members[get_json_open:get_json_close+1]
    members_data = json.loads(members_json)
    
    # Process guests
    try:
        guests = correct_string[3]
        get_json_open_guests = guests.index("{")
        guests_json = "["+guests[get_json_open_guests:]+"]"
        guests_data = json.loads(guests_json)
        guests_list = [i['email'] for i in guests_data]
    except:
        guests_list = []

    # Create formatted docstring message
    message = f"""
{'='*60}
{title.center(60)}
{'='*60}

📋 Meeting Details:
------------------
• Organizer: {name}

👤 Host Information:
-------------------
• Name: {members_data.get('user_name', 'Unknown')}
• Email: {members_data.get('user_email', 'Unknown')}
• User ID: {members_data.get('user', 'Unknown')}

👥 Guest Information:
--------------------
{chr(10).join([f'• Guest {i+1}: {email}' for i, email in enumerate(guests_list)]) if guests_list else '• No guests in this meeting'}

📊 Meeting Summary:
------------------
• Total Participants: {len(guests_list) + 1}
• Has Guests: {'Yes' if guests_list else 'No'}

{'='*60}
"""
    return message.strip()

@app.route('/process-meeting', methods=['POST'])
def process_meeting():
    try:
        data = request.get_json()
        if not data or 'meeting_string' not in data:
            return jsonify({
                'success': False,
                'error': 'No meeting string provided',
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }), 400
        
        meeting_string = data['meeting_string']
        result = process_meeting_string(meeting_string)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'data': {
                'message': result
            },
            'metadata': {
                'processing_time': datetime.now().isoformat(),
                'version': '1.0',
                'format': 'docstring'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'metadata': {
                'error_type': type(e).__name__,
                'version': '1.0'
            }
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
