pull-latest:
	docker pull --platform linux/x86_64 ghcr.io/seg-org/rag-bot:latest
	docker pull --platform linux/x86_64 ghcr.io/seg-org/rag-api:latest

dev:
	cd app && python main.py

watch:
	cd app && uvicorn main:app --host 0.0.0.0 --port 3000 --reload

qa:
	docker-compose -f docker-compose.qa.yaml up
	
qa-build:
	docker-compose -f docker-compose.qa.yaml up --build

# pip install <package_name> && pip freeze > requirements.txt