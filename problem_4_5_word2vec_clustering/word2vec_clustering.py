"""Word2Vec similarity and KMeans clustering for a banking RM Copilot."""

import importlib
import subprocess
import sys


def ensure_package(package_name, import_name=None):
    # Install a missing library automatically for easier first-time execution.
    import_name = import_name or package_name
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


# Install required packages automatically when needed.
ensure_package("gensim")
ensure_package("scikit-learn", "sklearn")
ensure_package("pandas")
ensure_package("matplotlib")

import matplotlib.pyplot as plt
import pandas as pd
import re
from pathlib import Path
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


CORPUS = """
Build an agentic assistant for relationship managers that continuously scans client financials, account behavior, product usage, covenant status, market news, and CRM notes to identify next-best-actions. The agent should prepare client meeting briefs, suggest cross-sell or retention opportunities, draft outreach emails, and flag early warning signals such as declining balances, covenant stress, delayed payments, or industry risk movement. The assistant should monitor client financials, account behavior, product usage, covenant status, market conditions, CRM notes, customer relationships, retention opportunities, financial risk, account balances, payment behavior, industry trends, and product opportunities. The relationship manager should receive proactive communication, client meeting recommendations, cross-sell opportunities, retention actions, covenant alerts, payment alerts, market risk alerts, and industry risk updates. The system should support explainable next-best-action recommendations while maintaining compliance-aware communication and human approval before client communication is sent.
"""

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "before", "by", "for",
    "from", "in", "is", "it", "of", "on", "or", "such", "that", "the",
    "their", "this", "to", "was", "while", "with", "should", "very",
}


def preprocess(text):
    """Convert the corpus into clean words that the model can learn from."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


# Break the cleaned corpus into short sentences so nearby word context is learned.
tokens = preprocess(CORPUS)
sentences = [tokens[i:i + 12] for i in range(0, len(tokens), 12)]

model = Word2Vec(
    sentences=sentences,
    vector_size=100,
    window=5,
    min_count=1,
    workers=1,
    epochs=100,
    seed=42,
)
# Word2Vec has now assigned a numeric vector to every learned vocabulary word.

key_words = ["relationship", "financials", "covenant", "market", "retention"]

similarity_rows = []
for key_word in key_words:
    for similar_word, score in model.wv.most_similar(key_word, topn=3):
        similarity_rows.append({
            "Key Word": key_word,
            "Similar Word": similar_word,
            "Similarity Score": score,
        })

print("=" * 100)
print("WORD2VEC SIMILARITY RESULTS")
print("=" * 100)
print(pd.DataFrame(similarity_rows).to_string(
    index=False,
    formatters={"Similarity Score": "{:.4f}".format},
))


# Group the learned vectors into three clusters using KMeans.
words = list(model.wv.index_to_key)
vectors = model.wv.vectors
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
cluster_ids = kmeans.fit_predict(vectors)

cluster_data = pd.DataFrame({"Word": words, "Cluster": cluster_ids})
cluster_sizes = cluster_data["Cluster"].value_counts().to_dict()

# Interpret clusters from their highest-frequency/representative words without
# assigning words to clusters manually. The labels are generated from keywords
# found in each calculated cluster.
theme_keywords = {
    "Client Relationship & Retention": {"relationship", "retention", "customer", "communication", "crm"},
    "Financial Risk & Covenant Monitoring": {"financials", "risk", "covenant", "payments", "balances", "stress"},
    "Market, Product & Opportunities": {"market", "product", "opportunities", "industry", "cross", "usage"},
}

def cluster_meaning(cluster_words):
    scores = {
        theme: len(set(cluster_words) & keywords)
        for theme, keywords in theme_keywords.items()
    }
    best_theme = max(scores, key=scores.get)
    return best_theme if scores[best_theme] else "General Banking Operations"

cluster_meanings = {
    cluster: cluster_meaning(cluster_data.loc[cluster_data["Cluster"] == cluster, "Word"].tolist())
    for cluster in sorted(cluster_data["Cluster"].unique())
}
cluster_data["Cluster Meaning"] = cluster_data["Cluster"].map(cluster_meanings)
cluster_data = cluster_data.sort_values(["Cluster", "Word"]).reset_index(drop=True)

print("\n" + "=" * 100)
print("ALL WORD CLUSTERS")
print("=" * 100)
print(cluster_data.to_string(index=False))

for cluster in sorted(cluster_data["Cluster"].unique()):
    print("\n" + "=" * 100)
    print(f"CLUSTER {cluster}: {cluster_meanings[cluster]}")
    print("=" * 100)
    print(cluster_data[cluster_data["Cluster"] == cluster].to_string(index=False))


# PCA compresses high-dimensional word vectors into two plot coordinates.
pca = PCA(n_components=2, random_state=42)
coordinates = pca.fit_transform(vectors)
plot_data = pd.DataFrame({
    "Word": words,
    "Cluster": cluster_ids,
    "PCA Component 1": coordinates[:, 0],
    "PCA Component 2": coordinates[:, 1],
})

plt.figure(figsize=(14, 10))
colors = ["tab:blue", "tab:orange", "tab:green"]
for cluster in sorted(plot_data["Cluster"].unique()):
    subset = plot_data[plot_data["Cluster"] == cluster]
    plt.scatter(
        subset["PCA Component 1"],
        subset["PCA Component 2"],
        color=colors[cluster],
        label=f"Cluster {cluster}: {cluster_meanings[cluster]}",
        s=55,
        alpha=0.8,
    )
    for _, row in subset.iterrows():
        plt.annotate(row["Word"], (row["PCA Component 1"], row["PCA Component 2"]), fontsize=8, alpha=0.85)

plt.title("Word2Vec Word Clusters: Commercial Banking Relationship Manager Copilot")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()
figure_path = Path(__file__).with_name("word2vec_kmeans_pca.png")
plt.savefig(figure_path, dpi=300, bbox_inches="tight")
print(f"\nPCA figure saved to: {figure_path}")
plt.show()


print("\n" + "=" * 100)
print("FINAL INTERPRETATION")
print("=" * 100)
print(
    "Word2Vec learns similarity from words appearing in nearby contexts. "
    "The most similar words should be interpreted cautiously because this is "
    "a very small corpus, not a large banking-language dataset."
)
print(
    "KMeans groups words by the geometry of their learned embeddings. The "
    "clusters can help organize relationship issues, financial and behavioural "
    "signals, risk terminology, product opportunities, retention themes, CRM "
    "notes, and market information."
)
print(
    "PCA provides a two-dimensional approximation of the embedding space. "
    "Clusters may not be perfectly separated because PCA compresses 100 "
    "dimensions into two and the training corpus is small."
)
print(
    "In a production Relationship Manager Copilot, these techniques could "
    "support next-best-action recommendations, risk monitoring, cross-sell "
    "discovery, retention analysis, and prioritization of CRM notes."
)
