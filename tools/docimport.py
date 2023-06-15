
class Docimport:
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['docimport'], help=f'Subcommand docimport')

        ap.add_argument('--verbose', '-v', action='store_true', help='Verbose printing')
        ap.add_argument('--dryrun', action='store_true', help='Do not modify the database, also enables verbose printing')

        ap.add_argument('--input', '-i', default='/home/hakononakani/Downloads', help='Scans this folder and imports all documents from it')
        ap.add_argument('--archive', '-a', default='archive', help='Imported documents are moved to this location')

        ap.add_argument('--ignore', choices=['archive', 'delete', 'ask', 'skip'], default='ask', help='Determines how to handle ignored documents.')

        ap.add_argument('--fix-names', action='store_true', help='Fixes alias names for imported documents.')

        args = ap.parse_args()


        import config
        config.set_config(args)

        import model.docimport
        model.docimport.import_folder(args.input, args.archive)


        if args.fix_names:
            import json
            from model.documents import Documents

            docs = Documents().get()
            for i, row in docs.iterrows():
                isin = row.ISIN
                name = json.loads(row.Content)['SecurityName']['value']

                aliases.make_alias(isin, name)



    
    def get_complete_positional_args_options(self, args):
        return None

    def get_complete_args(self):
        return {
            '--verbose':    (0, [], None), 
            '--dryrun':     (0, [], None), 
            '--input':      (1, [], None), 
            '--archive':    (1, [], None), 
            '--ignore':     (1, [], lambda arg: ['archive', 'delete', 'ask', 'skip']), 
            '--fix-names':  (0, [], None)
        }