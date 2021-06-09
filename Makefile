.PHONY: raw flask full tests app setup

setup:
	docker build -f app/Dockerfile_Setup -t setup .

data/raw/steam_games.json: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)",target=/app/ setup

data/raw/australian_users_items.json: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)",target=/app/ setup

raw: data/raw/australian_users_items.json data/raw/steam_games.json


pipeline:
	docker build -f app/Dockerfile_Pipeline -t pipeline .


data/processed/users_games.csv: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(shell pwd)",target=/app/ pipeline run.py process_data --config=config/config.yaml

data/processed/steam_games.csv: config/config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(shell pwd)",target=/app/ pipeline run.py process_data --config=config/config.yaml

process: data/processed/steam_games.csv data/processed/users_games.csv

ingest:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="$(shell pwd)",target=/app/ pipeline run.py ingest --config=config/config.yaml

data/results/similarities.csv: data/processed/users_games.csv data/processed/steam_games.csv
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="$(shell pwd)",target=/app/ pipeline run.py model --config=config/config.yaml

model: data/results/similarities.csv

full:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI--mount type=bind,source="$(shell pwd)",target=/app/ pipeline run.py full --config=config/config.yaml


app:
	docker build -f app/Dockerfile_App -t webapp .

flask:
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e SQLALCHEMY_DATABASE_URI -p 5000:5000 --mount type=bind,source="$(shell pwd)",target=/app/ webapp


clean:
	rm data/raw/*
	rm data/processed/*
	rm data/results/*
	rm tests/outputs/*

tests:
	docker run pipeline -m pytest