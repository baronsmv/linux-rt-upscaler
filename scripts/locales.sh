#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCALE_DIR="$PROJECT_ROOT/src/upscaler/gui/locale"
SRC_DIR="$PROJECT_ROOT/src"
LOCALE_PREFIX="upscale_gui"

PYLUPDATE=""
LRELEASE=""
LINGUIST=""

locate_pylupdate() {
    [[ -n "$PYLUPDATE" ]] && return

    if command -v pylupdate6 >/dev/null 2>&1; then
        PYLUPDATE="pylupdate6"
        PYLUPDATE_MODE="directory"
    elif command -v pyside6-lupdate >/dev/null 2>&1; then
        PYLUPDATE="pyside6-lupdate"
        PYLUPDATE_MODE="files"
        echo "warning: pylupdate6 not found; using pyside6-lupdate." >&2
        echo "         Plural detection may produce false positives." >&2
    else
        echo "error: neither pylupdate6 nor pyside6-lupdate found in PATH" >&2
        exit 1
    fi
}

locate_lrelease() {
    [[ -n "$LRELEASE" ]] && return
    local bin
    for bin in pyside6-lrelease lrelease6 lrelease; do
        if command -v "$bin" >/dev/null 2>&1; then
            LRELEASE="$bin"
            return
        fi
    done
    echo "error: pyside6-lrelease (or lrelease6) not found in PATH" >&2
    exit 1
}

locate_linguist() {
    [[ -n "$LINGUIST" ]] && return
    local bin
    for bin in pyside6-linguist linguist6 linguist; do
        if command -v "$bin" >/dev/null 2>&1; then
            LINGUIST="$bin"
            return
        fi
    done
    echo "error: pyside6-linguist not found in PATH" >&2
    exit 1
}

ts_path()  { printf '%s/%s_%s.ts\n'     "$LOCALE_DIR" "$LOCALE_PREFIX" "$1"; }
qm_path()  { printf '%s/%s_%s.qm\n'     "$LOCALE_DIR" "$LOCALE_PREFIX" "$1"; }
wip_path() { printf '%s/%s_%s.ts.wip\n' "$LOCALE_DIR" "$LOCALE_PREFIX" "$1"; }

list_languages() {
    [[ -d "$LOCALE_DIR" ]] || return 0
    find "$LOCALE_DIR" -maxdepth 1 -type f -name "${LOCALE_PREFIX}_*.ts" \
        | sed -e "s|^.*/${LOCALE_PREFIX}_||" -e 's|\.ts$||' \
        | sort
}

ensure_ts_exists() {
    local lang="$1" file
    file="$(ts_path "$lang")"
    [[ -f "$file" ]] && return
    mkdir -p "$LOCALE_DIR"
    cat > "$file" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="$lang">
<context>
</context>
</TS>
EOF
}

ensure_language_attr() {
    # Guarantee the <TS language="…"> attribute is correct. pylupdate6
    # preserves it, but this defends against a hypothetical clobber.
    local lang="$1" file="$2"
    grep -q "<TS[^>]*language=\"$lang\"" "$file" && return
    python3 - "$file" "$lang" <<'PY'
import re, sys
path, lang = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    src = f.read()
if re.search(r'<TS[^>]*\slanguage="[^"]*"', src):
    src = re.sub(
        r'(<TS[^>]*)\slanguage="[^"]*"',
        lambda m: f'{m.group(1)} language="{lang}"',
        src, count=1,
    )
else:
    src = re.sub(
        r'<TS(\s[^>]*)?>',
        lambda m: f'<TS{m.group(1) or ""} language="{lang}">',
        src, count=1,
    )
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
PY
}

update_language() {
    local lang="$1" file
    file="$(ts_path "$lang")"
    ensure_ts_exists "$lang"
    echo "  → updating $lang"

    case "$PYLUPDATE_MODE" in
        directory)
            "$PYLUPDATE" --no-obsolete --ts "$file" "$SRC_DIR"
            ;;
        files)
            local py_files
            mapfile -d '' py_files < <(find "$SRC_DIR" -type f -name '*.py' -print0)
            if [[ ${#py_files[@]} -eq 0 ]]; then
                echo "error: no .py files found under $SRC_DIR" >&2
                return 1
            fi
            "$PYLUPDATE" -no-obsolete -locations relative "${py_files[@]}" -ts "$file"
            ;;
        *)
            echo "error: unknown PYLUPDATE_MODE '$PYLUPDATE_MODE'" >&2
            return 1
            ;;
    esac

    ensure_language_attr "$lang" "$file"
}

compile_language() {
    local lang="$1" ts qm
    ts="$(ts_path "$lang")"
    qm="$(qm_path "$lang")"
    if [[ ! -f "$ts" ]]; then
        echo "  ! skip $lang (no .ts file)" >&2
        return
    fi
    echo "  → compiling $lang"
    "$LRELEASE" "$ts" -qm "$qm"
}

cmd_update_all() {
    locate_pylupdate
    local languages
    mapfile -t languages < <(list_languages)
    if [[ ${#languages[@]} -eq 0 ]]; then
        echo "error: no .ts files in $LOCALE_DIR" >&2
        echo "       create one with: $0 --new <lang>" >&2
        exit 1
    fi
    echo "Updating ${#languages[@]} language(s)..."
    local lang
    for lang in "${languages[@]}"; do
        update_language "$lang"
    done
    echo "Done."
}

cmd_release() {
    locate_pylupdate
    locate_lrelease
    local languages
    mapfile -t languages < <(list_languages)
    echo "Building release locales..."
    local lang
    for lang in "${languages[@]}"; do
        if [[ -f "$(wip_path "$lang")" ]]; then
            echo "  ! skip $lang (marked WIP)"
            continue
        fi
        update_language "$lang"
        compile_language "$lang"
    done
    echo "Done. .qm files in: $LOCALE_DIR"
    echo "Remember: *.qm should be gitignored."
}

cmd_new_language() {
    local lang="${1:-}"
    [[ -n "$lang" ]] || { echo "usage: $0 --new <lang>" >&2; exit 1; }
    if [[ ! "$lang" =~ ^[A-Za-z][A-Za-z0-9_]*$ ]]; then
        echo "error: '$lang' is not a valid locale tag (e.g., fr, pt_BR)" >&2
        exit 1
    fi
    local file
    file="$(ts_path "$lang")"
    if [[ -f "$file" ]]; then
        echo "error: $file already exists" >&2
        exit 1
    fi
    locate_pylupdate
    ensure_ts_exists "$lang"
    update_language "$lang"
    echo ""
    echo "Created: $file"
    echo ""
    echo "Next steps:"
    echo "  1. Translate:  $0 --edit $lang"
    echo "  2. Check:      $0 --check"
    echo "  3. Commit $file"
    echo ""
    echo "To keep it out of releases until it's complete:"
    echo "  $0 --wip $lang"
}

cmd_check() {
    local file lang total unfinished translated pct suffix found=0
    echo "Translation status:"
    for file in "$LOCALE_DIR/${LOCALE_PREFIX}_"*.ts "$LOCALE_DIR/${LOCALE_PREFIX}_"*.ts.wip; do
        [[ -f "$file" ]] || continue
        found=1
        lang=$(basename "$file" | sed -e "s/^${LOCALE_PREFIX}_//" -e 's/\.ts\(\.wip\)\?$//')
        suffix=""
        [[ "$file" == *.wip ]] && suffix=" [WIP]"
        total=$(grep -c '<message' "$file" 2>/dev/null || true)
        unfinished=$(grep -c 'type="unfinished"' "$file" 2>/dev/null || true)
        translated=$((total - unfinished))
        pct=0
        (( total > 0 )) && pct=$(( translated * 100 / total ))
        printf "  %-10s %4d/%-4d (%3d%%)%s\n" "$lang" "$translated" "$total" "$pct" "$suffix"
    done
    (( found )) || echo "  (no .ts files found in $LOCALE_DIR)"
}

cmd_edit() {
    local lang="${1:-}"
    [[ -n "$lang" ]] || { echo "usage: $0 --edit <lang>" >&2; exit 1; }
    local file
    file="$(ts_path "$lang")"
    [[ -f "$file" ]] || file="$(wip_path "$lang")"
    if [[ ! -f "$file" ]]; then
        echo "error: no .ts file for '$lang'" >&2
        exit 1
    fi
    locate_linguist
    "$LINGUIST" "$file" &
}

cmd_mark_wip() {
    local lang="${1:-}"
    [[ -n "$lang" ]] || { echo "usage: $0 --wip <lang>" >&2; exit 1; }
    local ts wip
    ts="$(ts_path "$lang")"
    wip="$(wip_path "$lang")"
    if [[ ! -f "$ts" ]]; then
        echo "error: $ts not found" >&2
        exit 1
    fi
    if [[ -f "$wip" ]]; then
        echo "error: $wip already exists" >&2
        exit 1
    fi
    mv "$ts" "$wip"
    rm -f "$(qm_path "$lang")"
    echo "Marked $lang as WIP ($wip)"
}

cmd_mark_active() {
    local lang="${1:-}"
    [[ -n "$lang" ]] || { echo "usage: $0 --unwip <lang>" >&2; exit 1; }
    local ts wip
    ts="$(ts_path "$lang")"
    wip="$(wip_path "$lang")"
    if [[ ! -f "$wip" ]]; then
        echo "error: $wip not found" >&2
        exit 1
    fi
    mv "$wip" "$ts"
    echo "Activated $lang ($ts)"
}

usage() {
    cat <<'EOF'
Usage: locales.sh [command]

Commands:
  (no args)          Update all .ts files from source (merges new strings).
  --new <lang>       Create a new language (e.g., fr, pt_BR).
  --edit <lang>      Open pyside6-linguist on the language's .ts file.
  --check            Show translation completion per language.
  --wip <lang>       Mark a language as WIP (excluded from --release).
  --unwip <lang>     Reverse --wip.
  --release          Update + compile .qm files for shipping (skips WIP).
  -h, --help         Show this help.

Paths:
  Locale files:  src/upscaler/gui/locale/
  Scanned source: src/

Files:
  *.ts      — translation source (commit).
  *.ts.wip  — partial translations, excluded from release (commit).
  *.qm      — compiled binaries (regenerate on release, gitignore).
EOF
}

case "${1:-}" in
    ""|--update)     cmd_update_all ;;
    --release)       cmd_release ;;
    --new)           cmd_new_language "${2:-}" ;;
    --check)         cmd_check ;;
    --edit)          cmd_edit "${2:-}" ;;
    --wip)           cmd_mark_wip "${2:-}" ;;
    --unwip)         cmd_mark_active "${2:-}" ;;
    -h|--help|help)  usage ;;
    *)
        echo "unknown command: $1" >&2
        echo "" >&2
        usage >&2
        exit 1
        ;;
esac