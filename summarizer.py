from openai import OpenAI


class Summarizer:
    def __init__(self, YourApi_key):
        self.client = OpenAI(api_key=YourApi_key)

    def summarize_text(self, text, output_file):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
                ],
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            summary = response['choices'][0]['message']['content'].strip()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary saved to {output_file}")
        except Exception as e:
            print(f"An error occurred while summarizing text: {e}")
