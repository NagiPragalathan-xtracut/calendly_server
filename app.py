from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

def process_meeting_string(string_parse):
    print("string_parse :", string_parse)
    
    correct_string = [i.strip() for i in string_parse.split("\n\n")]

    if(len(correct_string) == 1):
        correct_string = [i.strip() for i in string_parse.split("\\n\\n")]

    print("[correct_string] : ", correct_string)

    # Process title
    title = correct_string[0]

    # Process name (organizer)
    name_line = correct_string[1]
    organizer = name_line.split(":")[1].strip() if ":" in name_line else name_line

    # Process members (host)
    members = correct_string[2]
    get_json_open = members.index("{")
    get_json_close = members.index("}")
    members_json = members[get_json_open:get_json_close + 1]
    members_data = json.loads(members_json)

    # Process guests
    try:
        guests = correct_string[3]
        get_json_open_guests = guests.index("{")
        guests_json = "[" + guests[get_json_open_guests:] + "]"
        guests_data = json.loads(guests_json)
        guests_list = [i['email'] for i in guests_data]
    except:
        guests_list = []

    total_guests = len(guests_list)
    total_participants = total_guests + 1  # host + guests
    created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create a formatted docstring message with richer info and better structure
    message = f"""
╔{"="*66}╗
{title.center(66)}
╚{"="*66}╝

⨳  Meeting Overview
─────────────────────
• Organizer    : {organizer}
• Host Name    : {members_data.get('user_name', 'Unknown')}
• Host Email   : {members_data.get('user_email', 'Unknown')}
• Host User ID : {members_data.get('user', 'Unknown')}

♧  Guests Attending
─────────────────────
{chr(10).join([f"• Guest {i+1}: {email}" for i, email in enumerate(guests_list)]) if guests_list else "• No guests attending"}

♕  Summary
─────────────
• Total Guests       : {total_guests}
• Total Participants : {total_participants}
• Guests Present     : {"Yes" if guests_list else "No"}
• Created Time       : {created_time}

{'='*70}
"""

    return message.strip()

@app.route('/process-meeting', methods=['GET', 'POST'])
def process_meeting():
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
        else:  # GET
            data = request.args.to_dict()

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


def process_qa_list(qa_list):
    """
    qa_list: a list of dicts with 'question' and 'answer' keys
    Returns a formatted string of all questions and answers.
    """
    lines = []
    for i, qa in enumerate(qa_list, start=1):
        question = qa.get('question', 'No question provided')
        answer = qa.get('answer', 'No answer provided')
        lines.append(f"Q{i}: {question}\nA{i}: {answer}\n")

    result = "\n".join(lines).strip()
    return result


@app.route('/process-qa', methods=['GET', 'POST'])
def process_qa():
    """
    Endpoint expects 'qa_list' either in JSON body or as a query parameter (stringified JSON).
    Example input:
    [{"answer":"sample response","question":"Please share anything that will help prepare for our meeting.","position":0}]
    """
    try:
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
        else:  # GET
            data = request.args.to_dict()

        if not data or 'qa_list' not in data:
            return jsonify({
                'success': False,
                'error': 'No QA list provided',
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }), 400

        # qa_list might be a JSON string, so parse it
        qa_list_str = data['qa_list']

        # If the data is already a list (POST JSON), handle that too
        if isinstance(qa_list_str, list):
            qa_list = qa_list_str
        else:
            qa_list = json.loads(qa_list_str)

        formatted_result = process_qa_list(qa_list)

        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'data': {
                'formatted_qa': formatted_result
            },
            'metadata': {
                'processing_time': datetime.now().isoformat(),
                'version': '1.0',
                'format': 'plain-text'
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
