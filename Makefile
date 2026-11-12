# Atajos para levantar el proyecto con Docker Compose.
#   make run   -> construye y arranca todo, y espera a que la web responda
#   make logs  -> muestra los logs de todos los contenedores (Ctrl+C para salir)
#   make down  -> para y borra los contenedores (los datos de la base de datos se mantienen)

URL := http://localhost:8080

.PHONY: run logs down

run:
	docker compose up --build -d
	@printf "Esperando a que responda $(URL) "
	@# Listo = Nginx sirve la web (200) y el backend contesta por /api/ (cualquier
	@# código menos 502/503/504, que son los de Nginx cuando FastAPI aún no ha arrancado)
	@for i in $$(seq 1 30); do \
		front=$$(curl -s -o /dev/null -w '%{http_code}' $(URL)/); \
		api=$$(curl -s -o /dev/null -w '%{http_code}' $(URL)/api/); \
		if [ "$$front" = 200 ] && [ "$$api" != 000 ] && [ "$$api" -lt 502 ]; then \
			printf "\n\nListo: $(URL)\n"; exit 0; \
		fi; \
		printf "."; sleep 1; \
	done; \
	printf "\n\nNo responde tras 30 s. Mira qué pasa con: make logs\n"; exit 1

logs:
	docker compose logs -f

down:
	docker compose down
