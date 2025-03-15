# Cardinal

[![GitHub Code License](https://img.shields.io/github/license/the-seeds/cardinal)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pycardinal)](https://pypi.org/project/pycardinal/)

## Usage

Create a `.env` file in the `api_demo` directory:

```
api_demo
├── utils
└── .env
```

```
# imitater or openai
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=0

# models
DEFAULT_EMBED_MODEL=text-embedding-ada-002
DEFAULT_CHAT_MODEL=gpt-3.5-turbo
DEFAULT_RERANKER=bge-reranker-v2-m3 # empty if not needed
HF_TOKENIZER_PATH=01-ai/Yi-6B-Chat

# text splitter
DEFAULT_CHUNK_SIZE=300
DEFAULT_CHUNK_OVERLAP=100

# storages
STORAGE=redis
SEARCH_TARGET=content
REDIS_URI=redis://localhost:6379
ELASTICSEARCH_URI=http://localhost:9001

# graph storage
GRAPH_STORAGE=neo4j
NEO4J_URI=bolt://localhost:7687

# vectorstore
VECTORSTORE=chroma
CHROMA_PATH=./chroma
MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=0
```

Run `python launch.py --config config.yaml --action build`
