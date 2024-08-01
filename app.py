import os
import atexit
from flask import Flask, render_template, request, jsonify
from imap_tools import MailBox, AND, OR, NOT
from tts import TTS
from summarizer import Summarizer
from main import ACCOUNTS, OPENAI_API_KEY

app = Flask(__name__)
tts = TTS()
summarizer = Summarizer(OPENAI_API_KEY)


class EmailAssistant:
    def __init__(self):
        self.ensure_directories()

    @staticmethod
    def ensure_directories():
        os.makedirs('emails', exist_ok=True)
        os.makedirs('static', exist_ok=True)

    def fetch_emails(self):
        emails = {'unseen': [], 'pinned': [], 'flagged': []}
        email_counter = 1
        for account in ACCOUNTS:
            with MailBox(account["imap_server"], port=account["imap_port"]).login(account["username"],
                                                                                  account["password"]) as mailbox:
                mailbox.folder.set('INBOX')
                unseen_emails = list(mailbox.fetch(AND(seen=False)))
                pinned_emails = list(mailbox.fetch(AND(flagged=True, keyword='$PIN')))
                flagged_emails = list(mailbox.fetch(AND(flagged=True)))

                for email_list, category in [(unseen_emails, 'unseen'), (pinned_emails, 'pinned'),
                                             (flagged_emails, 'flagged')]:
                    email_list.sort(key=lambda x: x.date, reverse=True)
                    for email in email_list:
                        filename = f"{email_counter}_{account['username']}_{category}.txt"
                        full_path = os.path.join('emails', filename)
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(f"Subject: {email.subject}\n")
                            f.write(f"From: {email.from_}\n")
                            f.write(f"To: {', '.join(email.to)}\n")
                            f.write(f"Date: {email.date}\n")
                            f.write("\nBody:\n")
                            f.write(email.text)
                        emails[category].append({
                            'id': email_counter,
                            'account': account['username'],
                            'from': email.from_,
                            'subject': email.subject,
                            'filename': filename
                        })
                        email_counter += 1
        return emails

    def clear_emails(self):
        for filename in os.listdir('emails'):
            if filename.endswith('.txt'):
                os.remove(os.path.join('emails', filename))
        for filename in os.listdir('static'):
            if filename.endswith('.mp3'):
                os.remove(os.path.join('static', filename))

    def read_email(self, filename):
        full_path = os.path.join('emails', filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    def text_to_speech(self, filename):
        content = self.read_email(filename)
        audio_file = os.path.join('static', os.path.splitext(filename)[0] + '.mp3')
        tts.text_to_speech(content, audio_file)
        return os.path.basename(audio_file)

    def summarize_email(self, filename):
        content = self.read_email(filename)
        summary_filename = os.path.splitext(filename)[0] + '_summary.txt'
        output_path = os.path.join('emails', summary_filename)
        summarizer.summarize_text(content, output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            summary = f.read()
        return summary





email_assistant = EmailAssistant()

@app.route('/')
def index():
    emails = email_assistant.fetch_emails()
    return render_template('index.html', emails=emails)


@app.route('/read/<filename>')
def read_email(filename):
    content = email_assistant.read_email(filename)
    return jsonify({'content': content})


@app.route('/tts/<filename>')
def text_to_speech(filename):
    audio_file = email_assistant.text_to_speech(filename)
    return jsonify({'audio_file': audio_file})


@app.route('/summarize/<filename>')
def summarize_email(filename):
    summary = email_assistant.summarize_email(filename)
    return jsonify({'summary': summary})
@app.route('/refresh')
def refresh_emails():
    emails = email_assistant.fetch_emails()
    return jsonify({'emails': emails or []})


# Cleanup function
def cleanup():
    # Remove .txt files from 'emails' directory
    for filename in os.listdir('emails'):
        if filename.endswith('.txt'):
            os.remove(os.path.join('emails', filename))

    # Remove .mp3 files from 'static' directory
    for filename in os.listdir('static'):
        if filename.endswith('.mp3'):
            os.remove(os.path.join('static', filename))


@app.route('/toggle_flag', methods=['POST'])
def toggle_flag():
    filename = request.form.get('filename')
    category = request.form.get('category')

    if not filename or not category:
        return jsonify({'success': False, 'error': 'Missing filename or category'})

    try:
        # Extract email details from filename
        email_id, account, _ = filename.split('_')

        # Find the corresponding account
        account_info = next((acc for acc in ACCOUNTS if acc['username'] == account), None)
        if not account_info:
            return jsonify({'success': False, 'error': 'Account not found'})

        with MailBox(account_info["imap_server"], port=account_info["imap_port"]).login(account_info["username"],
                                                                                        account_info[
                                                                                            "password"]) as mailbox:
            mailbox.folder.set('INBOX')

            # Find the email
            emails = list(mailbox.fetch(AND(subject=email_id)))
            if not emails:
                return jsonify({'success': False, 'error': 'Email not found'})

            email = emails[0]

            # Toggle flag/pin status
            current_flags = mailbox.flag(email.uid, None)  # Get current flags

            if category == 'pinned':
                if '\\Flagged' in current_flags and '$PIN' in current_flags:
                    mailbox.flag(email.uid, ('\\Flagged', '$PIN'), False)
                else:
                    mailbox.flag(email.uid, ('\\Flagged', '$PIN'), True)
            elif category == 'flagged':
                if '\\Flagged' in current_flags:
                    mailbox.flag(email.uid, ('\\Flagged',), False)
                else:
                    mailbox.flag(email.uid, ('\\Flagged',), True)
            else:  # unseen
                if '\\Flagged' not in current_flags and '$PIN' not in current_flags:
                    mailbox.flag(email.uid, ('\\Flagged', '$PIN'), True)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Register cleanup function with atexit
atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True)
