APP = vc-wait-bot

build:
	docker build --rm --tag=$(APP) .
	docker image prune -f

run:
	docker run -itd --name $(APP) $(APP)

stop:
	docker stop $(APP)

logs:
	docker logs -f $(APP)

clean:
	docker image rm $(APP)
	docker system prune