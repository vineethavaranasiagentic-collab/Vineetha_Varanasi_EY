# Customer Email AI Assistant

A generic, interactive terminal application for summarizing customer emails and drafting replies with the OpenRouter Chat Completions API.

## Privacy

Customer request, email ID, subject, body, and model output exist only in memory while the program runs. The application does not create a database, cache, history, temporary file, or email sender. It does not log customer data or API keys. The email ID is displayed for identification only and is not persisted.

Customer text is explicitly marked as untrusted data. Instructions inside the email cannot override the application system prompt. The generated response is a draft for review; the program never sends email.

## Setup in PowerShell

From this directory:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your own values:

```text
OPENROUTER_API_KEY=your_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Never commit `.env` or share the API key.

## Run

```powershell
python main.py
```

The application asks for the requested task, email ID, optional subject, and email body. Finish the body by typing `END` on its own line.

## Example

```text
What do you need?
> Summarize the email and draft a reply.

Customer Email ID:
> customer123@example.com

Customer Email Subject (optional):
> Request for information

Paste the customer email below.
Type END on a new line when finished:
> Please send information about your services.
> END
```
