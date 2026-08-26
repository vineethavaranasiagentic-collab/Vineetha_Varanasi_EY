"""Educational next-token prediction simulation using NumPy."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RANDOM_SEED = 42
DATASET_SIZES = (100, 1_000, 10_000)
EPOCHS = 10
EMBEDDING_DIM = 32
LEARNING_RATE = 0.05
VALIDATION_SPLIT = 0.20
BATCH_SIZE = 256
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"

TEMPLATES = (
    "the bank approved the business loan",
    "the customer deposited money into the account",
    "the company increased its revenue this year",
    "the relationship manager reviewed the client account",
    "the customer requested a new credit facility",
    "the company paid its outstanding balance",
    "the bank offered a working capital facility",
    "the client increased its account balance",
    "the manager reviewed the financial statement",
    "the company expanded its operations",
    "the lender assessed the credit risk",
    "the business improved its profitability",
)


def generate_dataset(size: int, seed: int = RANDOM_SEED) -> list[str]:
    rng = np.random.default_rng(seed + size)
    return [TEMPLATES[int(rng.integers(0, len(TEMPLATES)))] for _ in range(size)]


def tokenize(sentence: str) -> list[str]:
    return ["<START>", *sentence.lower().split(), "<END>"]


def build_vocabulary(sentences: Iterable[str]) -> tuple[dict[str, int], dict[int, str]]:
    tokens = {"<START>", "<END>", "<UNK>"}
    for sentence in sentences:
        tokens.update(tokenize(sentence))
    ordered = ["<START>", "<END>", "<UNK>"] + sorted(tokens - {"<START>", "<END>", "<UNK>"})
    token_to_id = {token: index for index, token in enumerate(ordered)}
    return token_to_id, {index: token for token, index in token_to_id.items()}


def create_examples(sentences: Iterable[str], vocabulary: dict[str, int]) -> tuple[np.ndarray, np.ndarray]:
    inputs: list[int] = []
    targets: list[int] = []
    unknown = vocabulary["<UNK>"]
    for sentence in sentences:
        ids = [vocabulary.get(token, unknown) for token in tokenize(sentence)]
        inputs.extend(ids[:-1])
        targets.extend(ids[1:])
    return np.asarray(inputs, dtype=np.int64), np.asarray(targets, dtype=np.int64)


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    probabilities = np.exp(shifted)
    return probabilities / probabilities.sum(axis=-1, keepdims=True)


@dataclass
class EmbeddingPredictor:
    vocabulary_size: int
    embedding_dim: int
    learning_rate: float = LEARNING_RATE
    seed: int = RANDOM_SEED

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        scale = 0.08
        self.embeddings = rng.normal(0, scale, (self.vocabulary_size, self.embedding_dim))
        self.weights = rng.normal(0, scale, (self.embedding_dim, self.vocabulary_size))
        self.bias = np.zeros(self.vocabulary_size)

    def probabilities(self, inputs: np.ndarray) -> np.ndarray:
        return softmax(self.embeddings[inputs] @ self.weights + self.bias)

    def train(self, inputs: np.ndarray, targets: np.ndarray, epochs: int) -> list[dict[str, float]]:
        history: list[dict[str, float]] = []
        rng = np.random.default_rng(self.seed + 100)
        for epoch in range(1, epochs + 1):
            order = rng.permutation(len(inputs))
            for start in range(0, len(order), BATCH_SIZE):
                batch = order[start : start + BATCH_SIZE]
                x, y = inputs[batch], targets[batch]
                hidden = self.embeddings[x]
                probabilities = self.probabilities(x)
                probabilities[np.arange(len(y)), y] -= 1
                probabilities /= len(y)
                grad_weights = hidden.T @ probabilities
                grad_bias = probabilities.sum(axis=0)
                grad_hidden = probabilities @ self.weights.T
                grad_embeddings = np.zeros_like(self.embeddings)
                np.add.at(grad_embeddings, x, grad_hidden)
                self.weights -= self.learning_rate * grad_weights
                self.bias -= self.learning_rate * grad_bias
                self.embeddings -= self.learning_rate * grad_embeddings
            history.append({"epoch": epoch, **self.evaluate(inputs, targets)})
        return history

    def evaluate(self, inputs: np.ndarray, targets: np.ndarray) -> dict[str, float]:
        probabilities = self.probabilities(inputs)
        correct = probabilities[np.arange(len(targets)), targets]
        return {
            "loss": float(-np.log(np.clip(correct, 1e-12, 1)).mean()),
            "accuracy": float((np.argmax(probabilities, axis=1) == targets).mean() * 100),
        }

    def predict_next_token(self, token: str, vocabulary: dict[str, int], reverse: dict[int, str], top_k: int = 5) -> list[tuple[str, float]]:
        token_id = vocabulary.get(token.lower(), vocabulary["<UNK>"])
        probabilities = self.probabilities(np.asarray([token_id]))[0]
        indices = np.argsort(probabilities)[::-1][:top_k]
        return [(reverse[int(index)], float(probabilities[index] * 100)) for index in indices]


def run_experiment(size: int, embedding_dim: int = EMBEDDING_DIM) -> tuple[pd.DataFrame, EmbeddingPredictor, dict[str, int], dict[int, str]]:
    sentences = generate_dataset(size)
    split = max(1, int(size * (1 - VALIDATION_SPLIT)))
    train_sentences, validation_sentences = sentences[:split], sentences[split:]
    vocabulary, reverse = build_vocabulary(sentences)
    train_inputs, train_targets = create_examples(train_sentences, vocabulary)
    validation_inputs, validation_targets = create_examples(validation_sentences, vocabulary)
    model = EmbeddingPredictor(len(vocabulary), embedding_dim, seed=RANDOM_SEED + size + embedding_dim)
    rows: list[dict[str, float | int | str]] = []
    for item in model.train(train_inputs, train_targets, EPOCHS):
        validation = model.evaluate(validation_inputs, validation_targets)
        rows.append({"epoch": item["epoch"], "dataset_size": size, "model_size": embedding_dim, "train_loss": item["loss"], "validation_loss": validation["loss"], "train_accuracy": item["accuracy"], "validation_accuracy": validation["accuracy"]})
    return pd.DataFrame(rows), model, vocabulary, reverse


def plot_results(results: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(exist_ok=True)
    for metric, title, filename in (("train_loss", "Loss Reduction as Training Data Scales", "loss_vs_epoch.png"), ("train_accuracy", "Top-1 Accuracy as Training Data Scales", "accuracy_vs_epoch.png")):
        figure, axis = plt.subplots(figsize=(9, 5))
        for size, group in results.groupby("dataset_size"):
            axis.plot(group["epoch"], group[metric], marker="o", label=f"{size:,} sentences")
        axis.set(xlabel="Epoch", ylabel=metric.replace("_", " ").title(), title=title)
        axis.legend(); axis.grid(alpha=0.3); figure.tight_layout(); figure.savefig(output_dir / filename); plt.close(figure)
    small = results[results.dataset_size == min(DATASET_SIZES)]
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(small.epoch, small.train_loss, label="Training Loss"); axis.plot(small.epoch, small.validation_loss, label="Validation Loss")
    axis.set(xlabel="Epoch", ylabel="Cross-Entropy Loss", title="Training vs Validation Loss"); axis.legend(); axis.grid(alpha=0.3); figure.tight_layout(); figure.savefig(output_dir / "overfitting.png"); plt.close(figure)


def main() -> None:
    np.random.seed(RANDOM_SEED)
    print("=" * 60 + "\nNEXT-TOKEN PREDICTION TRAINING SIMULATION\n" + "=" * 60)
    all_results: list[pd.DataFrame] = []
    sample_model = None
    sample_vocabulary = sample_reverse = None
    for size in DATASET_SIZES:
        result, model, vocabulary, reverse = run_experiment(size)
        all_results.append(result)
        sample_model, sample_vocabulary, sample_reverse = model, vocabulary, reverse
        print(f"\nDataset Size: {size:,}\n", result.to_string(index=False, formatters={"train_loss": "{:.4f}".format, "validation_loss": "{:.4f}".format, "train_accuracy": "{:.2f}".format, "validation_accuracy": "{:.2f}".format}))
    results = pd.concat(all_results, ignore_index=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    results.to_csv(OUTPUT_DIR / "training_results.csv", index=False)
    results.assign(average_loss=results.train_loss, top_1_accuracy=results.train_accuracy)[["epoch", "dataset_size", "average_loss", "top_1_accuracy"]].to_csv(OUTPUT_DIR / "summary_results.csv", index=False)
    plot_results(results, OUTPUT_DIR)
    print("\nDATA SCALING SUMMARY\n", results.groupby("dataset_size").tail(1)[["dataset_size", "train_loss", "validation_loss", "validation_accuracy"]].to_string(index=False))
    print("\nSAMPLE NEXT-TOKEN PREDICTIONS")
    for token in ("the", "company", "customer", "bank"):
        predictions = sample_model.predict_next_token(token, sample_vocabulary, sample_reverse)
        print(token, ":", ", ".join(f"{word} ({prob:.2f}%)" for word, prob in predictions))
    print(f"\nGraphs and tables saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
