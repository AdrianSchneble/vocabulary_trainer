import random
from datetime import datetime, timedelta

import pandas as pd


def _find_plausible_distractors_improved(word, options_pool, num_distractors=3):
    """
    Find plausible distractors for a given word from the options_pool.
    If not enough similar words are found, it picks random words as distractors.

    :param word: The word for which to find distractors.
    :param options_pool: The pool of words to search for similar words.
    :param num_distractors: Number of distractors to return.
    :return: A list of plausible distractors.
    """
    # Select words that start with the same first letter or have the same length as the given word
    first_letter = word[0]  # Consider the first letter for similarity
    similar_length_words = [
        w for w in options_pool if len(w) == len(word) and w != word
    ]
    similar_words = [
        w for w in options_pool if w.startswith(first_letter) and w != word
    ]

    # Combine the lists of similar words, prioritize them, and ensure they're unique
    combined_similar = list(set(similar_words + similar_length_words))
    random.shuffle(combined_similar)
    chosen_distractors = combined_similar[:num_distractors]

    # If we don't have enough similar words, fill the rest with random choices
    if len(chosen_distractors) < num_distractors:
        remaining_options = list(set(options_pool) - set(chosen_distractors) - {word})
        random.shuffle(remaining_options)
        chosen_distractors.extend(
            remaining_options[: num_distractors - len(chosen_distractors)]
        )

    return chosen_distractors


def create_multiple_choice_question(dicts, chosen_word):
    """
    Create a multiple-choice question from the given dictionaries.

    :param dicts: Tuple of two dictionaries (from_korean and to_korean).
    :param from_korean: Boolean indicating the direction of translation.
    :return: A tuple containing the question, correct answer, and options.
    """
    # Determine if the chosen word is Korean or a translation
    from_korean = chosen_word in dicts[1]

    from_dict, to_dict = dicts if from_korean else dicts[::-1]
    question_word = random.choice(list(from_dict.keys()))
    correct_answers = from_dict[question_word]
    correct_answer = random.choice(correct_answers)

    # Find distractors from the opposite dictionary
    options_pool = list(to_dict.keys())  # Pool of possible options for distractors
    distractors = _find_plausible_distractors_improved(correct_answer, options_pool)

    # Combine correct answer and distractors, then shuffle
    options = distractors + [correct_answer]
    random.shuffle(options)

    return question_word, correct_answer, options


def update_selection_algorithm(historical_results, current_results, dicts):
    # Combine historical and current session results
    all_results = historical_results + current_results
    df = pd.DataFrame(all_results)

    weighted_vocab = []

    never_queried_weight = 10

    if not df.empty:
        df["datetime"] = pd.to_datetime(df["timestamp"])

        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        # Calculate weights based on historical correctness and recency
        df["weight"] = df.apply(
            lambda row: (0.5 if row["user_correct"] else 2)
            * (0.5 if row["datetime"] > day_ago else 1)
            * (0.75 if row["datetime"] > week_ago else 1.25),
            axis=1,
        )

        # Sum weights by query and answer type (Korean or translation)
        weights_korean = (
            df[df["query"].isin(dicts[0].keys())]
            .groupby("query")["weight"]
            .sum()
            .to_dict()
        )
        weights_translation = (
            df[df["query"].isin(dicts[1].keys())]
            .groupby("query")["weight"]
            .sum()
            .to_dict()
        )

        # Add Korean words and their weights
        for word, weight in weights_korean.items():
            weighted_vocab.extend([word] * int(weight))

        # Add translations and their weights
        for word, weight in weights_translation.items():
            weighted_vocab.extend([word] * int(weight))

    # Add a default weight for words never queried, or if no historical records exists (i.e. df.empty == true)
    for word in dicts[0].keys():
        if df.empty or word not in weights_korean:
            weighted_vocab.extend([word] * never_queried_weight)

    for word in dicts[1].keys():
        if df.empty or word not in weights_translation:
            weighted_vocab.extend([word] * never_queried_weight)

    # Shuffle the weighted vocab to ensure randomness
    random.shuffle(weighted_vocab)
    return weighted_vocab
