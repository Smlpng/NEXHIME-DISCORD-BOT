# Bot-Nexhime

Bot de Discord feito em Python (discord.py) com comandos híbridos (prefixo e slash), organizado por categorias (`commands/`) e com recursos extras como status rotativo e boas-vindas.

## Sumário

- [Principais recursos](#principais-recursos)
- [Rodando o bot](#rodando-o-bot)
- [Configuração](#configuração)
- [Prefixo (por servidor)](#prefixo-por-servidor)
- [Comandos](#comandos)
- [Estrutura do projeto](#estrutura-do-projeto)

## Principais recursos

- **Carregamento automático de cogs:** o `main.py` varre `commands/` recursivamente e carrega todo `.py` que tenha uma função `setup(bot)`.
- **Comandos híbridos:** a maioria dos comandos usa `@commands.hybrid_command`, então funciona via **prefixo** e também via **/** (slash).
- **Prefixo por servidor:** além do prefixo padrão do `config.json`, cada servidor pode ter seu próprio prefixo salvo em `DataBase/prefixes.json`.
- **Status/presença rotativa:** mensagens de status são alternadas periodicamente (ver `status.py`).
- **Help dinâmico com botões:** `/help` ou `prefixo + help` lista categorias e comandos de forma interativa (ver `commands/Geral/help.py`).

## Rodando o bot

### Requisitos

- Python 3.10+ (recomendado)
- Dependências do projeto instaladas

### Instalação

1) Instale as dependências:

```bash
pip install -r requirements.txt
```

2) Crie o arquivo `config.json` (você pode copiar o `config.example.json`).

3) Inicie o bot:

```bash
python main.py
```

## Configuração

O bot lê `config.json` na raiz do projeto.

Campos mais usados:

- `TOKEN`: token do bot no Discord.
- `prefix`: prefixo padrão (ex: `n!`).
- `dev_guild_id` (opcional): se definido, sincroniza slash commands primeiro nesse servidor.

Exemplo (baseado em `config.example.json`):

```json
{
    "TOKEN": "SEU_TOKEN_AQUI",
    "prefix": "n!",
    "dev_guild_id": 123456789012345678,
    "channels": {
        "explore_log": 123456789012345678,
        "combat_log": null
    }
}
```

## Prefixo (por servidor)

O prefixo funciona assim:

- **Padrão:** vem de `config.json` (`prefix`).
- **Por servidor:** é salvo em `DataBase/prefixes.json`.
- O bot também responde por **menção** (ex: `@Bot ping`).

Comandos relacionados a prefixo (Moderação):

- `prefix` — mostra o prefixo atual do servidor.
- `set <novo_prefixo>` — define um novo prefixo (admin).
- `reset` — restaura para o prefixo padrão (admin).
- `show_prefix` — mostra prefixo atual e o padrão (admin).

Além disso, existe `setprefix` em `main.py` (permissão `manage_guild`) que altera direto o prefixo cacheado e persiste no `DataBase/prefixes.json`.

## Comandos

Dica: use **`/help`** (ou `prefixo + help`) para ver a lista de forma dinâmica por categoria.

### Geral

- `help` — menu de ajuda por categoria (botões)
- `comandos` — lista de comandos por categoria (dropdown)
- `ping` — latência do bot
- `invite` — envia por DM um convite do servidor configurado em `commands/Geral/invite.py`
- `avatar` — mostra avatar do usuário
- `userinfo` — informações do usuário
- `serverinfo` — informações do servidor
- `say` — envia uma mensagem pelo bot
- `remindme` — lembretes
- `quote` — sistema de frases/citações (usa `DataBase/quotes.json`)
- `receber_tag` — utilitário de tags/cargos

### Entretenimento

- `8ball` — respostas estilo “bola 8”
- `ascii` — ASCII art
- `joke` — piadas
- `meme` — memes
- `quotes` — frases/quotes
- `roll` — rolagem aleatória
- `ship` — compatibilidade/ship
- `showdomilhao` — minigame/quiz
- `tomate` — interações de “tomatada” (usa `DataBase/tomate.json`)
- `tweet` — gera imagem estilo tweet (templates em `assets/templates/tweet/` e canais em `DataBase/tweet_channels.json`)
- `wanted` — gera imagem estilo “wanted” (template em `assets/templates/wanted/`)
- `triangulo`, `triodragao`, `cerebelo`, `fatos`, `fogueira`, `piseinamerda` — comandos de diversão variados

### Moderação

- `kick`, `ban`, `unban`, `softban` — punições
- `mute` — silenciar membro
- `warn` — avisos
- `lock` — trancar canal
- `nuke` — limpar/recriar canal
- `roles` — utilitários de cargos
- `emoji` — utilitários de emoji
- `embed_send` — enviar embeds
- `add_sticker` — utilitários de figurinha
- `bump_reminder` — lembrete de bump (usa `DataBase/bump_reminder.json`)
- `prefix`, `set`, `reset`, `show_prefix` — gerenciamento de prefixo
- `welcome_novo` — configuração/rotinas de boas-vindas (ver também `welcome.py`)
- `roadmap`, `parcerias`, `check_hibridos` — utilitários diversos de servidor

### RPG

O RPG fica em `commands/RPG/` e inclui comandos de:

- **Combate:** `fight`, `pvp`, `raid`, `dungeon`
- **Zonas/Exploração:** `zone`, `change_zone`
- **Heróis:** `race`, `tribe`, `quests`, `descansar` (alias `rest`)
- **Equipamento:** `equip`, `forge`, `inventory`
- **Economia/Recursos:** `bank`, `shop`, `trade`
- **Stats/Dex:** `stats`, `dex`, `advancements`

Dados do RPG costumam ficar em JSON (ex: `DataBase/players.json`).

## Estrutura do projeto

- `main.py` — inicia o bot, carrega cogs automaticamente e sincroniza slash commands.
- `commands/` — comandos por categoria (Geral/Entretenimento/Moderação/RPG).
- `DataBase/` — arquivos JSON usados por alguns comandos (prefixos, quotes, bump reminder, RPG etc.).
- `assets/` — fontes e templates de imagem (tweet/wanted/entretenimento).

## Observações

- Se você adicionar um novo comando, garanta que o arquivo tenha `async def setup(bot): ...` para ser carregado automaticamente.
- Alguns módulos utilitários existem mas podem estar comentados/desativados por padrão (ex: `mov_chat.py`).
