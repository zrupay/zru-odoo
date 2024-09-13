REQUIREMENTS=`cat requirements.txt | tr '\n' ' '`

.PHONY: start
start:
	docker-compose up -d
	docker-compose exec web pip3 install $(REQUIREMENTS)

.PHONY: stop
stop:
	docker-compose down

.PHONY: restart
restart:
	docker-compose down
	docker-compose up -d
	docker-compose exec web pip3 install $(REQUIREMENTS)

.PHONY: enter-odoo
enter-odoo:
	docker-compose exec web /bin/bash

.PHONY: install-requirements
install-requirements:
	docker-compose exec web pip3 install $(REQUIREMENTS)

.PHONY: full-stop
full-stop:
	docker-compose down
	docker volume prune -f

.PHONY: full-restart
full-restart:
	docker-compose down
	docker volume prune -f
	docker-compose up -d
	docker-compose exec web pip3 install $(REQUIREMENTS)
