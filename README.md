# Coletor de Tweets

O **Coletor de Tweets** é um projeto em Python criado para coletar e armazenar tweets utilizando a API do Twitter. Baseado em um caso de uso do livro *Um voluntário na campanha de Obama*, onde o monitoramento das redes sociais foi fundamental, o projeto foi inicialmente concebido para demonstrar a importância dessa prática. Atualmente, o coletor está configurado para buscar tweets somente sobre Neymar, facilitando análises específicas e pesquisas direcionadas.

## Funcionalidades

- Coleta de tweets em tempo real.
- Filtragem por palavras-chave, hashtags ou usuários.
- Armazenamento dos tweets coletados em formatos como CSV ou JSON.
- Fácil configuração e personalização dos parâmetros de coleta.

## Tecnologias Utilizadas

- **Python 3.x**
- Bibliotecas:
  - [Tweepy](https://www.tweepy.org/) para acesso à API do Twitter
  - Outras bibliotecas como `pandas`, `requests`, `flask` etc. (conforme necessidade)

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- Python 3.x
- pip (gerenciador de pacotes do Python)

## Instalação

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


## Configuração

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

3. **Ajuste os parâmetros de coleta::**
Edite o arquivo principal (por exemplo, coletor.py) ou utilize argumentos de linha de comando para definir os filtros desejados (como palavras-chave, hashtags, etc.). Atualmente, o projeto está configurado para buscar tweets relacionados a Neymar.

## Uso
Para iniciar a coleta de tweets, execute o script principal. Por exemplo:

```
python coletor.py --keywords "Neymar" --output tweets.csv
```

### Parâmetros Comuns:
- --keywords: Define as palavras-chave ou hashtags para filtrar os tweets.
- --output: Especifica o nome do arquivo onde os tweets coletados serão salvos.
- Outros parâmetros podem ser implementados conforme a necessidade do projeto.

### Exemplo de Uso
Coletar tweets contendo a palavra-chave Neymar e salvar no arquivo coleta.csv:
```
python coletor.py --keywords "Neymar" --output coleta.csv
```
## API Endpoints

A seguir, estão listados os endpoints disponíveis na API do projeto:

### GET `/fetch_tweets`

- **Descrição:**  
  Busca tweets e retorna-os como resposta em JSON.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos tweets.

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Tweets retrieved" e os dados dos tweets.
  - **Nenhum tweet encontrado (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro (400 para erros de validação e 500 para erros internos).

### GET `/feelings`

- **Descrição:**  
  Busca tweets, processa os sentimentos extraídos dos mesmos e retorna o resultado como JSON.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos tweets.

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Feelings retrieved" e os dados dos sentimentos processados.
  - **Nenhum tweet encontrado (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro.

### GET `/hourly_metrics`

- **Descrição:**  
  Processa os tweets para extrair métricas horárias e retorna o resultado como JSON.

- **Parâmetros de Consulta:**
  - `force_refresh` (opcional): Se definido como `true`, força a atualização dos dados.

- **Resposta:**
  - **Sucesso (200):**  
    JSON com status verdadeiro, mensagem "Feelings retrieved" e os dados das métricas horárias.
  - **Nenhum dado disponível (404):**  
    JSON com status falso e mensagem "No tweets available".
  - **Erros (400 ou 500):**  
    JSON com status falso e mensagem de erro.

## Contribuição
Contribuições são bem-vindas!

Em breve: Arquivo CONTRIBUTING.md para mais detalhes.

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE) .

