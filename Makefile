APP = vc-wait-bot

rebuild: stop remove build run

build:
	docker build --rm --tag=$(APP) .
	docker image prune -f

run:
	docker run -itd --mount type=bind,source="$(shell pwd)/src/db",target=/src/db --name $(APP) $(APP)

stop:
	docker stop $(APP)

logs:
	docker logs -f $(APP)

remove:
	docker rm $(APP)

clean: stop remove
	docker image rm $(APP)
	docker system prune