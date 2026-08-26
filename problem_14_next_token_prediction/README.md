# Problem 14 — Next-Token Prediction at Scale

This educational program trains a small NumPy embedding-based next-token predictor on synthetic business sentences.

## Install

```powershell
pip install -r requirements.txt
```

## Run

From the `problem_14_next_token_prediction` folder:

```powershell
python problem_14.py
```

The program runs experiments using 100, 1,000, and 10,000 sentences, calculates training/validation cross-entropy loss and top-1 accuracy, prints result tables, demonstrates predictions, and writes CSV/PNG outputs into `outputs/`.

The implementation uses actual gradient descent and does not use predefined metrics. It uses a fixed seed for reproducibility.
