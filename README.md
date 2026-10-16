
# Multilevel Text Generator

Aplicação web para transformação de textos e análise estimada de complexidade textual em quatro níveis de ensino: Ensino Fundamental 1, Ensino Fundamental 2, Ensino Médio e Ensino Superior.

## Funcionalidades

- Classificação de complexidade textual com machine learning.
- Estimativa de probabilidades para os quatro níveis de ensino.
- Substituição de palavras usando um dicionário de sinônimos e antônimos, com seleção auxiliada por similaridade semântica.
- Transformação de gênero de substantivos, artigos e adjetivos em padrões suportados.
- Comparação de indicadores linguísticos entre o texto original e o transformado.
- Interface para visualizar as transformações e as classificações.

A paráfrase permanece indisponível nesta versão.

## Tecnologias

**Frontend:** Next.js, React, TypeScript e Tailwind CSS.

**Backend:** Python, FastAPI, spaCy, scikit-learn, NumPy, pandas e joblib.

**Classificador:** TF-IDF, TruncatedSVD, características linguísticas e HistGradientBoostingClassifier.

## Estrutura do repositório

```text
multilevel-text-generator/
├── README.md
└── multilevel-text-generator-app/
    ├── backend/
    │   ├── app/
    │   │   ├── classifier_api.py
    │   │   ├── complexity_classifier.py
    │   │   ├── text_operations.py
    │   │   └── modelo_complexidade.joblib
    │   └── requirements.txt
    └── src/
        ├── app/
        ├── components/
        ├── services/
        └── types/
```

## Requisitos

- Python instalado.
- Node.js e npm compatíveis com a versão do Next.js declarada no `package.json`.
- O modelo spaCy português `pt_core_news_lg`.
- O arquivo `modelo_complexidade.joblib` e o dicionário `output.json` disponíveis no backend.

## Configuração do backend

No terminal:

```powershell
cd multilevel-text-generator-app/backend

python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

Se o ambiente virtual `.env` já existir e estiver sendo usado, ative-o em vez de criar outro. O nome `.venv` é recomendado para novos ambientes.

Inicie a API:

```powershell
python -m uvicorn app.main:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

## Configuração do frontend

Em outro terminal:

```powershell
cd multilevel-text-generator-app
npm ci
```

Crie o arquivo `.env.local` com:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Inicie o frontend:

```powershell
npm run dev
```

A aplicação estará disponível em `http://localhost:3000`.

## Observações

A classificação é uma estimativa produzida por um modelo treinado com documentos de diferentes níveis de ensino. O desempenho em frases muito curtas pode diferir do desempenho observado na avaliação do conjunto de documentos.

As transformações lexicais e de gênero são limitadas pelas entradas do dicionário e pelas regras implementadas; nem toda frase pode ser transformada com segurança.
