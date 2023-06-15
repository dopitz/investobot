#/usr/bin/env bash
_investobot_complete()
{
    comp=$(./bot.py complete $(printf " %s" "${COMP_WORDS[@]:1}"))
    local IFS=$'\n'

    CANDIDATES=($(compgen -W "${comp}" -- "${COMP_WORDS[-1]}"))

    # Correctly set our candidates to COMPREPLY
    if [ ${#CANDIDATES[*]} -eq 0 ]; then
        COMPREPLY=()
    else
        COMPREPLY=($(printf '%q\n' "${CANDIDATES[@]}"))
    fi
}

complete -F _investobot_complete ./bot.py