"""Word2Vec and KMeans clustering for Commercial Banking RM records.

Install once:
    python -m pip install pandas gensim scikit-learn matplotlib nltk

The script uses the CSV in this folder when it exists. If the CSV is missing,
it creates 240 realistic synthetic records so the example remains runnable.
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Reuse the exact Problem 7 preprocessing function instead of duplicating it.
PROBLEM_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROBLEM_ROOT / "problem_7_preprocessing_pipeline"))
from preprocessing_pipeline import download_nltk_resources, preprocess_text  # noqa: E402


RANDOM_SEED = 42
N_CLUSTERS = 5  # Change this value to experiment with a different number of clusters.
DATA_FILE = Path(__file__).with_name("banking_clustered_records.csv")
OUTPUT_FILE = Path(__file__).with_name("banking_semantic_clusters.png")


def create_synthetic_records():
    """Create 240 varied commercial-banking notes when no CSV is available."""
    topics = [
        ("loan", [
            "Client requested a term loan to expand its manufacturing facility.",
            "Borrower is reviewing a refinancing proposal after a change in leverage.",
            "The company needs a working capital line to fund seasonal inventory.",
            "Relationship manager discussed an overdraft renewal with the finance director.",
            "Customer asked for a credit limit increase to support new purchase orders.",
            "Cash flow pressure may affect the upcoming loan repayment schedule.",
        ]),
        ("trade", [
            "Exporter needs a letter of credit for an overseas buyer shipment.",
            "Importer requested trade finance for machinery purchased from Germany.",
            "The client is evaluating a bank guarantee for a government contract.",
            "Treasury meeting covered foreign exchange hedging and export proceeds.",
            "Trade operations reviewed shipping documents and documentary collections.",
            "Supplier finance could improve payment terms for the international supply chain.",
        ]),
        ("cash", [
            "Customer wants automated cash management for several operating accounts.",
            "The payroll team asked about bulk salary payments and account integration.",
            "Merchant services can support the client's growing card payment volume.",
            "Relationship manager reviewed liquidity balances and a sweeping solution.",
            "Online banking access and payment approval controls need to be configured.",
            "The business is considering receivables collection and payment reconciliation.",
        ]),
        ("risk", [
            "Credit review identified weaker debt service coverage and covenant pressure.",
            "Updated financial statements are required before the facility renewal.",
            "KYC refresh remains outstanding for two beneficial owners.",
            "Collateral valuation is overdue and should be completed before approval.",
            "Compliance team requested transaction details for an account activity review.",
            "Late loan payments and declining balances require enhanced monitoring.",
        ]),
        ("relationship", [
            "Client meeting identified cross-selling opportunities in deposits and insurance.",
            "Customer raised a service escalation and requested a recovery action plan.",
            "Relationship is healthy but product penetration remains limited.",
            "RM scheduled a quarterly review to discuss pricing and business priorities.",
            "Corporate deposits increased after the client discussed its investment plans.",
            "Implementation concerns may create retention risk despite stable performance.",
        ]),
    ]
    records = []
    record_number = 1
    for _, sentences in topics:
        for copy_number in range(48):
            sentence = sentences[copy_number % len(sentences)]
            suffix = (
                f" RM follow-up {copy_number + 1}: review next steps within "
                f"{(copy_number % 7) + 1} business days."
            )
            records.append({"record_id": f"CB-{record_number:03d}", "text": sentence + suffix})
            record_number += 1
    return pd.DataFrame(records)


def load_records():
    """Load a supplied CSV, or create a fallback dataset with 240 records."""
    if DATA_FILE.exists():
        data = pd.read_csv(DATA_FILE)
        required = {"record_id", "text"}
        if not required.issubset(data.columns):
            raise ValueError(f"{DATA_FILE.name} must contain columns: {required}")
        print(f"Loaded input file: {DATA_FILE.name}")
        return data[["record_id", "text"]].dropna().reset_index(drop=True)

    print(f"{DATA_FILE.name} was not found; creating a synthetic dataset.")
    return create_synthetic_records()


def document_vectors(tokenized_records, model):
    """Average the Word2Vec vectors for each record."""
    vectors = []
    for tokens in tokenized_records:
        known_vectors = [model.wv[token] for token in tokens if token in model.wv]
        if known_vectors:
            vectors.append(np.mean(known_vectors, axis=0))
        else:
            vectors.append(np.zeros(model.vector_size))
    return np.asarray(vectors)


def representative_terms(data, cluster_id, model, limit=8):
    """Find frequent content terms and Word2Vec terms near a cluster centroid."""
    cluster_rows = data[data["cluster"] == cluster_id]
    words = " ".join(cluster_rows["processed_text"]).split()
    counts = pd.Series(words).value_counts()
    frequent = list(counts.head(limit).index)
    return frequent


def cluster_name(terms):
    """Suggest a name from terms discovered after clustering, not labels in advance."""
    theme_terms = {
        "Lending & Working Capital": {"loan", "borrower", "working", "capital", "overdraft", "credit"},
        "Trade Finance": {"exporter", "importer", "trade", "letter", "credit", "guarantee", "foreign"},
        "Cash Management & Payments": {"cash", "payment", "payroll", "merchant", "account", "liquidity"},
        "Credit Risk & Compliance": {"risk", "credit", "review", "kyc", "compliance", "collateral", "financial"},
        "Relationship & Cross-Sell": {"client", "customer", "relationship", "crossselling", "service", "meeting"},
    }
    scores = {name: len(set(terms) & keywords) for name, keywords in theme_terms.items()}
    return max(scores, key=scores.get) if max(scores.values()) else "Mixed Banking Activity"


def main():
    download_nltk_resources()
    np.random.seed(RANDOM_SEED)
    data = load_records()
    print(f"\nNumber of records loaded: {len(data)}")
    print("\nDataFrame preview:")
    print(data.head().to_string(index=False))

    # Problem 7's best configuration was stopword removal + lemmatization.
    data["processed_text"] = data["text"].map(
        lambda value: preprocess_text(value, remove_stopwords=True, lemmatize=True)
    )
    data["tokens"] = data["processed_text"].str.split()
    print("\nPreprocessed examples:")
    print(data[["text", "processed_text"]].head(3).to_string(index=False))

    # Word2Vec learns local embeddings from these records; no pretrained model is used.
    model = Word2Vec(
        sentences=data["tokens"].tolist(),
        vector_size=100,  # Number of dimensions in each word vector.
        window=5,         # Maximum distance between words considered together.
        min_count=1,      # Keep every word in this small teaching dataset.
        workers=4,
        epochs=100,
        seed=RANDOM_SEED,
    )
    print(f"\nWord2Vec trained locally: {len(model.wv)} words, {model.vector_size} dimensions")

    embeddings = document_vectors(data["tokens"], model)
    print(f"Document embedding shape: {embeddings.shape}")

    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
    data["cluster"] = kmeans.fit_predict(embeddings)
    print("\nCluster distribution:")
    print(data["cluster"].value_counts().sort_index().to_string())

    # KMeans only assigns numbers. Meaning is inferred by inspecting terms and examples.
    summaries = []
    print("\nCLUSTER DETAILS")
    for cluster_id in range(N_CLUSTERS):
        rows = data[data["cluster"] == cluster_id]
        terms = representative_terms(data, cluster_id, model)
        name = cluster_name(terms)
        summaries.append((cluster_id, name, len(rows), terms))
        print(f"\nCluster {cluster_id}: {name} ({len(rows)} records)")
        print(f"Representative terms: {', '.join(terms)}")
        for example in rows["text"].head(3):
            print(f"- {example}")

    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    points = pca.fit_transform(embeddings)
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(points[:, 0], points[:, 1], c=data["cluster"], cmap="tab10", alpha=0.72)
    for cluster_id, name, _, _ in summaries:
        center = points[data["cluster"] == cluster_id].mean(axis=0)
        plt.annotate(f"C{cluster_id}: {name}", center, fontsize=9, fontweight="bold")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("Commercial Banking Relationship Records – KMeans Clusters")
    plt.colorbar(scatter, label="KMeans cluster")
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150)
    print(f"\nPCA visualization saved to: {OUTPUT_FILE.name}")
    plt.show()

    print("\nCLUSTER SUMMARY")
    for cluster_id, name, count, terms in summaries:
        print(f"Cluster {cluster_id}: {name}")
        print(f"Number of records: {count}")
        print(f"Main themes: {', '.join(terms[:5])}\n")


if __name__ == "__main__":
    main()
