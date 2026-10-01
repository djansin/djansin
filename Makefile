######################################################
#            Docker Container Management             #
######################################################

## Build and start all containers with forced recreation
## Usage: make build
build:
	docker compose -f ./compose.yml up --build -d --remove-orphans --force-recreate

## Start all containers in detached mode
## Usage: make up
up:
	docker compose -f ./compose.yml up -d

## Stop and remove containers
## Usage: make down
down:
	docker compose -f ./compose.yml down

## Stop and remove containers including volumes
## Usage: make down-v
down-v:
	docker compose -f ./compose.yml down -v

## Display container logs
## Usage: make logs
logs:
	docker compose -f ./compose.yml logs

## Display Docker Compose configuration
## Usage: make configs
configs:
	docker compose -f ./compose.yml config

.PHONY: build up down down-v logs configs

######################################################
#              Database Operations                   #
######################################################

## Start only the database service
## Usage: make db-up
db-up:
	docker compose -f ./compose.yml up -d db

## Access PostgreSQL database with psql client
## Usage: make psql
psql: db-up
	docker compose -f ./compose.yml exec db bash -c "run-as $$(id -u) -- yarsin psql"

## Create a backup of the database
## Usage: make db-backup
db-backup: db-up
	docker compose -f ./compose.yml exec db bash -c "yarsin backup data --dbname \$${POSTGRES_DB}"

## Restore database from backup
## Usage: make db-restore
db-restore: db-up
	docker compose -f ./compose.yml exec -T db bash -c "yarsin restore data"

## Drop and recreate the database (destructive operation)
## Usage: make db-recreate
db-recreate: db-up
	docker compose -f ./compose.yml exec -T db bash -c "yarsin recreate data --dbname \$${POSTGRES_DB}"

## Create a full DBMS backup
## Usage: make dbms-backup
dbms-backup: db-up
	docker compose -f ./compose.yml exec db bash -c "yarsin backup dbms"

## Restore full DBMS from backup
## Usage: make dbms-restore
dbms-restore: db-up
	docker compose -f ./compose.yml exec -T db bash -c "yarsin restore dbms"

.PHONY: db-up psql db-backup db-restore db-recreate dbms-backup dbms-restore

######################################################
#              Django Application Operations         #
######################################################

## Start only the Django API service
## Usage: make api-up
api-up:
	docker compose -f ./compose.yml up -d api

## Open a bash shell in the Django container with proper user permissions
## Usage: make api-bash
api-bash: api-up
	docker compose -f ./compose.yml run --rm api sh -c "run-as $$(id -u) -- bash"

## Initialize the project using yarsin custom script
## Usage: make init
init:
	docker compose -f ./compose.yml run --rm --no-deps api sh -c "run-as $$(id -u) -- yarsin init"

## Create a new Django project
## Usage: make startproject
startproject:
	docker compose -f ./compose.yml run --rm --no-deps api sh -c "run-as $$(id -u) -- yarsin startproject"

## Start Django development server on port 8000
## Usage: make runserver
runserver: api-up
	docker compose -f ./compose.yml exec -T api bash -c "yarsin runserver 0.0.0.0:8000"

## Access Django shell (Python REPL with Django context)
## Usage: make shell
shell: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin shell"

## Create new Django model migrations based on model changes
## Usage: make makemigrations
makemigrations: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin makemigrations"

## Apply pending database migrations
## Usage: make migrate
migrate: api-up
	docker compose -f ./compose.yml exec -T api bash -c "yarsin migrate"

## Create a Django superuser for admin access
## Usage: make createsuperuser
createsuperuser: api-up
	docker compose -f ./compose.yml exec api bash -c "yarsin createsuperuser"

## Collect static files into the configured static root
## Usage: make collectstatic
collectstatic: api-up
	docker compose -f ./compose.yml exec -T api bash -c "yarsin collectstatic --noinput"

## Run pytest test suite
## Usage: make pytest
pytest: api-up
	docker compose -f ./compose.yml exec -T api bash -c "yarsin pytest"

## Create one or more Django applications (standard app structure)
## Usage: make createapp app1 [app2 app3 ...]
## Example: make createapp blog users payments
startapp: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin startapp $(filter-out $@,$(MAKECMDGOALS))"

## Create one or more Django applications (standard app structure)
## Usage: make createapp app1 [app2 app3 ...]
## Example: make createapp blog users payments
createapp: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin createapp $(filter-out $@,$(MAKECMDGOALS))"

## Create one or more Django applications as Python packages (with __init__.py)
## Usage: make createpack app1 [app2 app3 ...]
## Example: make createpack blog users payments
createpack: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin createapp --package $(filter-out $@,$(MAKECMDGOALS))"

## Create one or more core Django applications (with specific core structure)
## Usage: make createcore app1 [app2 app3 ...]
## Example: make createcore blog users payments
createcore: api-up
	docker compose -f ./compose.yml exec -T api bash -c "run-as $$(id -u) -- yarsin createapp --core $(filter-out $@,$(MAKECMDGOALS))"

.PHONY: api-up api-bash init startproject runserver shell makemigrations migrate createsuperuser collectstatic pytest startapp createapp createpack createcore

######################################################
#                 Documentation Operations           #
######################################################

## Build Sphinx documentation
## Usage: make doc-build
doc-build: api-up
	docker compose -f ./compose.yml exec -T api bash -c "yarsin sphinx-build"

## Serve built documentation via HTTP server
## Usage: make doc-serve
doc-serve: api-up
	docker compose -f ./compose.yml exec -T api bash -c "python -m http.server --directory \$${DOC_OUTPUT}"

## Build and serve documentation (convenience target)
## Usage: make doc
doc: doc-build doc-serve

## Auto-generate Sphinx API documentation from docstrings
## Usage: make doc-autogen
doc-autogen:
	docker compose -f ./compose.yml exec -T api bash -c "sphinx-apidoc -o ./docs/source/api ./app"

.PHONY: doc-build doc-serve doc doc-autogen

######################################################
#                 Utility Operations                 #
######################################################

## Show status of all containers
## Usage: make status
status:
	docker compose -f ./compose.yml ps

## Show real-time resource usage of containers
## Usage: make stats
stats:
	docker stats $$(docker compose -f ./compose.yml ps -q)

## Remove unused Docker resources (containers, networks, images, build cache)
## Usage: make prune
prune:
	docker system prune -f

## Display this help message with all available commands
## Usage: make help
help:
	@echo "Available commands:"
	@echo ""
	@echo "DOCKER MANAGEMENT:"
	@echo "  make build             - Build and start all containers (force recreation)"
	@echo "  make up                - Start all containers in detached mode"
	@echo "  make down              - Stop and remove containers"
	@echo "  make down-v            - Stop, remove containers and volumes"
	@echo "  make logs              - Show container logs"
	@echo "  make configs           - Show Docker Compose configuration"
	@echo ""
	@echo "DATABASE:"
	@echo "  make psql              - Access PostgreSQL database"
	@echo "  make db-backup         - Create database backup"
	@echo "  make db-restore        - Restore database from backup"
	@echo "  make db-recreate       - Drop and recreate database"
	@echo "  make dbms-backup       - Create DBMS backup"
	@echo "  make dbms-restore      - Restore DBMS from backup"
	@echo ""
	@echo "DJANGO:"
	@echo "  make init              - Initialize project"
	@echo "  make startproject      - Create new Django project"
	@echo "  make runserver         - Run Django development server"
	@echo "  make shell             - Access Django shell"
	@echo "  make makemigrations    - Create migrations"
	@echo "  make migrate           - Apply migrations"
	@echo "  make createsuperuser   - Create admin user"
	@echo "  make collectstatic     - Collect static files"
	@echo "  make pytest            - Run tests"
	@echo "  make api-bash          - Open bash shell in API container"
	@echo "  make startapp          - Create Django app(s) (alias for createapp)"
	@echo "  make createapp         - Create standard Django app(s)"
	@echo "  make createpack        - Create Django app(s) as packages"
	@echo "  make createcore        - Create core Django app(s)"
	@echo ""
	@echo "DOCUMENTATION:"
	@echo "  make doc-build         - Build documentation"
	@echo "  make doc-serve         - Serve documentation"
	@echo "  make doc               - Build and serve documentation"
	@echo "  make doc-autogen       - Auto-generate API documentation"
	@echo ""
	@echo "UTILITIES:"
	@echo "  make status            - Show container status"
	@echo "  make stats             - Show container resource usage"
	@echo "  make prune             - Clean unused Docker resources"
	@echo "  make help              - Show this help message"
	@echo ""
	@echo "TARGETS WITH ARGUMENTS:"
	@echo "  make createapp app1 [app2 ...]  - Create multiple apps"
	@echo "  make createpack app1 [app2 ...] - Create multiple package apps"
	@echo "  make createcore app1 [app2 ...] - Create multiple core apps"

# Default target when just 'make' is called
.DEFAULT_GOAL := help

# This allows make to accept targets with arguments like 'make createapp blog'
# and prevents "No rule to make target" errors
%:
	@:

.PHONY: status stats prune help
