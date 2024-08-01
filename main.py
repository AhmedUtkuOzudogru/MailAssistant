from imap_tools import MailBox, AND
import os
from tts import TTS 
from summarizer import Summarizer
ACCOUNTS = [
    {
    "username": "YOUR_EMAIL_ADDRESS",
        "password": "YOUR_EMAIL_PASSWORD",
        "imap_server": "YOUR_IMAP_SERVER",
        "imap_port": 993
    },
    {
    "username": "YOUR_EMAIL_ADDRESS",
        "password": "YOUR_EMAIL_PASSWORD",
        "imap_server": "YOUR_IMAP_SERVER",
        "imap_port": 993
    },

    # Add more accounts as needed
]
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def create_txt(email, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Subject: {email.subject}\n")
        f.write(f"From: {email.from_}\n")
        f.write(f"To: {', '.join(email.to)}\n")
        f.write(f"Date: {email.date}\n")
        f.write("\nBody:\n")
        f.write(email.text)  

def fetch_and_save_emails():
    email_counter = 1
    for account in ACCOUNTS:
        with MailBox(account["imap_server"], port=account["imap_port"]).login(account["username"], account["password"]) as mailbox:
            mailbox.folder.set('INBOX')
            
            # Fetch unseen messages
            unseen_emails = list(mailbox.fetch(AND(seen=False)))
            
            # Sort emails by date, newest first
            unseen_emails.sort(key=lambda x: x.date, reverse=True)
            
            # Save emails as text files
            for email in unseen_emails:
                filename = os.path.join(os.getcwd(), f"{email_counter}_{account['username']}.txt")
                create_txt(email, filename)
                print(f"{email_counter}- Account: {account['username']}, From: {email.from_}, Subject: {email.subject}")
                email_counter += 1
        
        print(f"Retrieved and saved {len(unseen_emails)} unseen emails from {account['username']}.")

def main():
    fetch_and_save_emails()
    
    tts = TTS()
    summarizer = Summarizer(OPENAI_API_KEY)
    playing_file = None

    while True:
        command = input("Enter a command (list, read <number>, summarize <number>, stop, quit, refresh): ").lower().split()
        
        if command[0] == 'quit':
            break
        elif command[0] == 'list':
            if len(command) == 2:
                try:
                    email_number = int(command[1])
                    matching_files = [f for f in os.listdir() if f.startswith(f"{email_number}_") and f.endswith('.txt')]
                    if matching_files:
                        filename = matching_files[0]
                        with open(filename, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                        print(f"{filename}: {first_line}")
                    else:
                        print("Invalid email number.")
                except ValueError:
                    print("Invalid command. Please enter a number after 'list'.")
            else:
                print("Saved emails:")
                for filename in sorted(os.listdir(), key=lambda x: int(x.split('_')[0]) if x.endswith('.txt') else 0):
                    if filename.endswith('.txt'):
                        with open(filename, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                        print(f"{filename}: {first_line}")
        elif command[0] == 'read' and len(command) == 2:
            try:
                email_number = int(command[1])
                matching_files = [f for f in os.listdir() if f.startswith(f"{email_number}_") and f.endswith('.txt')]
                if matching_files:
                    filename = matching_files[0]
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()

                    print("Reading the email...")
                    print(content)  # Print the content to console
                    
                    audio_file = os.path.join(os.getcwd(), f"{email_number}.mp3")
                    tts.text_to_speech(content, audio_file)
                    tts.play_audio(audio_file)
                else:
                    print("Invalid email number.")
            except ValueError:
                print("Invalid command. Please enter a number after 'read'.")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif command[0] == 'summarize' and len(command) == 2:
            try:
                email_number = int(command[1])
                matching_files = [f for f in os.listdir() if f.startswith(f"{email_number}_") and f.endswith('.txt')]
                if matching_files:
                    input_filename = matching_files[0]
                    output_filename = os.path.join(os.getcwd(), f"{email_number}_summary.txt")
                    with open(input_filename, 'r', encoding='utf-8') as f:
                        content = f.read()

                    summarizer.summarize_text(content, output_filename)
                else:
                    print("Invalid email number.")
            except ValueError:
                print("Invalid command. Please enter a number after 'summarize'.")
            except Exception as e:
                print(f"An error occurred: {e}")
        elif command[0] == 'stop':
            tts.stop_audio()
            playing_file = None
            print("TTS playback stopped.")
        elif command[0] == 'refresh':
            tts.stop_audio()  # Ensure audio is stopped before cleanup
            for filename in os.listdir():
                if filename.endswith('.txt') or filename.endswith('.mp3'):
                    os.remove(filename)
            fetch_and_save_emails()
        else:
            print("Invalid command.")

    # Stop audio playback and delete all .txt and .mp3 files in the current directory when the program ends
    tts.stop_audio()  # Ensure audio is stopped before cleanup
    for filename in os.listdir('emails'):
        if filename.endswith('.txt'):
            os.remove(os.path.join('emails', filename))
    for filename in os.listdir('static'):
        if filename.endswith('.mp3'):
            os.remove(os.path.join('static', filename))
    print("All email and audio files have been deleted.")

if __name__ == "__main__":
    main()
