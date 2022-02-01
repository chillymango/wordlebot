"""
Analyze for best possible starting word
"""
from contextlib import contextmanager
import os
import sys
import typing as T

from pydantic import BaseModel
from solve import POSSIBLE_WORDS
from solve import solve_from_initial
from solve import WordsList


@contextmanager
def __silence_stdout():
    old_stdout = sys.stdout
    with open(os.devnull, 'w') as devnull_out:
        try:
            sys.stdout = devnull_out
            yield
        finally:
            sys.stdout = old_stdout


class Performance(BaseModel):

    scores: T.Dict[str, float]
    max: float = None
    min: float = None
    mean: float = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # calculate some stats here...
        self.max = self._get_max()
        self.min = self._get_min()
        self.mean = self._get_mean()

    def _get_max(self) -> T.Tuple[int, T.List[str]]:
        """
        Find the max score and all words that match the max score
        """
        max_score = max(self.scores.values())
        words = [word for word, score in self.scores.items() if score == max_score]
        return (max_score, words)

    def _get_min(self) -> T.Tuple[int, T.List[str]]:
        """
        Find the min score (that isn't trivial -- 1) and all words that match
        """
        min_score = min([score for score in self.scores.values() if score > 1])
        words = [word for word, score in self.scores.items() if score == min_score]
        return (min_score, words)

    def _get_mean(self) -> float:
        """
        Calculate the mean score (expected score)
        """
        return sum(self.scores.values()) / len(self.scores.values())


def analyze_default(max_guesses: int = 30) -> T.Dict[str, int]:
    """
    Use the default best guess
    """
    wordslist = WordsList()
    initial = wordslist.get_best_guess()
    return analyze_start(initial, max_guesses = max_guesses)


def analyze_start(initial: str, max_guesses: int = 30) -> T.Dict[str, int]:
    """
    Analyze a given starting word
    """
    scores: T.Dict[str, int] = dict()
    print(f'Solving for starting word {initial}')
    for actual in POSSIBLE_WORDS:
        with __silence_stdout():
            res = max_guesses - solve_from_initial(
                actual,
                initial,
                turns_allowed = max_guesses
            ) + 1
            scores[actual] = res

    return scores


if __name__ == "__main__":

    default = analyze_default()

    TO_ANALZYE = [
        'stare',
        'roate',
        'raise',
        'anime',
        'adieu',
        'steak',
        'tread',
        'table',
        'audio',
        'slice',
        'tried',
        'crane',
        'close',
        'trice',
        'train',
        'slate',
        'lance',
        'trace',
    ]
    results = dict()
    perf = dict()
    for starting_word in TO_ANALZYE:
        results[starting_word] = analyze_start(starting_word)
        perf[starting_word] = Performance(scores=results[starting_word])

    import IPython; IPython.embed()
