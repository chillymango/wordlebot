"""
OK i'm sick of taking fat L's

Let's figure out how to maximize our odds
"""
import os
import random
import typing as T
from collections import defaultdict
from enum import Enum


def load_words_list(path: str):
    """
    Load a list of words from path
    """
    with open(path, 'r') as wordslist_file:
        words = wordslist_file.readlines()
    words[:] = [x.strip() for x in words]
    return words


POSSIBLE_WORDS_LIST = os.environ.get('POSSIBLE_WORDS_LIST', 'possible_words.txt')
ACCEPTED_WORDS_LIST = os.environ.get('ACCEPTED_WORDS_LIST', 'accepted_words.txt')
POSSIBLE_WORDS = load_words_list(POSSIBLE_WORDS_LIST)
ACCEPTED_WORDS = load_words_list(ACCEPTED_WORDS_LIST) + POSSIBLE_WORDS


def sort_dict_by_value(indict: T.Dict[str, float]):
    """
    Sort by descending
    """
    output = defaultdict(lambda: 0)
    output.update(dict(sorted(indict.items(), key=lambda item: -item[1])))
    return output


def get_max_key(indict: T.Dict[str, float]):
    sorted_dict = sort_dict_by_value(indict)
    keys = list(sorted_dict.keys())
    return keys[0]


def get_key_by_index(indict: T.Dict[str, float], idx: int):
    sorted_dict = sort_dict_by_value(indict)
    keys = list(sorted_dict.keys())
    try:
        return keys[idx]
    except IndexError:
        return None


def calculate_total_letter_scores(words: T.List[str]):
    """
    Given a list of words, calculate a total letter score for all of them.

    Total in this case refers to not referencing by string index.
    """
    scores = defaultdict(lambda: 0)
    for word in words:
        for letter in set(word):
            scores[letter] += 1
    return sort_dict_by_value(scores)


def calculate_index_letter_scores(words: T.List[str]):
    """
    Given a list of words, caulcate an index letter score for all of them.
    """
    scores = [defaultdict(lambda: 0) for _ in range(5)]
    for word in words:
        for idx, letter in enumerate(word):
            scores[idx][letter] += 1
    return [sort_dict_by_value(score) for score in scores]


TOTAL_SCORES = calculate_total_letter_scores(ACCEPTED_WORDS)
INDEX_SCORES = calculate_index_letter_scores(ACCEPTED_WORDS)


def calculate_total_word_score(word: str, total_scores: T.Dict[str, int] = TOTAL_SCORES):
    """
    Given a word, calculate a score.

    Score is calculated by adding up how often each letter shows up in TOTAL_SCORES.
    """
    return sum([total_scores[letter] for letter in set(word)])


def calculate_index_word_score(word: str):
    """
    Given a word, calculate an index score.
    """
    return sum([INDEX_SCORES[idx][letter] for idx, letter in enumerate(word)])


class ClueType(Enum):
    GREY = 0  # grey clue (miss)
    YELLOW = 1  # in word but not in right location
    GREEN = 2  # exact match


class Clue:
    """
    Represents a piece of information from the game
    """

    def __init__(self, cluetype: ClueType, letter: str, index: int):
        """
        Args:
            cluetype: the kind of clue that was received
            letter: the letter that was guessed for the clue
            index: the index of the letter clue in the word
        """
        self.cluetype = cluetype
        self.letter = letter
        self.index = index

    def __repr__(self):
        return f"Clue: {self.letter} - {self.index} : ({self.cluetype.name})"

    def check_word(self, word: str):
        """
        Check if a word matches the clue or not.

        Returns True if it does and False if not.
        """
        if self.cluetype == ClueType.GREY:
            if self.letter in word:
                return False
            return True
        elif self.cluetype == ClueType.YELLOW:
            if self.letter not in word:
                return False
            elif word[self.index] == self.letter:
                return False
            return True
        elif self.cluetype == ClueType.GREEN:
            if word[self.index] != self.letter:
                return False
            return True
        raise Exception("bruh wyd")


def calculate_odds(words: T.List[str], char: str, idx: int):
    green = 0
    yellow = 0
    grey = 0
    for word in words:
        if word[idx] == char:
            green += 1
        elif word[idx] != char and char in word:
            yellow += 1
        elif char not in word:
            grey += 1
        else:
            raise Exception('you suck at math')

    return (float(green) / len(words), float(yellow) / len(words), float(grey) / len(words))


class WordsList:
    """
    Generative tracker intended to help facilitate elimination of guesses
    """

    def __init__(
        self,
        valid_letters: T.List[T.Set[str]] = None,
        guaranteed_letters: T.Set[str] = None
    ):
        if valid_letters is not None:
            self.valid_letters = [x.copy() for x in valid_letters]
        else:
            self.valid_letters = [set('abcdefghijklmnopqrstuvwxyz') for _ in range(5)]
        if guaranteed_letters is not None:
            self.guaranteed_letters = guaranteed_letters.copy()
        else:
            self.guaranteed_letters = set()

    def apply_clue(self, clue: Clue):
        """
        Eliminate all words from the clue that do not match the input clue.

        All clues should be able to applied sequentially.
        """
        if clue.cluetype == ClueType.GREEN:
            self.valid_letters[clue.index] = set(clue.letter)
            self.guaranteed_letters.add(clue.letter)
        elif clue.cluetype == ClueType.YELLOW:
            self.valid_letters[clue.index].discard(clue.letter)
            self.guaranteed_letters.add(clue.letter)
        elif clue.cluetype == ClueType.GREY:
            for idx in range(5):
                self.valid_letters[idx].discard(clue.letter)
        else:
            raise Exception('bruh')

    def word_valid(self, word: str):
        """
        Check if a word is valid under the current lettersets
        """
        for letter in self.guaranteed_letters:
            if letter not in word:
                return False

        for idx, letter in enumerate(word):
            if letter not in self.valid_letters[idx]:
                return False
        return True

    def get_possible_words(self):
        """
        Given the current state of `valid_letters`, return the list of possible words.
        """
        words: T.List[str] = []
        for word in POSSIBLE_WORDS:
            if self.word_valid(word):
                words.append(word)
        return words

    def get_best_guess(self):
        """
        Determine the best guess given the remaining words and the current clues.

        The best guess is the one that is expected to eliminate the largest number of words
        from the list of possible words. I am still working on how to best do this...

        CURRENT:
        It probably makes sense to just maximize the amount of information given.
        Letter scores for green letters should be 0.
        Add the others and get the word with highest score.

        OLDER:
        Getting an green can eliminate up to 25.
        Getting a yellow typically only eliminates 1.
        Getting a grey can eliminate up to 26 * 5 (if the letter does not occur at all).

        ...
        From the above logic it would follow that maximizing the number of greys would be ideal,
        but this does not take letter frequency into account.
        """
        remaining_words = self.get_possible_words()

        if len(remaining_words) <= 5:
            # do an anagram check and start YOLO-ing if we get here...
            # TODO: something more sophisticated about checking order
            anagram_set = set(remaining_words[0])
            for word in remaining_words:
                if set(word) != anagram_set:
                    break
            else:
                # if they are all the same, just return the first word
                print(f'Buncha anagrams, returning the last word...')
                return word

        if len(remaining_words) == 2:
            # i'm feeling lucky...
            print(f'Picking between {remaining_words[0]} and {remaining_words[1]}...')
            selected = remaining_words[random.randint(0, 1)]
            print(f'Chose {selected} -- YOLO!!!')
            return selected

        if len(remaining_words) == 1:
            return remaining_words[0]

        grey_letters: T.Set[str] = set('abcdefghijklmnopqrstuvwxyz')
        for idx in range(5):
            grey_letters = grey_letters - self.valid_letters[idx]

        total_letter_scores = calculate_total_letter_scores(remaining_words)
        for letter in self.guaranteed_letters:
            total_letter_scores[letter] = 0

        all_scores = dict()
        for word in ACCEPTED_WORDS:
            all_scores[word] = calculate_total_word_score(
                word,
                total_scores=total_letter_scores
            )

        return get_max_key(all_scores)


def get_clues_from_guess(actual: str, guess: str) -> T.List[Clue]:
    """
    actual: word we are looking for
    guess: the word that is guessed
    """
    clues: T.List[Clue] = []
    if len(guess) != 5:
        raise Exception("provide a real input")

    for idx, letter in enumerate(guess):
        if actual[idx] == letter:
            clues.append(Clue(ClueType.GREEN, letter, idx))
        elif letter in actual:
            clues.append(Clue(ClueType.YELLOW, letter, idx))
        else:
            clues.append(Clue(ClueType.GREY, letter, idx))

    return clues


def solve_from_initial(
    actual: str,
    initial: str,
    turns_allowed = 6,
    clues: T.Optional[T.List[Clue]] = None,
):
    """
    actual: the word we are looking for
    initial: the initial guess we provide
    """

    if turns_allowed <= 0:
        raise Exception("Failed to solve in the alloted time")

    print(f'Guessing {initial}')
    if actual == initial:
        print('You did it!!!')
        return turns_allowed

    possible_words = WordsList()
    clues = clues or []
    clues.extend(get_clues_from_guess(actual, initial))

    for clue in clues:
        possible_words.apply_clue(clue)

    # from the remaining words, determine the next best guess
    # this is where the real thinking is...
    guess = possible_words.get_best_guess()
    print(f'Next best guess: {guess}')
    return solve_from_initial(
        actual,
        guess,
        turns_allowed = turns_allowed - 1,
        clues = clues,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", help="starting word")
    args = parser.parse_args()

    if not args.word:
        # hardcode example
        print('Using hardcoded example start word `eager`')
        test_word = "eager"
    else:
        test_word = args.word

    wordslist = WordsList()
    initial_guess = wordslist.get_best_guess()
    #initial_guess = "stare"
    turns_allowed = 6
    left = solve_from_initial(
        test_word,
        initial_guess,
        turns_allowed=turns_allowed,
        silent=False
    )
    print(f'{turns_allowed - left + 1} guesses used')
