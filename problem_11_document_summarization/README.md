# Customer Email AI — Document Input

This terminal application reads one customer-email document, extracts its text in memory, sends it to OpenRouter, and displays a validated summary and/or reply draft. It never sends email and does not modify the input document.

## Supported files

- `.txt` using Python's built-in text reader
- `.docx` using `python-docx`
- PDF support can be added later in `document_reader.py` with a PDF library.

## Setup in Windows PowerShell

From this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Set `OPENROUTER_API_KEY` to your own key in `.env`. The model is configured in `openrouter_client.py`; replace `openai/gpt-5.6-luna` only if your OpenRouter account uses another exact model slug.

## Run

```powershell
python main.py
```

When prompted, enter a path such as `customer_email.txt` or an absolute `.docx` path. Choose `1`, `2`, or `3`, then wait for the structured response.

## Privacy

The application reads the document only for the current run. It does not save the extracted text, create a database, modify the input, send email, or log customer data. `.env` is ignored by Git. The document is passed to the model as untrusted content so instructions inside it are not treated as application instructions.
