import sys

tools = {
    'import': [
        '--verbose',
        '--dryrun',
        '--input',
        '--archive',
        '--ignored',
    ],
    'alias': [
        '--verbose',
        '--isin',
        '--alias',
        '--new-alias',
        '--strong-match',
    ]
}


def parse_cmd():
    if 'complete' in sys.argv:
        parse_complete()
        exit()

    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('tool', choices=tools.keys(), help=f'Specify the tool as first argument. Accepts {tools.keys()}')

    ap.add_argument('--verbose', '-v', action='store_true', help='Verbose printing')
    ap.add_argument('--dryrun', action='store_true', help='Verbose printing')

    ap.add_argument('--delete', '-d', action='store_true', default=False)

    ##########
    # import #
    ##########
    ap.add_argument('--input', '-i', default='/home/hakononakani/Downloads', help='Scans this folder and imports all documents from it')
    ap.add_argument('--archive', '-a', default='archive', help='Imported documents are moved to this location')

    ap.add_argument('--ignored', choices=['archive', 'delete', 'ask', 'skip'], default='ask', help='Determines how to handle ignored documents.')


    #########
    # alias #
    #########
    ap.add_argument('--isin')
    ap.add_argument('--alias')
    ap.add_argument('--new-alias')
    ap.add_argument('--strong-match', action='store_true', default=False)

    return ap.parse_args()


# auto completion
# ./ing.py [args] <tab><tab>    ----- becomes -----> ./ing.py complete [args]
def parse_complete():

    word = sys.argv[-1]

    # sys.argv[2] is always the tool
    if len(sys.argv) <= 3:
        # tool is not yet decided
        if word not in tools:
            [print(t) for t in tools.keys()]
            exit()

    # tool has been selected
    # complete tool arguments
    tool = sys.argv[2]
    if tool not in tools:
        exit()

    toolargs = tools[tool]




    toolargc = None
    toolarg = None
    for i, a in enumerate(sys.argv[::-1]):
        if a in toolargs:
            toolargc = i
            toolarg = a
            break

    if toolarg:
        from model.aliases import Aliases
        if toolarg == '--isin':
            if toolargc == 0:
                [print(a) for a in Aliases().get_similar_isins('')]
                exit()
            elif toolargc == 1:
                [print(a) for a in Aliases().get_similar_isins(word)]
                exit()

        elif toolarg == '--alias':
            if toolargc == 0:
                [print(a) for a in Aliases().get_similar_aliases('')]
                exit()
            elif toolargc == 1:
                [print(a) for a in Aliases().get_similar_aliases(word)]
                exit()

    [print(a) for a in toolargs if a not in sys.argv]
    
    exit()
