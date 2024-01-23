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
OPENAI_BASE_URL=http://192.168.0.1:8010/v1
OPENAI_API_KEY=0

# models
EMBED_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo-1106
TOKENIZER_PATH=Qwen/Qwen-14B-Chat

# text splitter
CHUNK_SIZE=200
CHUNK_OVERLAP=30
NUM_CPU_CORE=16

# storages
STORAGE=redis
REDIS_URI=redis://192.168.0.1:6379
ELASTICSEARCH_URI=http://192.168.0.1:9001

# vectorstore
VECTORSTORE=chroma
CHROMA_PATH=./chroma
MILVUS_URI=http://192.168.0.1:19530
MILVUS_TOKEN=0
ADMIN_USER_ID=123456789

# KBQA
DEFAULT_SYSTEM_PROMPT=You are a helpful assistant.
EMBED_INSTRUCTION=为这个句子生成表示以用于检索相关文章：
PLAIN_TEMPLATE=你是ChatGPT，由OpenAI开发的大语言模型，针对问题作出详细和有帮助的解答。\n\n问题：{question}
KBQA_TEMPLATE=你是ChatGPT，由OpenAI开发的大语言模型，根据已知信息，针对问题作出详细和有帮助的解答。\n\n已知信息：{context}\n\n问题：{question}
KBQA_THRESHOLD=1.0
KBQA_TEMPERATURE=0.95

# WordGraph
KEYWORD_TEMPLATE=提取文章里的实体概念，数量不超过三个，用分号“；”分割。文章内容：{answer}
KEYWORD_TEMPERATURE=0

# service
SERVICE_PORT=8020

# tests
SERVER_URL=http://192.168.0.1:8020
```

## Build Database

```bash
python src/launcher.py --action build
```

## Launch Server

```bash
python src/launcher.py --action launch
```

## View Collected Messages

```bash
python src/launcher.py --action view
```
