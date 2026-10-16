from app.services.text_operations import (
    swap_words,
)
examples = [
    "O aluno estava feliz.",
    "A casa era bonita.",
    "O homem estava cansado.",
]

for text in examples:
    result = swap_words(text)

    print(f"Original: {text}")
    print(f"Resultado: {result}")
    print("-" * 40)
