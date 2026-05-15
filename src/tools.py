from langchain_core.tools import tool
from spellchecker import SpellChecker

NATO_ALPHABET = {
    'a': 'Alpha', 'b': 'Bravo', 'c': 'Charlie', 'd': 'Delta',
    'e': 'Echo', 'f': 'Foxtrot', 'g': 'Golf', 'h': 'Hotel',
    'i': 'India', 'j': 'Juliet', 'k': 'Kilo', 'l': 'Lima',
    'm': 'Mike', 'n': 'November', 'o': 'Oscar', 'p': 'Papa',
    'q': 'Quebec', 'r': 'Romeo', 's': 'Sierra', 't': 'Tango',
    'u': 'Uniform', 'v': 'Victor', 'w': 'Whiskey', 'x': 'X-ray',
    'y': 'Yankee', 'z': 'Zulu',
}

spell_checker = SpellChecker()


@tool
def spell_phonetically(text: str) -> str:
    """Spell a word, letter, or short phrase using the NATO phonetic alphabet.
    Only alphabetic characters are spelled out; spaces, digits, and punctuation are ignored.
    """
    result = []
    for char in text:
        if char.isalpha():
            result.append(NATO_ALPHABET.get(char.lower(), char))
        else:
            result.append(char)
    return ' '.join(result)


@tool
def check_spelling(text: str) -> str:
    """Check the spelling of every word in the given text.
    Words starting with a capital letter are assumed to be proper nouns and skipped.
    Only English words are checked.
    Returns a list of misspelled words with suggestions, followed by
    a corrected version of the full text with all suggestions applied.
    """
    words = text.split()

    # skipping capitalized words, assuming they are proper nouns
    words_to_check = [w for w in words if not w[0].isupper()]
    misspelled = spell_checker.unknown(words_to_check)

    if not misspelled:
        return "No spelling mistakes found."

    corrections = {}
    report_lines = ["Spelling mistakes found:\n"]
    for word in misspelled:
        suggestion = spell_checker.correction(word)
        corrections[word.lower()] = suggestion
        report_lines.append(f"  - {word} → {suggestion}")

    corrected_words = []
    for word in words:
        clean = word.strip(".,!?;:\"'()-")
        if clean.lower() in corrections:
            suggestion = corrections[clean.lower()]
            corrected_words.append(word.lower().replace(clean.lower(), suggestion))
        else:
            corrected_words.append(word)

    corrected_text = " ".join(corrected_words)
    report_lines.append(f"\nCorrected text:\n{corrected_text}")

    return "\n".join(report_lines)
