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

    # expose skills to agent
    introduce_entry_to_agent "/opt/ard-tg/skills" "$ARDTG_AGENT_DATAPATH/skills"

    # run
    python3 -m "src.main"
}
main
