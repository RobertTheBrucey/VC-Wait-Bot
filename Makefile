APP = VC-Wait-Bot

build:
	docker build --rm --tag=$(APP) .
	docker image prune -f

run:
	docker run -itd --name $(APP) --rm $(APP)

stop:
	docker stop $(APP)

clean:
	docker image rm $(APP)
	docker system prune