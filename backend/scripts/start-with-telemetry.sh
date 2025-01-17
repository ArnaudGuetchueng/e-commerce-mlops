#! /usr/bin/env sh

# Script used to start the API with telemetry.
# Made for non-dev environments.
# Warning: do not add --reload argument to uvicorn.
# See https://signoz.io/docs/instrumentation/fastapi/#steps-to-auto-instrument-fastapi-app-for-traces

# Run prestart.sh to create DB
./prestart.sh

echo "Start with telemetry"
exec opentelemetry-instrument --traces_exporter otlp_proto_http --metrics_exporter otlp_proto_http uvicorn app.main:app --host 0.0.0.0 --port 8000