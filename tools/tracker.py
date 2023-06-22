import config
from tools.alias import Alias
from model.aliases import Aliases
from model.tracker import Tracker as Trackers

class Tracker(Alias):
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['tracker'], help=f'Subcommand tracker')

        ap.add_argument('name', help=f'ISIN or alias identifying a security.')
        ap.add_argument('tracker', help=f'Trakcer symbol on yahoo finance.')
        ap.add_argument('--info', default=None, help=f'Tracker symbol on yahoo finance.')
        ap.add_argument('--currency', default=None, help=f'Tracker symbol on yahoo finance.')

        ap.add_argument('--verbose', '-v', action='store_true', default=False, help='Verbose printing.')
        ap.add_argument('--weak-match', action='store_true', default=False, help='Enables weak matching of isin and alias for <name>')

        args = ap.parse_args()

        config.set_config(args)


        names = Aliases().match_name(args.name, args.weak_match)
        if len(names) != 1:
            print('Can not set tracker')
            print('Parameter passed to <name> does not identify a unique ISIN')
            print(f'Possible matches are:')
            self._Alias__print_names(Aliases().match_name(args.name, True))
            return

        isin = next(iter(names))
        Trackers().set_tracker(isin, args.tracker, args.info, args.currency)



    def get_complete_positional_args_options(self, args):
        if len(args) > 1:
            return None

        name = args[-1] if args else ''
        names = Aliases().match_name(name, True)

        if len(names) == 1 and next(iter(names)) == name:
            return None

        return list(names.keys()) + self._Alias__flatten_aliases(names)

    def get_complete_args(self):
        return {
            '--verbose':    (0, [], None),
            '--info':       (1, [], None),
            '--currency':   (1, [], None),
            '--weak-match': (0, [], None),
        }
