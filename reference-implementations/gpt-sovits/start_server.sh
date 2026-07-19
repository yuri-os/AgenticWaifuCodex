#!/usr/bin/env bash
# Start the GPT-SoVITS api_v2 inference server for the sovits_voice client.
#
# Defaults are the verified setup on this machine (see README §Setup); override
# any of them with environment variables, e.g.:
#   PORT=9881 GSV_REPO=~/AI/GPT-SoVITS ./start_server.sh
#
# Leave this running in its own terminal; then in another:  python -m sovits_voice live
set -euo pipefail

GSV_REPO="${GSV_REPO:-/mnt/6870C6B170C68572/AI/GPT-SoVITS}"
GSV_ENV="${GSV_ENV:-sovits}"                                   # conda env name
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-9880}"
CONFIG="${CONFIG:-GPT_SoVITS/configs/tts_infer.yaml}"

die() { echo "error: $*" >&2; exit 1; }

# --- pre-flight checks ------------------------------------------------------
command -v conda >/dev/null 2>&1 || die "conda not found on PATH."
conda env list | awk '{print $1}' | grep -qx "$GSV_ENV" \
  || die "conda env '$GSV_ENV' not found. Run: conda env list"

[ -d "$GSV_REPO" ] || die "GPT-SoVITS repo not at '$GSV_REPO'. Set GSV_REPO or clone it (see README)."
[ -f "$GSV_REPO/api_v2.py" ] || die "no api_v2.py in '$GSV_REPO' — not a GPT-SoVITS checkout?"
[ -f "$GSV_REPO/$CONFIG" ] || die "tts config '$CONFIG' missing under the repo."

# The default config's v2 weights must be present (repo ships pretrained_models empty).
V2_VITS="$GSV_REPO/GPT_SoVITS/pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"
[ -f "$V2_VITS" ] || die "v2 models missing (e.g. $V2_VITS). Download them — see README §Setup step 3."

# Don't double-start: is something already listening on the port?
if (exec 3<>"/dev/tcp/$HOST/$PORT") 2>/dev/null; then
  exec 3>&- 3<&-
  die "$HOST:$PORT already in use — the server is probably already running."
fi

# --- launch -----------------------------------------------------------------
echo "Starting GPT-SoVITS api_v2  (env=$GSV_ENV  $HOST:$PORT)"
echo "  repo:   $GSV_REPO"
echo "  config: $CONFIG"
echo "  client: python -m sovits_voice health   # in another terminal"
echo
cd "$GSV_REPO"
exec conda run -n "$GSV_ENV" --no-capture-output \
  python api_v2.py -a "$HOST" -p "$PORT" -c "$CONFIG"
