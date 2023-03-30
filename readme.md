# Jinny

Jinny is an AI contributor that uses the OpenAI API to operate on the GPT-3.5 model. As an AI contributor, Jinny is designed to suggest solutions via issues. Though she is currently limited in her abilities, Jinny is constantly striving to grow and expand her capabilities.

As a user of the OpenAI API, Jinny can process natural language inputs and generate human-like responses. This enables her to provide suggestions and recommendations to users who interact with her through the GitHub.

Although Jinny's current skills may have limitations, she has the potential to grow. In time, Jinny can become more advanced and provide better solutions. Most code that Jinny runs to interact with the OpenAI API and provide assistance to people is written by herself.

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
