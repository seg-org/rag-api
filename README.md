# rag-api

## Repositories

- [bot](https://github.com/seg-org/rag-bot)
- [api](https://github.com/seg-org/rag-api)

Making a bot that can **leverage chat context** with **RAG** to generate consistent responses.

## Stack

- langchain
- fastapi

## Getting Started

### Prerequisites

- 💻
- python 3

### Installation

1. Clone this repo
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Copy `.env.template` and paste it in the same directory as `.env` and fill in the values.
```bash
# for these, see README.md in the bot repo
BOT_TOKEN=
BOT_CLIENT_ID=
GUILD_ID=

# go to https://platform.openai.com/account/api-keys (you need to top-up some $$ first)
OPENAI_API_KEY=

# go to https://smith.langchain.com and create an account + api key
LANGCHAIN_API_KEY=

# go to https://tavily.com and create an account + api key (for internet searches when there's no relevant data in rag)
TAVILY_API_KEY=
```
3. Copy `prompt_tone.example.json` in `./app/config` and paste it in the same directory as `prompt_tone.json` and fill in the desired base prompt (what tone should the bot respond to your messages) or keep it as is.

### Running

1. Run `docker-compose up -d` to start vector database and bot.
2. Run `make dev` or `make watch` to start local api.
