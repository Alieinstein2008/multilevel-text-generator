# Multilevel Text Generator

O **Multilevel Text Generator** é uma aplicação desenvolvida para auxiliar na transformação e na análise da complexidade linguística de textos educacionais. O sistema combina operações heurísticas de mutação textual, processamento de linguagem natural (NLP) e aprendizado de máquina para estimar o nível de ensino associado a um texto.

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/spaCy-09A3D5?style=flat-square&logo=spacy&logoColor=white" alt="spaCy" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas" />
</p>

## Demonstração da aplicação

A interface responsiva permite transformar textos, consultar estatísticas linguísticas e comparar os níveis de complexidade previstos para o conteúdo original e suas versões modificadas.

<p align="center">
  <img src="multilevel-text-generator-app/assets/Interface0003.png" alt="Interface do Multilevel Text Generator — visão geral" width="32%" />
  <img src="multilevel-text-generator-app/assets/Interface0002.png" alt="Interface do Multilevel Text Generator — análise textual" width="32%" />
  <img src="multilevel-text-generator-app/assets/Interface0001.png" alt="Interface do Multilevel Text Generator — comparação de resultados" width="32%" />
</p>

## Funcionalidades

### Transformação textual

- **Substituição de palavras:** substitui palavras selecionadas por sinônimos ou antônimos de uma base lexical estruturada, utilizando similaridade vetorial e restrições gramaticais para orientar a escolha dos candidatos.
- **Transformação de gênero:** altera substantivos e adjetivos masculinos e femininos mapeados e utiliza informações de dependência sintática para ajustar artigos e adjetivos relacionados.
- **Paráfrase:** a opção está presente na interface, mas a operação ainda não foi implementada. Sua implementação está planejada para uma versão futura. Atualmente, a API retorna HTTP 422 quando essa operação é solicitada.

### Análise da complexidade linguística

A aplicação classifica os textos em quatro níveis de ensino:

| Sigla | Nível de ensino |
|---|---|
| EF1 | Ensino Fundamental I |
| EF2 | Ensino Fundamental II |
| EM | Ensino Médio |
| ES | Ensino Superior |

O painel de análise apresenta a classe prevista, as probabilidades associadas a cada classe e estatísticas descritivas do texto:

- Quantidade de palavras e sentenças.
- Comprimento médio das palavras.
- Diversidade lexical.
- Proporção de palavras que atendem à heurística de canonicidade.

Quando o texto inserido contém menos de 100 palavras, a interface apresenta um aviso contextual ao usuário.

## Arquitetura e tecnologias

A aplicação separa a interface de usuário do processamento textual e do pipeline de aprendizado de máquina.

| Camada | Tecnologias | Responsabilidades |
|---|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS e Lucide React | Entrada de texto, seleção das operações, interface responsiva e visualização comparativa dos resultados |
| Backend e API | Python, FastAPI e Pydantic | Validação das requisições e coordenação do processamento textual |
| Processamento de linguagem natural | spaCy (`pt_core_news_lg`) | Análise linguística, embeddings e ajustes gramaticais baseados em dependências sintáticas |
| Aprendizado de máquina | scikit-learn, NumPy, pandas e joblib | Processamento de características, classificação e serialização do modelo |
| Recursos lexicais | JSON e recurso derivado do TeP 2.0 | Consulta a candidatos a sinônimos e antônimos para substituição de palavras |

A base lexical tem origem em um recurso derivado do TeP 2.0, disponibilizado por meio do projeto `stavarengo/portuguese-brazilian-synonyms`.

## Modelo de classificação da complexidade

O classificador foi treinado com um conjunto de **2.076 documentos textuais extraídos de materiais didáticos do Ministério da Educação (MEC)**.

### Configuração do modelo

O modelo utiliza o `HistGradientBoostingClassifier`, da biblioteca scikit-learn, com os seguintes parâmetros:

| Parâmetro | Valor |
|---|---:|
| `max_iter` | 400 |
| `max_depth` | 6 |
| `learning_rate` | 0.05 |
| `max_leaf_nodes` | 31 |

O pipeline de representação textual e engenharia de características combina:

- **TF-IDF:** representação de unigramas e bigramas, limitada a 5.000 características.
- **Redução de dimensionalidade:** `TruncatedSVD` com 100 componentes.
- **Características linguísticas:** vetor com 31 características adicionais extraídas por meio do spaCy, abrangendo estrutura textual, riqueza lexical, distribuição de classes gramaticais, relações sintáticas e características morfológicas.
- **Canonicidade:** heurística personalizada que avalia padrões de caracteres consoante-vogal (CV) nos tokens. O modelo utiliza a média dos escores, sua dispersão e a proporção de palavras com pontuação perfeita.

A avaliação utiliza particionamento estratificado de 80% para treinamento e 20% para validação e teste. Os resultados abaixo correspondem ao conjunto de teste isolado, composto por 416 documentos.

### Resultados da avaliação

| Métrica | Resultado |
|---|---:|
| Acurácia no teste | **91,35%** |
| F1-score macro | **90,24%** |
| F1-score — Ensino Superior (ES) | 0,94 |
| F1-score — Ensino Fundamental II (EF2) | 0,87 |

A matriz de confusão relatada indica que os principais erros de classificação ocorrem entre níveis de ensino adjacentes, incluindo a sobreposição entre textos próximos à transição do EF1 para o EF2.

Esses resultados correspondem ao conjunto de dados e às condições de avaliação utilizados no projeto. Eles não representam uma garantia de desempenho equivalente para qualquer texto.

## Operadores de mutação textual

O endpoint de geração retorna o texto processado e uma trilha de auditoria das operações aplicadas.

### 1. Substituição de palavras

Substitui até cinco palavras selecionadas por sinônimos ou antônimos consultados em uma base lexical JSON.

A seleção de candidatos utiliza similaridade vetorial com recursos do spaCy e restrições gramaticais. O operador considera flexões de gênero e número e limita substituições envolvendo verbos conjugados.

### 2. Transformação de gênero

Transforma substantivos e adjetivos masculinos e femininos presentes nos mapeamentos disponíveis. Após a alteração principal, o operador percorre as árvores de dependência sintática do spaCy para ajustar a concordância dos artigos e adjetivos relacionados.

### 3. Paráfrase

A operação de paráfrase está planejada para uma versão futura. Embora a opção esteja disponível na interface, sua implementação ainda não foi concluída. Atualmente, a API retorna HTTP 422 quando a operação é solicitada.

## Instalação e execução

### Pré-requisitos

O backend depende dos seguintes artefatos:

- Modelo de classificação serializado: `modelo_complexidade.joblib`, localizado em `backend/app/ml/models/`.
- Base lexical: `output.json`, acessível a partir do diretório do backend.
- Modelo de português do spaCy: `pt_core_news_lg`.

Antes de iniciar a aplicação, verifique se os artefatos necessários estão disponíveis nos caminhos esperados.

### Executando o backend

A partir da raiz do repositório, instale as dependências e inicie o servidor de desenvolvimento:

```bash
cd multilevel-text-generator-app/backend

python -m pip install -r requirements.txt

python -m spacy download pt_core_news_lg

python -m uvicorn app.main:app --reload
```

A opção `--reload` habilita a reinicialização automática do servidor durante o desenvolvimento.

