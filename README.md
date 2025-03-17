# Coletor de Tweets

O **Coletor de Tweets** é um projeto em Python criado para coletar e armazenar tweets utilizando a API do Twitter. Inicialmente inspirado no caso de uso do livro *Um Voluntário na Campanha de Obama*, este projeto tem como objetivo demonstrar a importância do monitoramento de redes sociais. Agora, o coletor permite buscar tweets sobre **qualquer termo desejado** via **parâmetro de busca (`search`)**, tornando-o altamente flexível para análises e pesquisas.

## 🚀 **Funcionalidades**
- 📡 **Coleta de tweets em tempo real**.
- 🔍 **Busca personalizada** por palavras-chave, hashtags ou usuários via parâmetro `search`.
- 📊 **Extração de métricas avançadas**, como sentimentos e engajamento (likes, retweets, respostas).
- 💾 **Armazenamento em formatos CSV, JSON e banco de dados MongoDB**.
- 🔥 **Cálculo de hype score**, que mede o nível de engajamento dos tweets.

---

## 🛠️ **Tecnologias Utilizadas**
- **Python 3.x**
- **Flask** (API)
- **MongoDB** (Armazenamento de tweets e métricas)
- **Tweepy** (Acesso à API do Twitter)
- **Pandas** (Processamento de dados)
- **NLTK** (Análise de sentimentos)

---

## 📌 **Pré-requisitos**
Antes de iniciar, certifique-se de ter instalado:

- **Python 3.x**
- **pip** (gerenciador de pacotes do Python)
- **MongoDB** (opcional, caso utilize armazenamento em banco de dados)

---

## ⚙️ **Instalação**

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/carvalhoandre/coletor-tweets.git
   cd coletor-tweets
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**
   python -m venv venv
   
   #### Para Linux/macOS:
   ```source venv/bin/activate```
   
   #### Para Windows:
   ```venv\Scripts\activate```

3. **Instale as dependências:**
   
   ```pip install -r requirements.txt```

---

## 🔑 Configuração

1. **Obtenha as credenciais da API do Twitter:**

Para utilizar o coletor, você precisará das credenciais da API (API Key, API Secret, Access Token e Access Token Secret). Essas credenciais podem ser obtidas ao criar um aplicativo no Twitter Developer.

2. **Configure as credenciais:**
Crie um arquivo de configuração, por exemplo, config.py ou um arquivo .env com as seguintes variáveis:

#### Exemplo de config.py
```
TWITTER_API_KEY = 'sua_api_key'
TWITTER_API_SECRET = 'sua_api_secret'
TWITTER_ACCESS_TOKEN = 'seu_access_token'
TWITTER_ACCESS_TOKEN_SECRET = 'seu_access_token_secret'
```

3. **Banco de Dados (Opcional):**
   Se deseja armazenar os tweets em MongoDB, adicione a variável de ambiente:
    ```
    DATABASE_MONGO_URI='mongodb://localhost:27017'
    ```

---

## 🚀 Uso
Para iniciar a coleta de tweets, utilize o seguinte comando:
```
python coletor.py --keywords "Copa do Mundo" --output tweets.csv
```

📡 Acessando a API
Os endpoints permitem buscar tweets sobre qualquer assunto, especificado pelo parâmetro search.

### Parâmetros Comuns:
- --keywords: Define as palavras-chave ou hashtags para filtrar os tweets.
- --output: Especifica o nome do arquivo onde os tweets coletados serão salvos.
- Outros parâmetros podem ser implementados conforme a necessidade do projeto.

### Exemplo de Uso
Coletar tweets contendo a palavra-chave Neymar e salvar no arquivo coleta.csv:
```
python coletor.py --keywords "Neymar" --output coleta.csv
```

## 🔥 API Endpoints

A seguir, estão listados os endpoints disponíveis na API do projeto:

### 1️⃣ GET Buscar Tweets  `/fetch_tweets`

- **Descrição:**  
 Busca tweets relacionados ao termo especificado no parâmetro search.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos tweets.
  - `search` (obrigatório): Define o termo de busca (exemplo: "Messi", "Bitcoin").

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Tweets retrieved" e os dados dos tweets.
  - **Nenhum tweet encontrado (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro (400 para erros de validação e 500 para erros internos).

### 2️⃣ GET Análise de Sentimentos `/feelings`

- **Descrição:**  
  Busca tweets, processa os sentimentos extraídos dos mesmos e retorna o resultado como JSON.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos tweets.
  - `search` (obrigatório): Define o termo de busca (exemplo: "Messi", "Bitcoin").

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Feelings retrieved" e os dados dos sentimentos processados.
  - **Nenhum tweet encontrado (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro.

### 3️⃣ GET Métricas Horárias e Indicador de Hype `/hourly_metrics`

- **Descrição:**  
  Processa os tweets para extrair métricas horárias e retorna o resultado como JSON.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos dados.
  - `search` (obrigatório): Define o termo de busca (exemplo: "Messi", "Bitcoin").

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Feelings retrieved" e os dados das métricas horárias.
  - **Nenhum dado disponível (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro.

---
## 🎯 Principais Melhorias

✅ Busca dinâmica por qualquer termo via search.

✅ Novo indicador de hype score, analisando engajamento e sentimentos.

✅ Métricas horárias detalhadas para insights profundos.

✅ Análises de sentimentos com NLP para entender reações do público.

✅ Otimização da coleta e processamento de tweets.

---
## 📌 Contribuição
🚀  Contribuições são bem-vindas!

Em breve: Arquivo CONTRIBUTING.md para mais detalhes.

---

## 📜 Licença
Este projeto está licenciado sob a [MIT License](LICENSE) .

---
