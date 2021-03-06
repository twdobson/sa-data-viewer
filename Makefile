mac_setup:
	./mac_setup

setup: start_dev_db
	pip install -r requirements.txt
	python manage.py recreate_db

run_server:
	python manage.py runserver

start_dev_db:
	echo "creating docker postgres DB"
	docker run -e POSTGRES_USER=testusr -e POSTGRES_PASSWORD=password -e POSTGRES_DB=testdb -d -p 5432:5432 -v flask-app-db:/var/lib/postgresql/data -d kartoza/postgis:13

recreate_db:
	./scripts/docker_destroy.sh
	start_dev_db
	sleep 2
	python manage.py recreate_db


destroy:
	./scripts/docker_destroy.sh

up:
	docker-compose up

compose_destroy:
	docker-compose stop
	docker-compose rm -f
	docker volume rm flask-app-db

make compose_start:
	docker-compose start

heroku_setup:
	python manage.py recreate_db

initialise_database:	
	# ./scripts/docker_destroy.sh
	# start_dev_db
	python etl_functions/etl.py	


clean:
	find . -name '*.pyo' -delete
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	find . -name '*~' -delete	