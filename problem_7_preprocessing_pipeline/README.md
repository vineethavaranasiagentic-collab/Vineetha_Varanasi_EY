# Banking Text Preprocessing Pipeline

This program demonstrates reusable preprocessing for three messy Commercial Banking Relationship Manager Copilot texts.

## What it does

- Converts text to lowercase.
- Replaces URLs with `URL_PRESENT`.
- Replaces email addresses with `EMAIL_PRESENT`.
- Removes punctuation and extra whitespace.
- Tokenizes text with spaCy.
- Optionally removes stop words.
- Optionally lemmatizes words.
- Prints token-count metrics for three pipeline configurations.

The actual URLs and email addresses are not retained in the processed output.

## Run in PowerShell

From the project root:

```powershell
cd "c:\Users\user\Documents\AiTraining\Task1\Vineetha_Varanasi_EY\preprocessing_pipeline"
& "c:\Users\user\Documents\AiTraining\Task1\.venv\Scripts\python.exe" preprocessing_pipeline.py
```

The script automatically installs spaCy and downloads `en_core_web_sm` if they are missing. Internet access is required the first time for setup.
