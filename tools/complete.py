import sys

class Complete:
    def run(self, tools):
        word = sys.argv[-1]

        # sys.argv[2] is always the tool
        if len(sys.argv) <= 3:
            # tool is not yet decided
            if word not in [t for t in tools.keys()]:
                [print(t) for t in tools.keys()]
                return

        if sys.argv[2] not in tools:
            return



        options = tools[sys.argv[2]].get_complete_positional_args_options(sys.argv[3:])
        if options:
            [print(o) for o in options]
            return


        args = tools[sys.argv[2]].get_complete_args()

        # find last argument name in command line
        pos = None
        arg = None
        for i, a in enumerate(sys.argv[::-1]):
            if a in args:
                pos = i
                arg = a
                break

        # completion for this tools argument
        if arg:
            assert(arg in args)

            count, exclude, callback = args[arg] 

            if count is not None and pos < count:
                if callback:
                    [print(c) for c in callback(sys.argv[pos:])]
                return


        # complete all possible arguments for this tool
        ex = []

        for a in sys.argv:
            if a in args:
                count, exclude, callback = args[a]
                ex = ex + exclude + [a]


        [print(n) for n in args.keys() if n not in ex]
