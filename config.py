VERBOSE = []
DRYRUN  = False
HANDLE_IGNORED = 'ask'

def set_config(args):
    if hasattr(args, 'verbose'):
        VERBOSE          = args.verbose
    if hasattr(args, 'dryrun'):
        DRYRUN           = args.dryrun
        VERBOSE          = True
    if hasattr(args, 'ignore'):
        HANDLE_IGNORED   = args.ignore