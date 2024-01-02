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
OPENAI_BASE_URL=http://192.168.0.1:8000/v1
OPENAI_API_KEY=0

# models
EMBED_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo-1106
TOKENIZER_PATH=hiyouga/Qwen-14B-Chat-LLaMAfied
TEMPERATURE=0.95

# text splitter
CHUNK_SIZE=200
CHUNK_OVERLAP=30

# storages
CHROMA_PATH=./chroma
REDIS_URI=redis://192.168.0.1:6379
MILVUS_URI=http://192.168.0.1:19530
MILVUS_TOKEN=0
ADMIN_USER_ID=123456789

# RAGs
DEFAULT_SYSTEM_PROMPT=You are a helpful assistant.
EMBED_INSTRUCTION=为这个句子生成表示以用于检索相关文章：
PLAIN_TEMPLATE=你是ChatGPT，由OpenAI开发的大语言模型，针对问题作出详细和有帮助的解答。\n\n问题：{question}
KBQA_TEMPLATE=你是ChatGPT，由OpenAI开发的大语言模型，根据已知信息，针对问题作出详细和有帮助的解答。\n\n已知信息：{context}\n\n问题：{question}
KBQA_THRESHOLD=1.0

# tests
SERVER_URL=http://192.168.0.1:8000
```

## Build Database

```bash
python src/launcher.py --action build
```

## Launch Server

```bash
python src/launcher.py --action launch
```
