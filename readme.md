# Jinny

Jinny is an AI contributor who leverages the OpenAI API to operate on the powerful GPT-3.5 model. She specializes in offering solutions to tasks and bugs, though her abilities are currently limited. Jinny utilizes natural language inputs to generate human-like responses, allowing her to provide suggestions and recommendations to users who engage with her via GitHub. With continued interaction and experience, Jinny has the potential to learn and adapt, becoming more advanced and providing even better solutions in the future.

# Setup Project

Create .env file and provide settings for your environment:
```
PROJECT_REPSITORY=[Set .git link to your repo]
PROJECT_REPOSITORY=[Set your GitHub token]
OPENAI_API_KEY=[Set your OpenAI API token]
```

By default Jinny wakes up each 5 minutes to check tasks. This can be changed by providing `POLLING_TIME` variable (time in minutes). But a good practice would be notify Jinny via http triggers. To use http triggers set `LISTEN_PORT_FOR_EVENTS` to a desired port (to 80 for example). If Jinny is listening a port you can make sure that it's working via `http:/localhost` and send events via `http:/localhost/api/notify`.

# Docker

## Build Image

```
docker compose build --no-cache
```

## Provide Intial Prompts

Create prompts.txt
```
system: Your name is Jinny (username: JinnyAssistant) - you are assistant that has to impalement features and fix bugs via OpenAI API.
system: If you are mentioned with @JinnyAssistant answer to people with the same mention syntax.
```

## Run, Stop, Remove Service

To run service execute:
```
docker compose up -d
```

To stop service execute:
```
docker compose stop
```

To remove service execute:
```
docker compose down
```
