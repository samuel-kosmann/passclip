import logging
import secrets
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
LOGGING_STYLE = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(format=LOGGING_STYLE, datefmt="%Y-%m-%d %H:%M:%S")


class MarkovChainGenerator:
    """
    A class to generate words using a Markov chain based on a given word list.
    """

    def __init__(self, wordlist_path: str, order: int = 3):
        """
        Initialize the MarkovChainGenerator with a word list and order.

        Args:
            wordlist_path (str): The path to the word list file.
            order (int): The order of the Markov chain.
        """
        self.order = order
        # Load the word list from the specified file
        self.wordlist = MarkovChainGenerator._load_wordlist_from_file(wordlist_path)
        # Build the transitions dictionary from the word list
        self.transitions = MarkovChainGenerator._build_transitions_dict(
            self.wordlist, order=self.order
        )

    def _load_wordlist_from_file(path: str) -> list:
        """
        Load a word list from a file.

        Args:
            path (str): The path to the word list file.

        Returns:
            list: A list of words loaded from the file.
        """

        with open(path, "r") as file:
            wordlist = file.read().splitlines()

        # Check if all lines are valid words
        for word in wordlist:
            if not word.isalpha():
                # Remove invalid words
                wordlist.remove(word)

        # Make all words lowercase
        wordlist = [word.lower() for word in wordlist if word.isalpha()]

        logger.debug("Loaded %d words from %s", len(wordlist), path)

        return wordlist

    def _build_transitions_dict(wordlist: list, order: int = 1) -> Counter:
        """
        Build a transitions dictionary from a list of words.

        Args:
            wordlist (list): A list of words.
            order (int): The order of the Markov chain.

        Returns:
            dict: A dictionary where keys are prefixes and values are Counters of
                next characters.
        """
        transitions = defaultdict(Counter)

        for word in wordlist:
            word = f"{'^' * order}{word}"
            for i in range(len(word) - order):
                prefix = word[i : i + order]
                next_char = word[i + order]
                transitions[prefix][next_char] += 1

        return transitions

    def generate_word(self, length: int = 5) -> str:
        """
        Generate a word using the transitions dictionary.

        Args:
            transitions (dict): The transitions dictionary.
            order (int): The order of the Markov chain.
            length (int): The desired length of the generated word.

        Returns:
            str: A generated word.
        """
        word = "^" * self.order

        while len(word) < length + self.order:
            # Get the last 'order' characters as the prefix
            prefix = word[-self.order :]

            # Get the next character choices based on the prefix
            choices = list(self.transitions[prefix].elements())

            # Check if there are choices available
            if choices == []:
                raise ValueError(
                    (
                        f"No transitions found for prefix '{prefix}'. "
                        "Consider decreasing the order or using a different word list."
                    )
                )

            # Randomly select the next character from the choices
            next_char = secrets.choice(list(choices))
            word += next_char

            logger.debug(f"{prefix} + {next_char} = {word}")

        # Remove the prefix characters from the generated word
        word = word[self.order :]

        return word
