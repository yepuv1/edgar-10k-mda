import argparse
import pandas as pd
import csv


def join_on_key(file1, file2, on_key, col_sep, file1_disp_col, file2_disp_col, output_file):
    print('file1: {0}'.format(file1))
    print('file2: {0}'.format(file2))
    print('on_key: {0}'.format(on_key))
    print('col_sep: {0}'.format(col_sep))
    print('file1_disp_col: {0}'.format(file1_disp_col))
    print('file2_disp_col: {0}'.format(file2_disp_col))
    print('output: {0}'.format(output_file))

    df_file1 = pd.read_csv(file1, header=None)
    file1_num_col = len(df_file1.columns)
    file1_cols = ['col_f1_{0}'.format(x) for x in range(1, file1_num_col + 1)]
    df_file1.columns = file1_cols
    df_file1.fillna(-1, inplace=True)

    df_file2 = pd.read_csv(file2, header=None)
    file2_num_col = len(df_file2.columns)
    file2_cols = ['col_f2_{0}'.format(x) for x in range(1, file2_num_col + 1)]
    df_file2.columns = file2_cols
    df_file2.fillna(-2, inplace=True)

    keys = ['col_f1_{0}'.format(on_key[0]), 'col_f2_{0}'.format(on_key[1])]
    print('keys: {0}'.format(keys))

    # Key columns can be text, but here forcing them to integer
    # may fail so change the type as needed
    df_file1.loc[:, (keys[0])] = df_file1[keys[0]].astype('int64').values
    df_file2.loc[:, (keys[1])] = df_file2[keys[1]].astype('int64').values
    df_file1.sort_values(by=[keys[0]])
    df_file2.sort_values(by=[keys[1]])

    if file1_disp_col:
        file1_disp_columns = ['col_f1_{0}'.format(x) for x in file1_disp_col.split(',')]
    else:
        file1_disp_columns = file1_cols

    if file2_disp_col:
        file2_disp_columns = ['col_f2_{0}'.format(x) for x in file2_disp_col.split(',')]
    else:
        file2_disp_columns = file2_cols

    print(file1_disp_columns)
    print(file2_disp_columns)

    print(df_file1)
    print(df_file2)
    df_joined = pd.merge(df_file1, df_file2, how='inner', left_on=keys[0], right_on=keys[1])
    df_joined = df_joined[file1_disp_columns + file2_disp_columns]
    print(df_joined)
    df_joined.to_csv(output_file, header=False, index=False, quoting=csv.QUOTE_ALL)


def main():
    parser = argparse.ArgumentParser("Join two files on a key")
    parser.add_argument('--file1', type=str)
    parser.add_argument('--file1_key_col_num', type=str)
    parser.add_argument('--file2', type=str)
    parser.add_argument('--file2_key_col_num', type=str)
    parser.add_argument('--col_sep', type=str, default=',')
    parser.add_argument('--file1_disp_col', type=str, default=None)
    parser.add_argument('--file2_disp_col', type=str, default=None)
    parser.add_argument('--output_file', type=str)

    args = parser.parse_args()
    join_on_key(file1=args.file1,
                file2=args.file2,
                on_key=[args.file1_key_col_num, args.file2_key_col_num],
                col_sep=args.col_sep,
                file1_disp_col=args.file1_disp_col,
                file2_disp_col=args.file2_disp_col,
                output_file=args.output_file
                )


if __name__ == "__main__":
    main()