class Backup:
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['backup'], help=f'Subcommand backup')

        args = ap.parse_args()


        import os
        import shutil as sh
        from datetime import date
        if os.path.isfile('data.sqlite'):
            sh.copy('data.sqlite', f'data-bak-{date.today()}.sqlite')
            print(f'backed up database as data-bak-{date.today()}.sqlite')

    
    def get_complete_positional_args_options(self, args):
        return None

    def get_complete_args(self):
        return {}
