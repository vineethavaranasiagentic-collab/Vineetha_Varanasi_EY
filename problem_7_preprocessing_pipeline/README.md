# Banking Text Preprocessing Pipeline

This program demonstrates reusable preprocessing for three messy, user-provided texts.

## What it does

- Converts text to lowercase.
- Removes URLs and email addresses.
- Removes punctuation and extra whitespace.
- Tokenizes text with NLTK.
- Optionally removes stop words.
- Optionally lemmatizes words.
- Compares all four stopword/lemmatization configurations.

The actual URLs and email addresses are not retained in the processed output.

## Run in PowerShell

From the repository root:

```powershell
cd "c:\Users\user\Documents\AgenticAITraining\Vineetha_Varanasi_EY"
python .\problem_7_preprocessing_pipeline\preprocessing_pipeline.py
```

Install NLTK once if needed:

```powershell
python -m pip install nltk
```

The script automatically downloads the NLTK tokenizer, stopword, WordNet, and part-of-speech tagger resources the first time it runs. Internet access is required for that first run.
