import pandas as pd


def get_dicts_from_df(dataframe: pd.DataFrame) -> tuple[dict, dict]:
    translations_to_korean: dict = {}
    korean_to_translations: dict = {}

    for _, row in dataframe.iterrows():
        # Check for NaN values and skip if any key information is missing
        if pd.isna(row["Deutsch"]) or pd.isna(row["한국어"]):
            continue

        german_word = row["Deutsch"].strip()
        korean_word = row["한국어"].strip()

        # Update the German/English to Korean dictionary
        translations_to_korean.setdefault(german_word, []).append(korean_word)
        translations_to_korean[german_word] = list(
            set(translations_to_korean[german_word])
        )  # Remove duplicates

        # Update the Korean to German/English dictionary
        korean_to_translations.setdefault(korean_word, []).append(german_word)
        korean_to_translations[korean_word] = list(
            set(korean_to_translations[korean_word])
        )  # Remove duplicates
    return translations_to_korean, korean_to_translations
