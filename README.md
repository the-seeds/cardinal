# Cardinal


Create a `.env` file in the root directory:

```
.
├── src
└── .env
```

```
OPENAI_API_KEY=sk-xxxx
EMBED_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo-1106

REDIS_URI=redis://192.168.0.1:6379
MILVUS_URI=http://192.168.0.1:19530
MILVUS_TOKEN=0
```

## Build Database

```bash
python src/launcher.py --action build
```

## Launch Server

```bash
python src/launcher.py --action launch
```
