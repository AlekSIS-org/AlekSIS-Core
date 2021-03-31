#!/bin/sh
#-
# Startup/entrypoint script for deployments based on Docker, vanilla or K8s
#
# Designed to be used in Kubernetes in a way such that this container is used
# in four places:
#
#  1. The app pod(s), setting PREPARE = 0
#  2. The celery-worker pod(s), setting PREPARE = 0 and RUN_MODE = celery-worker
#  3. One celery-beat pod, setting PREPARE = 0 and RUN_MODE = celery-beat
#  4. A post-deploy job, setting RUN_MODE = prepare
#
# To run as stand-alone Docker container, bundling all components, set
# ALEKSIS_dev__uwsgi__celery = true.

# Run mode to start container in
#
#  uwsgi       - application server
#  celery-$foo - celery commands (e.g. worker or beat)
#  *           - Anything else to run arguments verbatim
RUN_MODE=${RUN_MODE:-uwsgi}

# HTTP port to let uWSGI bind to
HTTP_PORT=${HTTP_PORT:-8000}

# Run preparation steps before real command
PREPARE=${PREPARE:-1}

wait_migrations() {
	# Wait for migrations to be applied from elsewhere, e.g. a K8s job
	echo -n "Waiting for migrations to appear"
	until aleksis-admin migrate --check >/dev/null 2>&1; do
		sleep 0.5
		echo -n .
	done
	echo
}

wait_database() {
	# Wait for database to be reachable
	echo -n "Waiting for database."
	until aleksis-admin dbshell -- -c "SELECT 1" >/dev/null 2>&1; do
		sleep 0.5
		echo -n .
	done
	echo
}

prepare_database() {
	# Migrate database; should only be run in app container or job
	aleksis-admin migrate
	aleksis-admin createinitialrevisions
}

# Wait for database to be reachable under all conditions
wait_database

case "$RUN_MODE" in
uwsgi)
	# uWSGI app server mode

	if [ $PREPARE = 1 ]; then
		# Responsible for running migratiosn and preparing staticfiles
		prepare_database
	else
		# Wait for migrations to be applied elsewhere
		wait_migrations
	fi

	exec aleksis-admin runuwsgi -- --http-socket=:$HTTP_PORT
	;;
celery-*)
	# Celery command mode

	if [ $PREPARE = 1 ]; then
		# Responsible for running migrations
		prepare_database
	else
		# Wait for migrations to be applied elsewhere
		wait_migrations
	fi

	exec celery -A aleksis.core ${RUN_MODE#celery-}
	;;
prepare)
	# Preparation only mode
	prepare_database
	;;
*)
	# Run arguments as command verbatim
	exec "$@"
	;;
esac
