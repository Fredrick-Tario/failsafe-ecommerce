#!/usr/bin/env bash

services=(auth-service product-service inventory-service order-service payment-service)
ports=(8001 8002 8003 8004 8006)

for i in "${!services[@]}"; do
	service="${services[$i]}"
	port="${ports[$i]}"

	echo "Starting $service on port $port..."

	(
		cd "services/$service" &&
		python -m uvicorn app.main:app \
			--host 127.0.0.1 \
			--port "$port" \
			--reload
	) &
done
