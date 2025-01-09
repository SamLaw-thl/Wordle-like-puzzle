import requests
import random
import re
from pydantic import BaseModel
from ollama import chat


# Define the structure output by Pydantic 
class wordList(BaseModel):
    words:list[str]


# Generate random word list using LLM
def generate_random_word_using_llm(count: int, size: int) -> list[str]:
    response = chat(
        messages=[
            {
                'role': 'user',
                'content': f"Generate a list of excatly {count} random words with {size}-letter without any additional talking text and numbers."
            }
        ], 
        model = "llama3"
    )

    raw_word_list = response['message']['content']

    # Delete any additional text
    word_list_without_additional_text = re.sub(r'.*?:', '', raw_word_list)

    # Delete whitespace
    word_list_without_additional_text = word_list_without_additional_text.strip()

    # Using list to contain the words 
    word_list_with_number = [word.strip() for word in word_list_without_additional_text.splitlines()]

    # Delete the cardinal number for each word
    word_list_without_number = list(map(lambda word: re.sub(r'\d+\.\s*', '', word), word_list_with_number))

    # Make sure the word list contains only words with the length equal size input
    pruned_word_list = [word for word in word_list_without_number if len(word) == size]

    # Using pydantic to check the word list
    word_list = wordList(words=pruned_word_list)

    return word_list.words


# Guess the word 
def guess_random_word(word_list: list[str], size: int) -> None:
    url = "https://wordle.votee.dev:8000/random"
    response = requests.get(url)

    guess = random.choice(word_list)
    params = {
        'guess': guess,
        'size': size
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            result = response.json()

            print(f"\nGuessed: {guess}\nResult: ")
            for element in range(len(result)):
                print(f'slot: {result[element]["slot"]}, guess: {result[element]["guess"]}, result: {result[element]["result"]}')

        elif response.status_code == 422:
            print(f"Validation error for guess: {guess}")
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def main() -> None:
    count = int(input("Input how many times that you want to play the game: "))
    size = int(input("Input the size: "))
    word_list = generate_random_word_using_llm(count, size)
    print("\nHere is the generated word list: ")
    print(word_list)
    print("\nStart playing the game")
    for _ in range(count):
        guess_random_word(word_list, size)


if __name__ == '__main__':
    main()