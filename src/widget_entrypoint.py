import random
from datetime import datetime

from IPython.display import clear_output
from ipywidgets import Button, HBox, Label, Layout, Output, VBox

from src.audio import correct_sound, incorrect_sound, play_vocabulary_tts
from src.historical_results import load_historical_results, save_results_to_file
from src.option_selection import (
    create_multiple_choice_question,
    update_selection_algorithm,
)


# create dynamic layout for answer buttons
def create_button_grid(buttons, columns=2) -> VBox:
    # Calculate the number of rows needed
    rows = len(buttons) // columns + (len(buttons) % columns > 0)

    # Create a list to hold all the row HBox widgets
    hbox_rows = []

    for i in range(rows):
        # Extract the buttons for this row
        row_buttons = buttons[i * columns : (i + 1) * columns]

        # Check if this row is the last and has an odd number of buttons
        if i == rows - 1 and len(row_buttons) % columns != 0:
            # Make the last button double width if there"s an odd number of buttons
            row_buttons[-1].layout.width = "auto"

        # Create a HBox for each row
        hbox = HBox(row_buttons)
        hbox_rows.append(hbox)

    # Create a VBox to hold all HBoxes (rows)
    vbox = VBox(hbox_rows)

    return vbox


# Function to create and manage the quiz with result tracking and real-time adjustment
def create_mc_question_widget_with_tracking(
    dicts: tuple[dict, dict],
    container: VBox,
    results: list[dict] | None = None,
    historical_data: list[dict] | None = None,
) -> None:
    if results is None:
        results = []
    if historical_data is None:
        historical_data = load_historical_results()

    # Clear previous widgets
    clear_output(wait=True)
    container.children = []  # Remove previous widgets

    common_style = {"font_size": "20px"}

    # Update the vocabulary selection based on historical and current session results
    weighted_vocab = update_selection_algorithm(historical_data, results, dicts)

    # Select a random entry from weighted_vocab
    chosen_word = random.choice(weighted_vocab)

    # Get the question details
    question, correct_answer, options, from_korean = create_multiple_choice_question(
        dicts, chosen_word
    )

    button_width = "25%"

    # Create the list of buttons for answer options
    answer_buttons = [
        Button(
            description=option,
            layout=Layout(
                width=button_width, height="auto", padding="10px 40px", margin="5px"
            ),
            style=common_style,
        )
        for option in options
    ]

    answer_buttons_grid = create_button_grid(answer_buttons)

    # Label for the question
    question_label = Label(f'Translate: "{question}"', style=common_style)

    # Output widget to display messages
    output = Output(style=common_style)

    # Next question button
    next_button = Button(
        description="Next",
        button_style="primary",
        layout=Layout(
            width=button_width, height="auto", padding="10px 40px", margin="5px"
        ),
        style=common_style,
    )

    # Stop quiz button
    stop_button = Button(
        description="Stop",
        button_style="danger",
        layout=Layout(
            width=button_width, height="auto", padding="10px 40px", margin="5px"
        ),
        style=common_style,
    )

    # Function to handle button click event for answers
    def on_button_clicked(b):
        with output:
            clear_output()
            answer_correct = b.description == correct_answer
            if answer_correct:
                print("Correct!")
                next_button.style.button_color = "LimeGreen"
                correct_sound()
            else:
                print(f"Incorrect! The correct translation is: {correct_answer}")
                next_button.style.button_color = "Orange"
                incorrect_sound()

            if not from_korean:
                # i.e. the source is not korean, but the answer (= b.description) is
                play_vocabulary_tts(b.description)
            # Record the result
            results.append(
                {
                    "query": question,
                    "correct_translation": correct_answer,
                    "user_correct": answer_correct,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Disable buttons after a choice is made
        for button in answer_buttons:
            button.disabled = True

    # Attach the event handler to all the answer buttons
    for button in answer_buttons:
        button.on_click(on_button_clicked)

    # Button event handlers
    def on_next_button_clicked(b):
        # Create a new question with the current results and historical data
        create_mc_question_widget_with_tracking(
            dicts, container, results, historical_data
        )

    def on_stop_button_clicked(b):
        if len(results) > 0:
            # Save the results to a file
            save_results_to_file(results)
        # Clear the container and stop the quiz
        container.children = [Label("Quiz stopped. Results saved.")]
        clear_output(wait=True)

    next_button.on_click(on_next_button_clicked)
    stop_button.on_click(on_stop_button_clicked)

    # Arrange buttons and question into a box
    buttons_box = HBox([next_button, stop_button])
    answer_box = VBox(
        [question_label] + [answer_buttons_grid] + [buttons_box, output],
        layout=Layout(display="flex", flex_flow="column", align_items="stretch"),
    )

    # Update the container with the new widgets
    container.children = [answer_box]

    if from_korean:
        play_vocabulary_tts(question)
