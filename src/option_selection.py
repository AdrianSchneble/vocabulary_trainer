import random
from datetime import datetime, timedelta

import jellyfish
import pandas as pd


def _filter_similar_words(base_str, words) -> list[str]:
    """Returns a sorted list of the most similar words (the first element is most similar)"""
    # Create a dictionary to hold words and their similarity scores
    similar_words = {
        word: jellyfish.jaro_winkler_similarity(base_str, word)
        for word in words
        if word != base_str
    }
    filtered_sorted_words = sorted(
        similar_words,
        key=lambda word: similar_words[word],
        reverse=True,
    )
    return filtered_sorted_words


def _find_plausible_distractors(word, options_pool, num_distractors=3):
    """
    Find plausible distractors for a given word from the options_pool.
    If not enough similar words are found, it picks random words as distractors.

    :param word: The word for which to find distractors.
    :param options_pool: The pool of words to search for similar words.
    :param num_distractors: Number of distractors to return.
    :return: A list of plausible distractors.
    """
    similar_words = _filter_similar_words(word, options_pool)

    # Pick the most similar word, and sample the remaining words.
    # Sample from more than just the <num_distractors> top words!
    # This decreases the accuracy of the distrators, but it ensures some variation, instead of always
    # showing the same options for a specific given word. As a countermeasure, the top result is always kept.
    most_similar_word = similar_words[0]
    num_distractors -= 1
    remaining_words = similar_words[1:]

    # + 2, because two degrees of freedom is a good middle ground.
    second_most_similar_words = random.sample(
        remaining_words[: num_distractors + 2], num_distractors
    )
    chosen_distractors = [most_similar_word] + second_most_similar_words

    return chosen_distractors


def create_multiple_choice_question(dicts, chosen_word) -> tuple[str, str, list, bool]:
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
    distractors = _find_plausible_distractors(correct_answer, options_pool)

    # Combine correct answer and distractors, then shuffle
    options = distractors + [correct_answer]
    random.shuffle(options)

    return question_word, correct_answer, options, from_korean


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
