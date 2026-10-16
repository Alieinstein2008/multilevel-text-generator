from app.services.text_operations import (
    swap_gender,
)

TEST_CASES = [
    {
        "name": "Feminino para masculino",
        "input": "A cantora era famosa.",
        "expected": "O cantor era famoso.",
    },
    {
        "name": "Masculino para feminino",
        "input": "O cantor era famoso.",
        "expected": "A cantora era famosa.",
    },
    {
        "name": "Possessivo e adjetivo",
        "input": "Meu amigo era alto.",
        "expected": "Minha amiga era alta.",
    },
    {
        "name": "Profissão e concordância",
        "input": "A professora era dedicada.",
        "expected": "O professor era dedicado.",
    },
    {
        "name": "Adjetivo com substantivo feminino",
        "input": "A médica estava cansada.",
        "expected": "O médico estava cansado.",
    },
    {
        "name": "Texto sem palavras reconhecidas",
        "input": "O carro estava na garagem.",
        "expected": "O carro estava na garagem.",
    },
]


def main():
    passed = 0
    failed = 0

    print("=" * 70)
    print("TESTE DE TROCA DE GÊNERO")
    print("=" * 70)

    for case in TEST_CASES:
        original = case["input"]
        expected = case["expected"]

        try:
            result = swap_gender(original)
            success = result == expected

            if success:
                passed += 1
                status = "PASSOU"
            else:
                failed += 1
                status = "FALHOU"

            print(f"\n[{status}] {case['name']}")
            print(f"Original:  {original}")
            print(f"Esperado:  {expected}")
            print(f"Obtido:    {result}")

        except Exception as exc:
            failed += 1

            print(f"\n[ERRO] {case['name']}")
            print(f"Original:  {original}")
            print(f"Exceção:   {type(exc).__name__}: {exc}")

    print("\n" + "=" * 70)
    print(f"Resultado: {passed} passaram; {failed} falharam.")
    print("=" * 70)


if __name__ == "__main__":
    main()
