

# Your Mail Assistant

This application allows you to fetch unread emails from an IMAP server, save them as text files, and use text-to-speech 
(TTS) to read the content of these emails aloud. It uses the `gtts` (Google Text-to-Speech) 
library for generating audio and `pygame` for playback(takes around 30+ secs until audio starts
to play for an average length mail ). Also uses openAi Api to summarize emails. I also added a web interface to the project using flask (_Not completed yet_). 
You can access the web interface by going to http://127.0.0.1:5000 or http://localhost:5000 after executing app.py in your IDE.
Using a venv is strongly recommended for the project. You can create a venv by running the following command in the project directory:
```bash  
python -m venv venv
```
Then you can activate the venv by running the following command:
```bash
venv\Scripts\activate
```

## Features

- **Fetch Unread Emails:** Retrieve unseen emails from an IMAP server and save them as text files.
- **List Emails:** Display a list of saved emails with their subject lines.
- **Read Emails:** Convert the text content of emails to speech and play the audio.
- **Summarize:** Summarizes emails using openAi Api.
- **Refresh:** Remove all saved text and audio files and fetch new emails.

## Prerequisites

- Python 3.x
- Libraries: `gtts`, `pygame`, `imap-tools`,`openai`,`flask`  

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/AhmedUtkuOzudogru/MailAssistant.git
   cd MailAssistant
   ```

2. **Install Dependencies**

   Make sure you have `pip` installed. Then install the required libraries using:

   ```bash
   pip install gtts pygame imap-tools openai flask
   ```
   or 
`pip install -r requirements.txt
`
## Configuration

1. **IMAP Server Details**

   Edit the `main.py` file and set the following variables with your IMAP server details:

   ```python
   MAIL_PASSWORD = "your_email_password"
   MAIL_USERNAME = "your_email_address"
   IMAP_SERVER = "your_imap_server"
   IMAP_PORT = 993
   ```

2. **Running the Application**

   You can run the application by executing:

   ```bash
   python app.py
   ```
   if you want to use terminal interface you can run the following command:
   ```bash
    python main.py
    ```
## Commands For Console

- `list`: List all saved email files with their subject lines.
- `list <number>`: Shows the email content of the specified email number.
- `read <number>`: Read and play the email content of the specified email number.
- `summarize <number>`: Summarizes the specified email.
- `stop`: Stop the current TTS playback.
- `refresh`: Remove all saved text and audio files and fetch new emails.
- `quit`: Exit the application.

## Usage Example For Console 

```plaintext
Enter a command (list, read <number>, stop, quit, refresh): list
```

```plaintext
Enter a command (list, read <number>, stop, quit, refresh): read 1
Reading the email...
```

```plaintext
Enter a command (list, read <number>, stop, quit, refresh): stop
TTS playback stopped.
```

```plaintext
Enter a command (list, read <number>, stop, quit, refresh): quit
```

## Troubleshooting

- **No Audio Playback:** Ensure that `pygame` and `gtts` are installed correctly. Check that the MP3 files are not corrupted.
- **File Deletion Issues:** If you encounter permission errors while deleting files, ensure that the files are not in use and that you have the appropriate permissions.
- **No ChatGPT Response:** Make sure you have enough quota on your account.

Feel free to adjust any details to better match your specific use case or project requirements!
