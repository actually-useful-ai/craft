#!/usr/bin/env bash
# Portable, one-shot outside-model consultation for Craft.

set -uo pipefail

DEFAULT_PROVIDER="${ASK_DEFAULT_PROVIDER:-grok}"
MAX_TOKENS="${ASK_MAX_TOKENS:-2048}"
TIMEOUT="${ASK_TIMEOUT:-120}"
OUTPUT_FORMAT=text
MODEL_OVERRIDE=""
EFFORT_OVERRIDE=""
CONFIG_FILE="${CRAFT_ASK_ENV:-${XDG_CONFIG_HOME:-$HOME/.config}/craft/ask.env}"

die() {
  printf 'ask: %s\n' "$1" >&2
  exit "${2:-2}"
}

file_mode() {
  local mode
  mode=$(stat -f '%Lp' "$1" 2>/dev/null || true)
  case "$mode" in
    ''|*[!0-9]*) mode=$(stat -c '%a' "$1" 2>/dev/null || true) ;;
  esac
  case "$mode" in ''|*[!0-9]*) return 1 ;; esac
  printf '%s\n' "$mode"
}

require_private_file() {
  local path="$1" mode
  [ -f "$path" ] || return 1
  mode=$(file_mode "$path") || die "cannot inspect permissions for $path" 3
  case "$mode" in
    400|600) return 0 ;;
    *) die "refusing insecure credential file $path (mode $mode; expected 600 or 400)" 3 ;;
  esac
}

allowed_config_name() {
  case "$1" in
    ASK_GATEWAY_URL|ASK_GATEWAY_KEY|ASK_GATEWAY_KEY_FILE|ASK_DEFAULT_PROVIDER|ASK_MAX_TOKENS|ASK_TIMEOUT|XAI_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY) return 0 ;;
    *) return 1 ;;
  esac
}

load_config() {
  local path="$1" key value
  [ -f "$path" ] || return 0
  require_private_file "$path"
  while IFS='=' read -r key value; do
    allowed_config_name "$key" || continue
    [ -n "$key" ] && [ -z "${!key:-}" ] || continue
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
    export "$key=$value"
  done < "$path"
}

load_config "$CONFIG_FILE"
DEFAULT_PROVIDER="${ASK_DEFAULT_PROVIDER:-$DEFAULT_PROVIDER}"
MAX_TOKENS="${ASK_MAX_TOKENS:-$MAX_TOKENS}"
TIMEOUT="${ASK_TIMEOUT:-$TIMEOUT}"

if [ -z "${ASK_GATEWAY_KEY:-}" ] && [ -n "${ASK_GATEWAY_KEY_FILE:-}" ]; then
  require_private_file "$ASK_GATEWAY_KEY_FILE"
  ASK_GATEWAY_KEY=$(tr -d '\r\n' < "$ASK_GATEWAY_KEY_FILE")
  export ASK_GATEWAY_KEY
fi

route() {
  PROVIDER="" MODEL="" EFFORT="" EFFORT_LABEL="-" DIRECT_URL="" DIRECT_KEY=""
  case "$1" in
    grok|xai)
      PROVIDER=xai; MODEL=grok-4.5
      DIRECT_URL=https://api.x.ai/v1/chat/completions; DIRECT_KEY="${XAI_API_KEY:-}"
      ;;
    anthropic|claude|opus)
      PROVIDER=anthropic; MODEL=claude-opus-5; EFFORT_LABEL=high-default
      DIRECT_URL=https://api.anthropic.com/v1/messages; DIRECT_KEY="${ANTHROPIC_API_KEY:-}"
      ;;
    openai|gpt)
      PROVIDER=openai; MODEL=gpt-5.6-sol; EFFORT=medium; EFFORT_LABEL=medium
      DIRECT_URL=https://api.openai.com/v1/chat/completions; DIRECT_KEY="${OPENAI_API_KEY:-}"
      ;;
    *) die "unknown provider '$1' (supported: grok, anthropic, openai)" ;;
  esac
  [ -n "$MODEL_OVERRIDE" ] && MODEL="$MODEL_OVERRIDE"
  if [ -n "$EFFORT_OVERRIDE" ]; then EFFORT="$EFFORT_OVERRIDE"; EFFORT_LABEL="$EFFORT_OVERRIDE"; fi
}

transport_for_route() {
  if [ -n "${ASK_GATEWAY_URL:-}" ] && [ -n "${ASK_GATEWAY_KEY:-}" ]; then
    printf gateway
  elif [ -n "$DIRECT_KEY" ]; then
    printf direct
  else
    printf unavailable
  fi
}

emit_routes() {
  local alias transport
  for alias in grok anthropic openai; do
    route "$alias"; transport=$(transport_for_route)
    printf '%s\t%s\t%s\t%s\t%s\n' "$alias" "$PROVIDER" "$transport" "$MODEL" "$EFFORT_LABEL"
  done
}

list_routes() {
  if [ "$OUTPUT_FORMAT" = json ]; then
    emit_routes | python3 -c '
import json, sys
routes = []
for line in sys.stdin:
    provider, api_provider, transport, model, effort = line.rstrip("\n").split("\t")
    routes.append({"provider": provider, "api_provider": api_provider, "transport": transport,
                   "model": model, "effort": None if effort == "-" else effort})
print(json.dumps({"routes": routes}))
'
    return
  fi
  printf '%-12s %-14s %-20s %s\n' PROVIDER TRANSPORT MODEL EFFORT
  emit_routes | while IFS="$(printf '\t')" read -r alias api_provider transport model effort; do
    printf '%-12s %-14s %-20s %s\n' "$alias" "$transport" "$model" "$effort"
  done
}

status() {
  local alias transport config_state
  config_state=absent; [ -f "$CONFIG_FILE" ] && config_state=loaded
  printf 'config\t%s\n' "$config_state"
  for alias in grok anthropic openai; do
    route "$alias"; transport=$(transport_for_route)
    printf '%s\t%s\n' "$alias" "$transport"
  done
}

make_payload() {
  local transport="$1" prompt_file="$2"
  python3 - "$PROVIDER" "$MODEL" "$EFFORT" "$MAX_TOKENS" "$transport" "$prompt_file" <<'PY'
import json, sys
provider, model, effort, max_tokens, transport, prompt_file = sys.argv[1:]
with open(prompt_file, encoding="utf-8") as handle:
    prompt = handle.read()
body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
if transport == "gateway":
    body["provider"] = provider
    body["max_tokens"] = int(max_tokens)
    if provider == "openai" and effort:
        body["reasoning_effort"] = effort
    elif effort:
        body["effort"] = effort
elif provider == "anthropic":
    body["max_tokens"] = int(max_tokens)
    if effort:
        body["effort"] = effort
elif provider == "openai":
    body["max_completion_tokens"] = int(max_tokens)
    if effort:
        body["reasoning_effort"] = effort
else:
    body["max_tokens"] = int(max_tokens)
print(json.dumps(body, ensure_ascii=False))
PY
}

classify_http_error() {
  case "$1" in
    401|403) die "authentication rejected (HTTP $1)" 3 ;;
    404) die "provider or model unavailable (HTTP 404)" 4 ;;
    429) die "provider rate limit reached (HTTP 429)" 5 ;;
    5??) die "provider service failed (HTTP $1)" 6 ;;
    *) die "request failed (HTTP $1)" 7 ;;
  esac
}

extract_response() {
  local response_file="$1"
  python3 - "$PROVIDER" "$MODEL" "$OUTPUT_FORMAT" "$response_file" <<'PY'
import json, sys
declared_provider, declared_model, output_format, response_file = sys.argv[1:]
try:
    with open(response_file, encoding="utf-8") as handle:
        data = json.load(handle)
except Exception:
    print("ask: provider returned malformed JSON", file=sys.stderr)
    raise SystemExit(7)
if isinstance(data, dict) and data.get("error"):
    print("ask: provider returned an error", file=sys.stderr)
    raise SystemExit(7)
actual_provider = data.get("provider", declared_provider)
actual_model = data.get("model", declared_model)
content = data.get("content")
if content is None:
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        try:
            content = "".join(x.get("text", "") for x in data["content"] if x.get("type") == "text")
        except (KeyError, TypeError):
            content = ""
if not isinstance(content, str) or not content.strip():
    print("ask: provider returned empty content", file=sys.stderr)
    raise SystemExit(7)
if actual_model != declared_model:
    print(f"ask: model mismatch: requested {declared_model}, received {actual_model}", file=sys.stderr)
    raise SystemExit(7)
usage = data.get("usage", {})
if output_format == "json":
    print(json.dumps({"provider": actual_provider, "model": actual_model, "content": content.strip(), "usage": usage}, ensure_ascii=False))
else:
    print(f"ask: {actual_provider}/{actual_model}", file=sys.stderr)
    print(content.strip())
PY
}

ask_once() {
  local prompt="$1" transport payload prompt_file request_file response_file header_file status curl_status extract_status
  route "$PROVIDER_ALIAS"
  transport=$(transport_for_route)
  [ "$transport" != unavailable ] || die "no configured transport for $PROVIDER_ALIAS" 3
  prompt_file=$(mktemp "${TMPDIR:-/tmp}/craft-ask-prompt.XXXXXX") || die "could not create prompt file" 7
  printf '%s' "$prompt" > "$prompt_file"
  payload=$(make_payload "$transport" "$prompt_file") || die "could not encode request" 7
  request_file=$(mktemp "${TMPDIR:-/tmp}/craft-ask-request.XXXXXX") || die "could not create request file" 7
  response_file=$(mktemp "${TMPDIR:-/tmp}/craft-ask.XXXXXX") || die "could not create response file" 7
  header_file=$(mktemp "${TMPDIR:-/tmp}/craft-ask-headers.XXXXXX") || die "could not create header file" 7
  printf '%s' "$payload" > "$request_file"
  trap 'unlink "$prompt_file" 2>/dev/null || true; unlink "$request_file" 2>/dev/null || true; unlink "$response_file" 2>/dev/null || true; unlink "$header_file" 2>/dev/null || true' EXIT HUP INT TERM

  if [ "$transport" = gateway ]; then
    printf 'X-API-Key: %s\nContent-Type: application/json\n' "$ASK_GATEWAY_KEY" > "$header_file"
    status=$(curl -sS --max-time "$TIMEOUT" -o "$response_file" -w '%{http_code}' \
      "$ASK_GATEWAY_URL" -H "@$header_file" --data-binary "@$request_file")
    curl_status=$?
  elif [ "$PROVIDER" = anthropic ]; then
    printf 'x-api-key: %s\nanthropic-version: 2023-06-01\nContent-Type: application/json\n' "$DIRECT_KEY" > "$header_file"
    status=$(curl -sS --max-time "$TIMEOUT" -o "$response_file" -w '%{http_code}' \
      "$DIRECT_URL" -H "@$header_file" --data-binary "@$request_file")
    curl_status=$?
  else
    printf 'Authorization: Bearer %s\nContent-Type: application/json\n' "$DIRECT_KEY" > "$header_file"
    status=$(curl -sS --max-time "$TIMEOUT" -o "$response_file" -w '%{http_code}' \
      "$DIRECT_URL" -H "@$header_file" --data-binary "@$request_file")
    curl_status=$?
  fi

  [ "$curl_status" -eq 0 ] || die "transport failed before receiving a response" 6
  case "$status" in 2??) ;; *) classify_http_error "$status" ;; esac
  extract_response "$response_file"
  extract_status=$?
  unlink "$prompt_file"
  unlink "$request_file"
  unlink "$response_file"
  unlink "$header_file"
  trap - EXIT HUP INT TERM
  return "$extract_status"
}

usage() {
  cat <<'EOF'
Usage:
  ask.sh [grok|anthropic|openai] QUESTION
  ask.sh [grok|anthropic|openai] -        # read question from stdin
  ask.sh --provider PROVIDER [--model ID] [--effort LEVEL] QUESTION
  ask.sh --list [--json] | --status | --probe PROVIDER

List and status make no inference calls. Probe makes one small paid call.
EOF
}

PROVIDER_ALIAS=""
PROMPT=""
PROBE=""
ACTION=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --provider) [ "$#" -ge 2 ] || die '--provider requires a value'; PROVIDER_ALIAS="$2"; shift 2 ;;
    --model) [ "$#" -ge 2 ] || die '--model requires a value'; MODEL_OVERRIDE="$2"; shift 2 ;;
    --effort) [ "$#" -ge 2 ] || die '--effort requires a value'; EFFORT_OVERRIDE="$2"; shift 2 ;;
    --json) OUTPUT_FORMAT=json; shift ;;
    --list) ACTION=list; shift ;;
    --status) ACTION=status; shift ;;
    --probe) [ "$#" -ge 2 ] || die '--probe requires one provider'; PROBE="$2"; shift 2 ;;
    --health) die '--health was removed because it made many paid calls; use --status or --probe PROVIDER' ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -) PROMPT=-; shift; break ;;
    *)
      if [ -z "$PROVIDER_ALIAS" ]; then
        case "$1" in grok|xai|anthropic|claude|opus|openai|gpt) PROVIDER_ALIAS="$1"; shift; continue ;; esac
      fi
      break
      ;;
  esac
done

case "$ACTION" in
  list) [ "$#" -eq 0 ] || die '--list accepts only --json'; list_routes; exit 0 ;;
  status) [ "$#" -eq 0 ] || die '--status accepts no question'; status; exit 0 ;;
esac

if [ -n "$PROBE" ]; then
  [ "$#" -eq 0 ] || die '--probe accepts exactly one provider'
  PROVIDER_ALIAS="$PROBE"
  PROMPT='Reply with exactly: OK'
else
  PROVIDER_ALIAS="${PROVIDER_ALIAS:-$DEFAULT_PROVIDER}"
  if [ "$PROMPT" = - ]; then
    PROMPT=$(cat)
  elif [ "$#" -gt 0 ]; then
    PROMPT="$*"
  elif [ ! -t 0 ]; then
    PROMPT=$(cat)
  fi
fi

[ -n "$PROMPT" ] || { usage >&2; exit 2; }
ask_once "$PROMPT"
