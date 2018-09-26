import argparse
import csv
import os
import json


class MdaJsonExport(object):
    def __init__(self):
        pass

    def get_mda_txt(self, filename):
        mda_txt = ''
        if not os.path.exists(filename):
            return ''

        with open(filename, 'r') as fh:
            mda_txt = fh.readlines()

        return mda_txt

    def get_mda_filename(self, mda_dir, cik, filename):
        fn = cik + '_' + os.path.basename(filename).split('.')[0] + '.mda'
        return os.path.join(mda_dir, fn)

    def export(self, index_path, mda_dir, json_dir, json_filename):
        self.json_dir = json_dir
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)

        jsonfile = os.path.join(json_dir, json_filename)

        with open(index_path, 'r') as indexfile_in:
            with open(jsonfile, 'w') as jsonfile_out:
                fieldnames = ("form_type", "company_name", "cik", "date_filed", "filename", "symbol")

                reader = csv.reader(indexfile_in, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
                reader_dic = csv.DictReader(indexfile_in, fieldnames)
                for url_idx, row in enumerate(reader_dic, 1):
                    filename = row["filename"]
                    mda_filename = self.get_mda_filename(mda_dir, row['cik'], filename)
                    mda_txt = self.get_mda_txt(mda_filename)
                    row['mda_txt'] = mda_txt
                    json.dump(row, jsonfile_out)
                    jsonfile_out.write('\n')


def main():
    parser = argparse.ArgumentParser("Combine and export Index and Mda Text to Json")
    parser.add_argument('--index_path', type=str)
    parser.add_argument('--mda_dir', type=str, default='./data/mda')
    parser.add_argument('--json_dir', type=str, default='./data/json')
    parser.add_argument('--json_filename', type=str, default='mda.json')
    args = parser.parse_args()

    index_path = args.index_path

    # Export index meta data and mda text to Json
    mda_export = MdaJsonExport()
    mda_export.export(index_path=index_path,
                      mda_dir=args.mda_dir,
                      json_dir=args.json_dir,
                      json_filename=args.json_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Combine and export Index and Mda Text to Json")
    parser.add_argument('--index_path', type=str)
    parser.add_argument('--mda_dir', type=str, default='./data/mda')
    parser.add_argument('--json_dir', type=str, default='./data/json')
    parser.add_argument('--json_filename', type=str, default='mda.json')
    args = parser.parse_args()

    index_path = args.index_path

    # Export index meta data and mda text to Json
    mda_export = MdaJsonExport()
    mda_export.export(index_path=index_path,
                      mda_dir=args.mda_dir,
                      json_dir=args.json_dir,
                      json_filename=args.json_filename)
