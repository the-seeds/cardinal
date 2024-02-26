# Cardinal

[![GitHub Code License](https://img.shields.io/github/license/the-seeds/cardinal)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pycardinal)](https://pypi.org/project/pycardinal/)

## Usage

Create a `.env` file in the root directory:

```
.
├── src
└── .env
```

```
# imitater or openai
OPENAI_BASE_URL=http://localhost:8010/v1
OPENAI_API_KEY=0

# models
EMBED_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
TOKENIZER_PATH=01-ai/Yi-6B-Chat

# text splitter
CHUNK_SIZE=200
CHUNK_OVERLAP=30

# storages
STORAGE=redis
SEARCH_TARGET=content
REDIS_URI=redis://localhost:6379
ELASTICSEARCH_URI=http://localhost:9001

# vectorstore
VECTORSTORE=chroma
CHROMA_PATH=./chroma
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=0
```
