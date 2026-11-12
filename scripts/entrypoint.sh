#! /bin/sh

##########################
# Introduce all files and subfolder from source to destination
#   Copy docs and run agent
# Arguments:
#   $1 - sourcec folder path
#   $2 - destination folder path
##########################
introduce_entry_to_agent() {
    SRC_FOLDER="$1"
    DST_FOLDER="$2"

    mkdir -p "$DST_FOLDER"

    for src in "$SRC_FOLDER"/*; do

        [ -d "$src" ] || continue

        dst="$DST_FOLDER/${src##*/}"

        if [ -e "$dst" ]; then
            chmod -R u+w "$dst"
            rm -rf "$dst"
        fi

        cp -r "$src" "$dst"
        chmod -R u+w "$dst"
    done
}

##########################
# Entry point
#   Copy docs and run agent
# Arguments:
#   - None
##########################
main() {

    APP_ROOT="/opt/ard-tg"

    # expose skills to agent
    introduce_entry_to_agent "$APP_ROOT/skills" "$ARDTG_AGENT_DATAPATH/skills"

    # run, sources stay in the '$APP_ROOT/src' subfolder (see dockerfile);
    # running the file directly puts that folder on sys.path, which the
    # flat module imports inside main.py rely on
    cd "$APP_ROOT" || exit 1
    exec python3 "$APP_ROOT/src/main.py"
}
main
