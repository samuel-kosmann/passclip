import secrets

import pyperclip
import typer

from passclip.generator import MarkovChainGenerator

app = typer.Typer()

wordlist = "/usr/share/dict/words"

section_length = 6
sections = 3
delimiter = "-"
capitals_per_section = 1
number_per_section = 1


@app.command()
def generate():
    mcg = MarkovChainGenerator(wordlist, order=3)

    password = ""

    for _ in range(sections):
        # Generate a random word that is not a real word
        for attempt in range(11):
            if attempt == 10:
                raise ValueError(
                    "Failed to generate a non-real word after 10 attempts."
                )

            word = mcg.generate_word(length=section_length)
            if word in mcg.wordlist:
                continue
            break

        # Add capitals
        for _ in range(capitals_per_section):
            index = secrets.randbelow(section_length)
            word = word[:index] + word[index].upper() + word[index + 1 :]

        # Add numbers
        for _ in range(number_per_section):
            index = secrets.randbelow(section_length)
            number = str(secrets.randbelow(10))
            word = word[:index] + number + word[index + 1 :]

        password += f"{word}{delimiter}"

    password = password.rstrip(delimiter)  # Remove the trailing delimiter

    # Copy the generated password to the clipboard
    pyperclip.copy(password)
    # typer.echo(f"Generated password: {password}")


if __name__ == "__main__":
    app()
