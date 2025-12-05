import random
from collections import Counter, defaultdict
from pathlib import Path

from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from passclip.logging_config import console


class MarkovChain:
    wordlist: set[str] | None = None
    transition_table: dict[str, Counter] | None = None

    def __init__(self, order: int = 3):
        self.order = order

    def load_wordlist(self, path: str) -> None:
        """Loads a wordlist from a file, cleans it, and stores it in self.wordlist.
        Args:
            wordlist_path (str): The path to the wordlist file.
        Raises:
            FileNotFoundError: If the wordlist file does not exist.
        """
        # Check if the wordlist file exists
        wordlist_path = Path(path)
        if not wordlist_path.is_file():
            raise FileNotFoundError(f'Wordlist file not found: "{wordlist_path}"')

        # Open wordlist file
        console.print(f'Loading wordlist from: "{wordlist_path}"')

        with open(wordlist_path, "r") as wordlist_file:
            # Read all lines from the file
            wordlist = wordlist_file.read().splitlines()
            word_count = len(wordlist)

            console.print(f"Total words in wordlist: {word_count}")

            # Initialize empty set for cleaned wordlist
            self.wordlist = set()

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total}"),
                TimeElapsedColumn(),
                TextColumn("/"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                # create task to track progress
                task = progress.add_task("Cleaning wordlist:", total=word_count)
                for word in wordlist:
                    # Check if words only contain alphabetic characters
                    if word.isalpha():
                        # Convert word to lowercase and add to set
                        self.wordlist.add(word.lower())

                    progress.update(task, advance=1)

            # Report cleaned wordlist size
            console.print(f"Removed {len(wordlist) - len(self.wordlist)} invalid words")

    def set_order(self, order: int) -> None:
        """Sets the order of the Markov chain.
        Transition table needs to be rebuilt after changing order.

        Args:
            order (int): The order of the Markov chain.
        """
        self.order = order

    def build_transition_table(self) -> None:
        """
        Build the transitions dictionary for the laoded wordlist.

        1.  Count how often one character follows a set of preceding characters:
            '^' is a placeholder token for the start of a word

            Example for the word "apple" and order 2:
            ^^ -> Next char: a
            ^a -> Next char: p
            ap -> Next char: p
            pp -> Next char: l
            pl -> Next char: e

            Doing this for all words creates a transitions table like this:
            {'^^': {'a': 10, 'b': 5, ...},
             '^a': {'p': 8, 'n': 2, ...},
             ...}

        2.  Convert counts to probabilities for each transition:

            Sum the total transitions for each prefix, then divide each count by
            the total to get a probability.

            Example:
            For prefix '^^' with transitions {'a': 10, 'b': 5}:
            Total transitions = 10 + 5 = 15
            Probabilities:
            'a': 10 / 15 = 0.6667
            'b': 5 / 15 = 0.3333

            New transitions table:
            {'^^': {'a': 0.6667, 'b': 0.3333, ...},
             '^a': {'p': 0.8, 'n': 0.2, ...},
             ...}

        Args:
            order (int): The order of the Markov chain.
        """
        console.print(f"Building transition table with order {self.order}")

        # Check if wordlist is loaded
        if not self.wordlist:
            raise ValueError("Wordlist is not loaded, load a wordlist first.")

        # Create transitions dictionary
        self.transition_table = defaultdict(Counter)

        # Count transitions from one character to the next
        for word in self.wordlist:
            # Pad the beginning of the word with start tokens
            # apple -> ^^apple for order 2
            word = f"{'^' * self.order}{word}"

            # Iterate through each character in the word and record transitions
            for i in range(len(word) - self.order):
                prefix = word[i : i + self.order]
                next_char = word[i + self.order]
                self.transition_table[prefix][next_char] += 1

    def generate_string(self, length: int = 5) -> str:
        """Generate a word using the transitions dictionary.

        Args:
            length (int): The desired length of the generated string.

        Returns:
            str: A generated string.
        """

        # Check if transition table is present
        if not self.transition_table:
            raise ValueError(
                "Transition table is not available "
                "build or load the transition table first."
            )

        # Start with the starting tokens
        output_string = "^" * self.order

        while len(output_string) < length + self.order:
            # Get the first 'order' characters as the prefix
            # For order 2: ^^, ^a, ap, pp, pl, ...
            prefix = output_string[-self.order :]

            # Get possible next characters and their probabilities
            counter = self.transition_table[prefix]
            possible_chars = list(counter.keys())
            probabilities = list(counter.values())

            # Check if there are choices available, if not raise an error
            if not possible_chars:
                raise ValueError(
                    (
                        f"No transitions found for prefix '{prefix}'. "
                        "Consider decreasing the order or using a different word list."
                    )
                )

            # Randomly select the next character based on the probabilities
            next_char = random.choices(possible_chars, weights=probabilities)[0]

            # Append the selected character to the output string
            output_string += next_char

        # Remove starting tokens before returning
        output_string = output_string[self.order :]

        return output_string
