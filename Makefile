pull-latest:
	docker pull --platform linux/x86_64 ghcr.io/seg-org/rag-bot:latest

dev:
	cd app && python main.py

watch:
	uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# pip install <package_name> && pip freeze > requirements.txt