SHELL = /bin/sh

.DEFAULT_GOAL := help

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up:
	docker compose up -d --build
down:
	docker compose down

restart_parser:
	docker restart hhparser-parser-1
	docker logs -f hhparser-parser-1

restart_web:
	docker restart hhparser-web-1
	docker logs -f hhparser-web-1


migrations:
	docker exec -it hhparser-web-1 python3 manage.py makemigrations
	docker exec -it hhparser-web-1 python3 manage.py makemigrations app
	docker exec -it hhparser-web-1 python3 manage.py migrate

createsuperuser:
	docker exec -it hhparser-web-1 python3 manage.py createsuperuser
	docker restart hhparser-parser-1
	docker restart hhparser-web-1

