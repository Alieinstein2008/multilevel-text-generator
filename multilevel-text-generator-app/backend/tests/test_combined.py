import random

from app.services.text_operations import (
    apply_text_operations,
)

random.seed(42)

text = "A cantora era famosa."

operations = {
    "wordSwap": True,
    "genderSwap": True,
    "paraphrase": False,
}

result, applied = apply_text_operations(text, operations)

print("Original:", text)
print("Resultado:", result)
print("Operações aplicadas:", applied)

assert applied["genderSwap"], "A troca de gênero não foi aplicada."

assert (
    isinstance(result, str) and result.strip()
), "O resultado está vazio ou é inválido."

print("\nTeste combinado concluído.")
