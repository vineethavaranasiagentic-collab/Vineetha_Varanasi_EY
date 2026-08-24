"""TF-IDF analysis for a Commercial Banking Relationship Manager Copilot."""

import math
import re
from collections import Counter

import pandas as pd


# Every dictionary below is one small banking document containing its name,
# subject area, and text. The rest of the file compares their vocabulary.
# Six realistic domain documents.
documents = [
    {
        "Document": "Client Financial Review",
        "Domain Topic": "Client financials and risk",
        "Text": (
            "The client financials show stable revenue, improving cash flow, "
            "and manageable leverage. The relationship manager should remain "
            "proactive and review liquidity risk continuously."
        ),
    },
    {
        "Document": "Account Behaviour Report",
        "Domain Topic": "Account behaviour monitoring",
        "Text": (
            "Account behaviour shows irregular overdraft usage and delayed "
            "receipts. The manager should increase communication, monitor "
            "cash movements, and record an early warning signal."
        ),
    },
    {
        "Document": "Covenant Monitoring Note",
        "Domain Topic": "Covenant compliance",
        "Text": (
            "The covenant monitoring review confirms covenant compliance, but "
            "debt service coverage is close to the required threshold. A "
            "proactive manager should request updated financials and drafting "
            "of a mitigation plan."
        ),
    },
    {
        "Document": "Market Risk Update",
        "Domain Topic": "Market and industry conditions",
        "Text": (
            "Market volatility is affecting the manufacturing industry. "
            "Interest rates and supply costs may reduce margins, while export "
            "opportunities require careful scenario analysis and risk review."
        ),
    },
    {
        "Document": "Product Usage Review",
        "Domain Topic": "Product usage and opportunities",
        "Text": (
            "Product usage remains limited across treasury and trade services. "
            "The relationship manager identified cross sell opportunities, "
            "improved retention potential, and a need for proactive product "
            "communication."
        ),
    },
    {
        "Document": "CRM Relationship Note",
        "Domain Topic": "Relationship and client communication",
        "Text": (
            "The relationship team recorded a positive client meeting and "
            "strong communication. Managers should follow up on financing "
            "opportunities, retention concerns, and the next account review."
        ),
    },
]


# Common stop words removed during preprocessing.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "in", "is", "it", "of", "on", "or", "should", "that", "the", "to",
    "was", "while", "with", "this", "their", "across", "may", "next",
}


def preprocess(text):
    """Keep lowercase meaningful words that can be compared mathematically."""
    text = text.lower()
    tokens = re.findall(r"[a-z]+", text)
    return [token for token in tokens if token not in STOP_WORDS]


# Preprocess every document.
tokenized_documents = [preprocess(item["Text"]) for item in documents]
document_names = [item["Document"] for item in documents]

# Count words and create one combined vocabulary for all documents.
term_counts = [Counter(tokens) for tokens in tokenized_documents]
vocabulary = sorted({term for counts in term_counts for term in counts})

# TF measures how frequently a word occurs inside one document.
tf_matrix = []
for counts, tokens in zip(term_counts, tokenized_documents):
    total_terms = len(tokens)
    tf_matrix.append({
        term: counts[term] / total_terms if total_terms else 0.0
        for term in vocabulary
    })

# DF counts documents containing a word; IDF rewards words that are uncommon.
number_of_documents = len(documents)
document_frequency = {
    term: sum(term in counts for counts in term_counts)
    for term in vocabulary
}
idf = {
    term: math.log(number_of_documents / document_frequency[term])
    for term in vocabulary
}

# Calculate TF-IDF for every term in every document.
tfidf_matrix = [
    {
        term: tf_matrix[index][term] * idf[term]
        for term in vocabulary
    }
    for index in range(number_of_documents)
]


def print_heading(title):
    print("\n" + "=" * 110)
    print(title)
    print("=" * 110)


# Table 1: Documents.
print_heading("TABLE 1: DOCUMENTS")
documents_table = pd.DataFrame(documents)
print(documents_table.to_string(index=False))

# Table 2: TF values.
print_heading("TABLE 2: TERM FREQUENCY (TF) VALUES")
tf_table = pd.DataFrame(tf_matrix, index=document_names).T
print(tf_table.to_string(float_format=lambda value: f"{value:.4f}"))

# Table 3: DF and IDF.
print_heading("TABLE 3: DOCUMENT FREQUENCY (DF) AND INVERSE DOCUMENT FREQUENCY (IDF)")
df_idf_table = pd.DataFrame([
    {
        "Term": term,
        "Document Frequency": document_frequency[term],
        "IDF": idf[term],
    }
    for term in vocabulary
])
print(df_idf_table.to_string(index=False, formatters={"IDF": "{:.4f}".format}))

# Table 4: complete TF-IDF matrix.
print_heading("TABLE 4: COMPLETE TF-IDF MATRIX")
tfidf_table = pd.DataFrame(tfidf_matrix, index=document_names).T
print(tfidf_table.to_string(float_format=lambda value: f"{value:.4f}"))

# Rank each term by its maximum TF-IDF score across all documents.
term_rankings = []
for term in vocabulary:
    scores = [row[term] for row in tfidf_matrix]
    best_index = max(range(number_of_documents), key=lambda index: scores[index])
    best_score = scores[best_index]
    best_tf = tf_matrix[best_index][term]
    best_df = document_frequency[term]

    if best_df == 1 and best_tf >= 0.10:
        explanation = (
            "High TF in one document and high IDF; highly distinctive to its "
            "banking topic."
        )
    elif best_df == 1:
        explanation = (
            "Appears in only one document, so its high IDF helps distinguish "
            "that client-management topic."
        )
    elif best_tf >= 0.10:
        explanation = (
            "Occurs relatively often in its most relevant document and helps "
            "describe that banking theme."
        )
    else:
        explanation = (
            "Has a useful combination of document frequency and local frequency "
            "for distinguishing banking content."
        )

    term_rankings.append({
        "Word": term,
        "Most Relevant Document": document_names[best_index],
        "TF-IDF Score": best_score,
        "Why Is It Special?": explanation,
    })

term_rankings.sort(key=lambda row: (-row["TF-IDF Score"], row["Word"]))
top_15 = term_rankings[:15]

print_heading("TOP 15 MOST SPECIAL WORDS")
top_table = pd.DataFrame(top_15)
top_table.insert(0, "Rank", range(1, len(top_table) + 1))
print(top_table.to_string(index=False, formatters={"TF-IDF Score": "{:.4f}".format}))

# Show the five highest-scoring words for each document.
print_heading("TOP 5 TF-IDF WORDS FOR EACH DOCUMENT")
for index, document_name in enumerate(document_names):
    top_words = sorted(
        tfidf_matrix[index].items(),
        key=lambda item: (-item[1], item[0]),
    )[:5]
    formatted = ", ".join(f"{word} ({score:.4f})" for word, score in top_words)
    print(f"{document_name}: {formatted}")

# Final interpretation and domain-specific conclusion.
print_heading("INTERPRETATION")
print("TF measures how frequently a term occurs within one document.")
print("DF measures how many documents contain the term.")
print("IDF is log(N / DF), so rare terms receive larger IDF values.")
print("TF-IDF is TF multiplied by IDF and combines local importance with rarity.")
print("Common terms receive lower scores because they appear across many documents.")
print(
    "In this corpus, terms such as covenant, retention, financials, market, "
    "and account help distinguish compliance, client loyalty, financial health, "
    "market conditions, and account-monitoring themes."
)
print(
    "For the Commercial Banking Relationship Manager Copilot, these scores can "
    "surface client risk themes, early warning signals, cross-sell opportunities, "
    "retention concerns, industry developments, and CRM notes requiring attention."
)

print_heading("CONCLUSION")
print(
    "The 15 most special words are: "
    + ", ".join(row["Word"] for row in top_15)
    + ". They are special because their calculated maximum TF-IDF scores show "
    "that they are frequent in a particular document, uncommon across the "
    "corpus, or both. Consequently, they help the Copilot identify the most "
    "distinctive banking topics for relationship-manager review."
)
