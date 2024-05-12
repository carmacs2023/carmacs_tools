import argparse
from .file_tools import list_files_from_dir, unzip, copy_matched_files, match_names_to_filenames
from .dat_tools import calculate_checksum_dir
import argcomplete


def main():
    banner = r"""
     ██████╗ █████╗ ██████╗ ███╗   ███╗ █████╗  ██████╗███████╗
    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝██╔════╝
    ██║     ███████║██████╔╝██╔████╔██║███████║██║     ███████╗
    ██║     ██╔══██║██╔══██╗██║╚██╔╝██║██╔══██║██║     ╚════██║
    ╚██████╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║╚██████╗███████║
     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝                                             
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        description=banner + "Tools for manipulating files and directories.\n\n" +
        "Author: carmacs\n" +
        "License: MIT License\n" +
        "Date: 2023\n",
        # formatter_class=argparse.RawDescriptionHelpFormatter
        formatter_class=argparse.RawTextHelpFormatter  # Prevents auto-wrapping of command descriptions

    )
    # Create a subparser object
    subparsers = parser.add_subparsers(dest="command", help='Available sub-commands')

    # Subparser for the unzip command
    unzip_parser = subparsers.add_parser('unzip_dir', help='Unzip files from a source directory to a destination.')

    unzip_parser.add_argument('--source', type=str, required=True, help='The source directory containing ZIP files.')
    unzip_parser.add_argument('--destination', type=str, required=True, help='The destination directory to extract files.')
    unzip_parser.add_argument('--separate_dirs', action='store_true', help='Extract files into separate directories.')

    # Subparser for the list_files command
    list_parser = subparsers.add_parser('list_files_from_dir', help='List files in a directory and output to a specified file format.')

    list_parser.add_argument('--source', type=str, required=True, help='The source directory to list files from.')
    list_parser.add_argument('--filename', type=str, default='file_list.txt', help='The output file name where the list will be stored.')
    list_parser.add_argument('--output', type=str, choices=['txt', 'csv'], default='txt', help='The output file format (txt or csv).')
    list_parser.add_argument('--recursive', action='store_true', help='Recursively list files in subdirectories.')

    # Subparser for the match_names_to_filenames command
    rapidfuzz_parser = subparsers.add_parser('match_filenames', help='Find matches between two lists of names and filenames.')

    rapidfuzz_parser.add_argument('--name_list_file', type=str, required=True,
                                  help='Path to the text file containing a list of names to match.')
    rapidfuzz_parser.add_argument('--filename_list_file', type=str, required=True,
                                  help='Path to the text file containing a list of filenames to match against.')
    rapidfuzz_parser.add_argument('--match_method', type=str, choices=['exact', 'partial'], default='partial',
                                  help='Method of matching: exact or partial.')
    rapidfuzz_parser.add_argument('--similarity_threshold', type=float, default=80.0,
                                  help='Minimum similarity percentage required for a match.')
    rapidfuzz_parser.add_argument('--normalization_pattern', type=str, default=r'[^a-z0-9]+',
                                  help='Regex pattern defining characters to keep. Characters not matching this pattern will be removed.')
    rapidfuzz_parser.add_argument('--sort', action='store_true', help='Sort the results alphabetically by name.')
    rapidfuzz_parser.add_argument('--verbose', action='store_true', help='Print verbose output during the process.')
    rapidfuzz_parser.add_argument('--output_to_file', action='store_true', help='Output the best matches to a text file.')

    # Subparser for the copy_matched_files command
    copy_parser = subparsers.add_parser('copy_files_from_list', help='Copy matched files from source to destination.')

    copy_parser.add_argument('--filename_matched_list', type=str, required=True,
                             help='Path to the text file containing filenames to be copied.')
    copy_parser.add_argument('--source', type=str, required=True,
                             help='Source directory where files are located.')
    copy_parser.add_argument('--destination', type=str, required=True,
                             help='Destination directory where files should be copied.')
    copy_parser.add_argument('--enforce_extension', action='store_true',
                             help='Enforce that filenames end with a specific extension.')
    copy_parser.add_argument('--extension', type=str, help='File extension to check for if enforce_extension is true.')

    # Subparser for the calculate_checksum_dir command
    checksum_parser = subparsers.add_parser('calculate_checksum', help='Calculate and verify checksums for ROM files based on a DAT file.')
    checksum_parser.add_argument('--source_dir', type=str, required=True, help='The directory containing the ROM files to verify.')
    checksum_parser.add_argument('--dat_filename', type=str, required=True,
                                 help='The filename of the DAT XML file containing metadata and checksums.')
    checksum_parser.add_argument('--checksum_type', type=str, choices=['crc', 'md5', 'sha1'],
                                 default='sha1', help='Type of checksum to compute.')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.command == 'unzip_dir':
        unzip(source=args.source, destination=args.destination, separate_dirs=args.separate_dirs)

    elif args.command == 'list_files_from_dir':
        list_files_from_dir(source=args.source, filename=args.filename, output=args.output, recursive=args.recursive)

    elif args.command == 'match_filenames':
        match_names_to_filenames(name_list_file=args.name_list_file, filename_list_file=args.filename_list_file,
                                 match_method=args.match_method, similarity_threshold=args.similarity_threshold,
                                 normalization_pattern=args.normalization_pattern, sort=args.sort,
                                 verbose=args.verbose, output_to_file=args.output_to_file)

    elif args.command == 'copy_files_from_list':
        copy_matched_files(
            filename_matched_list=args.filename_matched_list, source=args.source, destination=args.destination,
            enforce_extension=args.enforce_extension, extension=args.extension if args.enforce_extension else None)

    elif args.command == 'calculate_checksum':
        calculate_checksum_dir(source_dir=args.source_dir, dat_filename=args.dat_filename, checksum_type=args.checksum_type)


if __name__ == '__main__':
    main()
