# 🤖 Bot de Discord com MongoDB Atlas

Este projeto é um Bot de Discord modular desenvolvido em **Python** utilizando a biblioteca **`discord.py`** e conexão assíncrona ao **MongoDB Atlas** através do driver **`motor`**.

---

## 📁 Estrutura do Projeto

```text
.
├── cogs/
│   ├── general.py     # Comandos de informação, status e ping
│   └── user_data.py   # Comandos com integração CRUD ao MongoDB Atlas
├── .env               # Suas credenciais seguras (não enviar para o Git)
├── .env.example       # Modelo de arquivo de variáveis de ambiente
├── config.py          # Leitura e validação do .env
├── database.py        # Gerenciamento da conexão com o MongoDB Atlas
├── main.py            # Ponto de entrada e inicialização do Bot
├── requirements.txt   # Dependências do projeto
└── README.md          # Documentação do projeto
```

---

## 🚀 Passo a Passo de Configuração

### 1. Criar o Bot no Discord Developer Portal

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications).
2. Clique em **New Application**, dê um nome para a aplicação e confirme.
3. No menu lateral esquerdo, vá em **Bot**:
   - Clique em **Reset Token** para gerar e copiar seu **DISCORD_TOKEN**.
   - Em **Privileged Gateway Intents**, ative a opção **MESSAGE CONTENT INTENT** (obrigatório para comandos de texto).
4. No menu lateral esquerdo, vá em **OAuth2** -> **URL Generator**:
   - Em *Scopes*, marque `bot`.
   - Em *Bot Permissions*, marque as permissões necessárias (ex: `Send Messages`, `Embed Links`, `Read Message History`).
   - Copie o URL gerado ao final da página e abra no seu navegador para convidar o bot para o seu servidor.

---

### 2. Configurar o MongoDB Atlas

1. Acesse o [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Crie um Cluster gratuito (Shared Tier M0).
3. Vá em **Database Access** e crie um usuário com login e senha (guarde esses dados).
4. Vá em **Network Access** e adicione o endereço IP `0.0.0.0/0` (ou o seu IP atual) para permitir conexões.
5. Vá em **Database** -> **Connect** -> **Drivers** -> selecione **Python**.
6. Copie a string de conexão (MONGO_URI), que terá o formato:
   `mongodb+srv://<usuario>:<senha>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`

---

### 3. Configurar Variáveis de Ambiente

Abra o arquivo `.env` gerado no projeto e insira seu Token do Discord e a URI do MongoDB Atlas:

```env
DISCORD_TOKEN=seu_token_do_discord_aqui
COMMAND_PREFIX=!

MONGO_URI=mongodb+srv://seu_usuario:sua_senha@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=discord_bot_db
```

---

### 4. Instalar as Dependências

Abra o terminal no diretório do projeto e execute:

```bash
pip install -r requirements.txt
```

---

### 5. Executar o Bot

Com as dependências instaladas e o arquivo `.env` configurado, execute:

```bash
python main.py
```

---

## 📌 Comandos Disponíveis

| Comando | Descrição | Permissão |
| :--- | :--- | :--- |
| `!ping` | Exibe a latência do bot e testa o status de resposta do MongoDB Atlas | Qualquer usuário |
| `!info` | Exibe detalhes sobre a arquitetura do bot | Qualquer usuário |
| `!registrar` | Cadastra a conta do usuário no MongoDB Atlas com um bônus inicial | Qualquer usuário |
| `!perfil [@usuario]` | Exibe o perfil e saldo de pontos cadastrado no MongoDB Atlas | Qualquer usuário |
| `!adicionar_pontos @user N` | Adiciona `N` pontos à conta de um usuário no MongoDB Atlas | Administrador |

---

## 🛡️ Dicas de Boas Práticas

- **Segurança**: Nunca compartilhe ou faça commit do seu arquivo `.env` contendo o Token do Discord ou a senha do MongoDB Atlas.
- **Assincronismo**: O projeto utiliza `motor`, permitindo que operações no banco não travem as requisições de outros usuários no bot do Discord.
