import config
from model.aliases import Aliases


class Alias:
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['alias'], help=f'Subcommand alias')

        ap.add_argument('name', nargs='?', default='', help=f'ISIN or alias identifying a security.')

        ap.add_argument('--dividend-cash-isin', help='Sets this parameter\'s string as  for the specified name. The parameter passed to <name> must uniquely identify a security.')
        ap.add_argument('--set', help='Sets this parameter\'s string as alias for the specified name. The parameter passed to <name> must uniquely identify a security.')
        ap.add_argument('--favourite', action='store_true', default=False, help='Marks alias specified in <name> as favourite')
        ap.add_argument('--delete', action='store_true', default=False, help='Deletes aliases matched for <name>')

        ap.add_argument('--verbose', '-v', action='store_true', default=False, help='Verbose printing.')
        ap.add_argument('--weak-match', action='store_true', default=False, help='Enables weak matching of isin and alias for <name>')

        args = ap.parse_args()

        config.set_config(args)

        if args.name == '':
            args.weak_match = True

        names = Aliases().match_name(args.name, args.weak_match)

 
        if args.set:
            if len(names) != 1:
                print('Can not set alias')
                print('Parameter passed to <name> does not identify a unique ISIN')
                print(f'Possible matches are:')
                self.__print_names(names)
                return

            isin = next(iter(names))
            
            alias = Aliases().match_name(args.set, False)
            if alias:
                if next(iter(alias)) != isin:
                    print('Can not set alias')
                    print('Alias specified to --set is already used by different isin:')
                    self.__print_names(alias)
                return

            Aliases().make_alias(isin, args.set)


        elif args.delete:
            delete_many = 'y'
            if len(names) != 1:
                print('Parameter passed to <name> does not identify a unique ISIN')
                print('Deleted aliases will be:')
                self.__print_names(names)
                delete_many = input('Do you want to delete all aliases? (N)o, (y)es, (s)elect')

            for alias in self.__flatten_aliases(names):
                if delete_many == 's':
                    if input('Delete {}: {}? (Y)es, (n)o') == 'n':
                        continue
                Aliases().delete_alias(alias)


        elif args.favourite:
            if len(names) != 1:
                print('Can not make favourite')
                print('Parameter passed to <name> does not identify a unique isin')
                print(f'Possible matches are:')
                print(self.__flatten_aliases(names))
                return

            aliases = names[next(iter(names))]

            if len(aliases) != 1:
                print('Can not make favourite')
                print('Parameter passed to <name> does not identify a unique alias')
                print(f'Possible matches are:')
                print(self.__flatten_aliases(names))
                return

            Aliases().make_favourite(aliases[0])
            
        elif args.dividend_cash_isin:
            if len(names) != 1:
                print('Can not set dividend cash isin')
                print('Parameter passed to <name> does not identify a unique isin')
                print(f'Possible matches are:')
                print(self.__flatten_aliases(names))
                return

            isin_div = Aliases().match_name(args.dividend_cash_isin, args.weak_match)

            if len(isin_div) != 1:
                print('Can not set dividend cash isin')
                print('Parameter passed to <dividend-cash-isin> does not identify a unique isin')
                print(f'Possible matches are:')
                print(self.__flatten_aliases(isin_div))
                return

            Aliases().set_dividend_cash(next(iter(names)), next(iter(isin_div)))


        else:
            self.__print_names(names)



    def __print_names(self, names):
        for isin in sorted(names.keys()):
            print(f'{isin}:   {names[isin][0]}')
            for alias in names[isin][1:]:
                print(f'                {alias}')
    
    def __flatten_aliases(self, names):
        aliases = []
        for isin in names.keys():
            for alias in names[isin]:
                aliases.append(alias)
        return aliases





    def get_complete_positional_args_options(self, args):
        if len(args) > 1:
            return None

        name = args[-1] if args else ''
        names = Aliases().match_name(name, True)

        if len(names) == 1 and next(iter(names)) == name:
            return None

        return list(names.keys()) + self.__flatten_aliases(names)

    def get_complete_args(self):
        return {
            '--verbose':                (0, [], None),
            '--set':                    (1, ['--favourite', '--delete', '--dividend-cash-isin'], None),
            '--favourite':              (1, ['--set', '--delete', '--dividend-cash-isin'], None),
            '--delete':                 (1, ['--set', '--favourite', '--dividend-cash-isin'], None),
            '--dividend-cash-isin':     (1, ['--set', '--favourite', '--delete'], None),
            '--weak-match':             (0, [], None),
        }