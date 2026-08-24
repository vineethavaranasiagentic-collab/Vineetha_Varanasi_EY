"""Self-contained demonstration of English stemming and lemmatization."""

from dataclasses import dataclass


class PorterStemmer:
    """Implementation of the original Porter stemming algorithm."""

    # The methods in this class apply mechanical English word-reduction rules.
    # A stem is not required to be a complete English dictionary word.

    @staticmethod
    def consonant(word, i):
        if word[i] in "aeiou":
            return False
        if word[i] == "y":
            return i == 0 or not PorterStemmer.consonant(word, i - 1)
        return True

    @staticmethod
    def measure(word):
        count = 0
        previous_consonant = True
        for i in range(len(word)):
            is_consonant = PorterStemmer.consonant(word, i)
            if is_consonant:
                previous_consonant = True
            elif previous_consonant:
                count += 1
                previous_consonant = False
        return count

    @staticmethod
    def contains_vowel(word):
        return any(not PorterStemmer.consonant(word, i) for i in range(len(word)))

    @staticmethod
    def double_consonant(word):
        return (len(word) >= 2 and word[-1] == word[-2]
                and PorterStemmer.consonant(word, len(word) - 1))

    @staticmethod
    def cvc(word):
        if len(word) < 3:
            return False
        return (PorterStemmer.consonant(word, -3)
                and not PorterStemmer.consonant(word, -2)
                and PorterStemmer.consonant(word, -1)
                and word[-1] not in "wxy")

    def apply_rules(self, word, rules, minimum_measure=0):
        for suffix, replacement in rules:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                return (stem + replacement
                        if self.measure(stem) > minimum_measure else word)
        return word

    def finish_step_1b(self, word):
        if word.endswith(("at", "bl", "iz")):
            return word + "e"
        if self.double_consonant(word) and word[-1] in "bdgmnprt":
            return word[:-1]
        if self.measure(word) == 1 and self.cvc(word):
            return word + "e"
        return word

    def stem(self, word):
        word = word.lower()

        # Step 1a: plurals.
        if word.endswith("sses"):
            word = word[:-2]
        elif word.endswith("ies"):
            word = word[:-2]
        elif not word.endswith("ss") and word.endswith("s"):
            word = word[:-1]

        # Step 1b: past tense and -ing forms.
        if word.endswith("eed"):
            stem = word[:-3]
            if self.measure(stem) > 0:
                word = stem + "ee"
        elif word.endswith("ed") and self.contains_vowel(word[:-2]):
            word = self.finish_step_1b(word[:-2])
        elif word.endswith("ing") and self.contains_vowel(word[:-3]):
            word = self.finish_step_1b(word[:-3])

        # Step 1c.
        if word.endswith("y") and self.contains_vowel(word[:-1]):
            word = word[:-1] + "i"

        # Steps 2 and 3.
        word = self.apply_rules(word, [
            ("ational", "ate"), ("tional", "tion"), ("enci", "ence"),
            ("anci", "ance"), ("izer", "ize"), ("bli", "ble"),
            ("alli", "al"), ("entli", "ent"), ("eli", "e"),
            ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"),
            ("ator", "ate"), ("alism", "al"), ("iveness", "ive"),
            ("fulness", "ful"), ("ousness", "ous"), ("aliti", "al"),
            ("iviti", "ive"), ("biliti", "ble"), ("logi", "log")])
        word = self.apply_rules(word, [
            ("icate", "ic"), ("ative", ""), ("alize", "al"),
            ("iciti", "ic"), ("ical", "ic"), ("ful", ""),
            ("ness", "")])

        # Step 4.
        for suffix, replacement in [
            ("ement", ""), ("ance", ""), ("ence", ""), ("able", ""),
            ("ible", ""), ("ment", ""), ("ant", ""), ("ent", ""),
            ("al", ""), ("er", ""), ("ic", ""), ("ion", ""),
            ("ou", ""), ("ism", ""), ("ate", ""), ("iti", ""),
            ("ous", ""), ("ive", ""), ("ize", "")]:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.measure(stem) > 1 and (suffix != "ion" or stem[-1:] in "st"):
                    word = stem + replacement
                break

        # Step 5.
        if word.endswith("e"):
            stem = word[:-1]
            m = self.measure(stem)
            if m > 1 or (m == 1 and not self.cvc(stem)):
                word = stem
        if word.endswith("ll") and self.measure(word) > 1:
            word = word[:-1]
        return word


@dataclass
class Result:
    original: str
    stem: str
    lemma: str
    difference: int


def lemmatize(word):
    # A lemma is a meaningful dictionary form, not just a shortened spelling.
    dictionary = {
        "relationship": "relationship", "managers": "manager",
        "continuously": "continuous", "financials": "financial",
        "account": "account", "behaviour": "behaviour", "covenant": "covenant",
        "market": "market", "retention": "retention", "proactive": "proactive",
        "communication": "communication", "industry": "industry",
        "opportunities": "opportunity", "product": "product", "drafting": "draft",
    }
    return dictionary.get(word.lower(), word.lower())


def main():
    words = [
        "relationship", "managers", "continuously", "financials", "account",
        "behaviour", "covenant", "market", "retention", "proactive",
        "communication", "industry", "opportunities", "product", "drafting",
    ]
    stemmer = PorterStemmer()
    results = [
        Result(word, stemmer.stem(word), lemmatize(word),
               abs(len(stemmer.stem(word)) - len(lemmatize(word))))
        for word in words
    ]
    largest = max(r.difference for r in results)
    smallest = min(r.difference for r in results)

    headers = ["Original Word", "Stem", "Lemma", "Stem Length", "Lemma Length", "Difference", "Marker"]
    rows = []
    for r in results:
        marker = []
        if r.difference == largest:
            marker.append(">>> LARGEST <<<")
        if r.difference == smallest:
            marker.append(">>> SMALLEST <<<")
        rows.append([r.original, r.stem, r.lemma, str(len(r.stem)), str(len(r.lemma)), str(r.difference), " / ".join(marker)])

    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    line = "-+-".join("-" * width for width in widths)
    print("=" * 120)
    print("STEMMING AND LEMMATIZATION COMPARISON")
    print("=" * 120)
    print(line)
    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print(line)
    for row in rows:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
    print(line)

    largest_words = [r.original for r in results if r.difference == largest]
    smallest_words = [r.original for r in results if r.difference == smallest]
    print(f"\nLargest difference: {largest} character(s) - {', '.join(largest_words)}")
    print(f"Smallest difference: {smallest} character(s) - {', '.join(smallest_words)}")
    print("\nEXPLANATION")
    print("Stemming mechanically removes or changes suffixes to group related words.")
    print("A stem may not be an English word; for example, 'financials' may become 'financi'.")
    print("Lemmatization uses vocabulary and morphology to return a dictionary form.")
    print("For example, 'managers' becomes 'manager' and 'opportunities' becomes 'opportunity'.")
    print("Therefore, lemmatization is generally more linguistically meaningful than stemming.")


if __name__ == "__main__":
    main()
