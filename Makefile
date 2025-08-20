.PHONY: up stop down reset restart logs ps status rebuild

# Start containers (detached, rebuild if Dockerfile changed)
up:
	docker compose up -d --build

# Stop containers but keep them (can be restarted quickly)
stop:
	docker compose stop

# Stop and remove containers (keep named volumes & data)
down:
	docker compose down

# Stop and remove containers + volumes (DB reset, MLflow wipe!)
reset:
	docker compose down -v

# Full restart (safe: keeps volumes/data)
restart: down up

# Show last 200 log lines and follow
logs:
	docker compose logs -f --tail=200

# Show running containers and their state
ps:
	docker compose ps

# Quick health/status check
status:
	@echo "=== Container Status ==="
	@docker compose ps
	@echo "\n=== API Health ==="
	@docker compose exec api curl -s http://localhost:8000/healthz || echo "API not responding"
	@echo "\n=== DB Health ==="
	@docker compose exec db pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB || echo "DB not ready"

# Force rebuild of all images and restart
rebuild:
	docker compose build --no-cache
	docker compose up -d
