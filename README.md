# WhatsApp-Chat-Analyzer

This projects build an application capable of analyzing a Chat Export from WhatsApp and get interesting insights.

## Current Progress

### Home screen

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/b85dc4cc-737f-4571-b64c-83eb45d6263f)

### Analyze View

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/87a6c76c-d926-453c-bb4a-3b9c56634324)

### Feedback Form

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/da84c90c-19c8-45a9-bb39-6b0cf56f9551)

### S3 Object storage

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/01f31912-5c00-41c6-8a5f-a95aa041168e)

#### Recently added

- I recently added the Hall of Fame feature which allows users to see who has the most messages with a given keyword.

- I recently added the exact match feature, so now users can look for messages containg the exact word they are looking for.

- I recently added s3 bucket upload, and ingestion from ETL pipeline.

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/0d3782e0-fdcf-45ce-a508-a67a8722601a)

## Heroku Deployment

![image](https://github.com/kevinknights29/WhatsApp-Chat-Analyzer/assets/74464814/66b59797-7bb4-4eec-be63-c865fd6da883)

## Local Usage

Open as a devcontainer with Visual Studio Code.

Run the following command inside the devcontainer.

```bash
flask run
```

## Contributing

### Installing pre-commit

Pre-commit is already part of this project dependencies.
If you would like to installed it as standalone run:

```bash
pip install pre-commit
```

To activate pre-commit run the following commands:

- Install Git hooks:

```bash
pre-commit install
```

- Update current hooks:

```bash
pre-commit autoupdate
```

To test your installation of pre-commit run:

```bash
pre-commit run --all-files
```
