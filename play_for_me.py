from solve import ACCEPTED_WORDS, Clue
from solve import ClueType
from solve import WordsList

def main():

    wordslist = WordsList()

    while True:
        try:
            guessed_word = input('Enter the word you guessed:\n')
            if guessed_word not in ACCEPTED_WORDS:
                print(f'{guessed_word} is not a recognized word')
                continue

            hints = input('Enter the hints you got back (Y = yellow X = grey G = green):\n')

            for idx, (letter, hint) in enumerate(zip(guessed_word, hints)):
                if hint.lower() == 'y':
                    cluetype = ClueType.YELLOW
                elif hint.lower() == 'g':
                    cluetype = ClueType.GREEN
                elif hint.lower() == 'x':
                    cluetype = ClueType.GREY
                else:
                    raise ValueError('Invalid hint entered')

                wordslist.apply_clue(Clue(cluetype, letter, idx))

            remaining_words = wordslist.get_possible_words()
            if len(remaining_words) == 1:
                print(f'The word is {remaining_words[0]}!')
                return
            elif len(remaining_words) == 0:
                raise Exception('No words left. Something went wrong')
            print(f'Remaining Words:\n{wordslist.get_possible_words()}')
            print(f'Best Guess: {wordslist.get_best_guess()}')

        except KeyboardInterrupt:
            print('Exiting')
            break
        except ValueError:
            print(f"Invalid input character {hint}")
            raise


if __name__ == "__main__":
    main()
