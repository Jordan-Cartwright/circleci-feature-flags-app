#!/usr/bin/env bash

usage() {
  echo "Usage: $0 IMAGE"
}

log_info() {
  printf "INFO: %s\n" "$*"
}

log_err() {
  printf "ERRO: %s\n" "$*" >&2
}

require_env() {
  local var="$1"
  if [[ -z "${!var:-}" ]]; then
    log_err "Required environment variable '$var' is not set"
    exit 1
  fi
}

deploy_to_render() {
  local image="$1"
  local deploy_url="${RENDER_DEPLOY_HOOK}&imgURL=${image}"

  log_info "Starting Render deploy..."

  local http_status
  local response

  response=$(
    curl --silent --show-error \
      --connect-timeout 10 \
      --max-time 30 \
      --request GET \
      --write-out "\nHTTP_STATUS:%{http_code}\n" \
      "$deploy_url" \
      2>&1
  )

  http_status=$(echo "$response" | sed -n 's/HTTP_STATUS://p')

  if [ "$http_status" -lt 200 ] || [ "$http_status" -ge 300 ]; then
    log_err "Render deployment hook failed (http: ${http_status})"
    echo "$response"
    exit 1
  fi

  log_info "Render deploy hook succeeded"
}

main() {
  if [[ $# -eq 0 ]]; then
    usage
    exit 1
  fi

  require_env "RENDER_DEPLOY_HOOK"

  local image="$1"

  deploy_to_render "${image}"
}

main "$@"
