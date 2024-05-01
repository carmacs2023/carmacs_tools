import argparse
from carmac_tools import list_files_to_csv, unzip
import argcomplete


def main():
    parser = argparse.ArgumentParser(description="Tools for manipulating files and directories.")
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for the unzip command
    unzip_parser = subparsers.add_parser('unzip', help='Unzip files from a source directory to a destination.')
    unzip_parser.add_argument('--source', type=str, required=True, help='The source directory containing ZIP files.')
    unzip_parser.add_argument('--destination', type=str, required=True, help='The destination directory to extract files.')
    unzip_parser.add_argument('--separate_dirs', action='store_true', help='Extract files into separate directories.')

    # Subparser for the list_files_to_csv command
    list_parser = subparsers.add_parser('list_files_to_csv', help='List files in a directory to a CSV file.')
    list_parser.add_argument('--source', type=str, required=True, help='The source directory to list files from.')
    list_parser.add_argument('--filename', type=str, default='file_list.csv', help='The output CSV file name.')
    list_parser.add_argument('--recursive', action='store_true', help='Recursively list files in subdirectories.')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.command == 'unzip':
        unzip(args.source, args.destination, args.separate_dirs)
    elif args.command == 'list_files_to_csv':
        list_files_to_csv(args.source, args.filename, args.recursive)


if __name__ == '__main__':
    main()
