import zipfile
import csv
import re
from rapidfuzz import fuzz
from thefuzz import fuzz as tfuzz
import difflib
from pathlib import Path
import os
from typing import Optional, List, Dict, Tuple
import subprocess

from .config import get_global_logger
logger = get_global_logger()


def unzip(source: str, destination: str, separate_dirs: bool = True) -> None:
    """
    Unzips all ZIP files located in the `source` folder into the `destination` folder.
    If `separate_dirs` is True, each ZIP file is extracted to a separate subfolder named after the ZIP file.

    :param source: Path to the folder containing ZIP files.
    :type source: str
    :param destination: Path where the contents should be extracted.
    :type destination: str
    :param separate_dirs: If True, extract ZIPs into separate subdirectories.
    :type separate_dirs: bool
    """
    try:
        # Ensure the source directory exists
        if not os.path.exists(source):
            print(f"The source directory {source} does not exist.")
            return

        # Ensure the destination directory exists
        os.makedirs(destination, exist_ok=True)

        # List all files in the source directory
        for filename in os.listdir(source):
            file_path = os.path.join(source, filename)
            # Check if the file is a ZIP file
            if zipfile.is_zipfile(file_path):
                if separate_dirs:
                    # Path for the subdirectory
                    subfolder_path = os.path.join(destination, os.path.splitext(filename)[0])
                    # Create a subdirectory named after the ZIP file (without extension)
                    os.makedirs(subfolder_path, exist_ok=True)
                    extract_path = subfolder_path
                else:
                    extract_path = destination

                # Open and extract the ZIP file into the specified path
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Extracted '{filename}' ----> {extract_path}")
            else:
                print(f"Skipped '{filename}', not a ZIP file.")

    except Exception as e:
        print(f"An error occurred: {e}")


def list_files_from_dir(source: str, filename: str = 'file_list', output: str = 'txt', recursive: bool = False) -> None:
    """
    Lists files in the specified source directory and writes the list to a file in either text or CSV format.
    Allows for both non-recursive and recursive listing of files.

    :param source: Path to the directory containing files to be listed.
    :type source: str
    :param filename: Base filename for the output file where the list will be stored, without extension.
    :type filename: str
    :param output: Output file format, supports 'txt' or 'csv'. Default is 'txt'.
    :type output: str
    :param recursive: If True, includes files in subdirectories recursively. Default is False.
    :type recursive: bool
    :raises FileNotFoundError: If the source directory does not exist.
    :raises ValueError: If the output format is not supported.
    """

    if not os.path.exists(source):
        raise FileNotFoundError(f"The source directory {source} does not exist.")

    if output not in ['txt', 'csv']:
        raise ValueError("Output format should be 'txt' or 'csv'.")

    file_paths = []
    filename += '.txt' if output == 'txt' else '.csv'

    if recursive:
        # Recursive listing with full relative paths
        for root, _, files in os.walk(source):
            for file in files:
                if not file.startswith('.'):  # Ignore hidden files
                    file_path = os.path.relpath(os.path.join(root, file), start=source)
                    file_paths.append(file_path)
    else:
        # Non-recursive listing, only filenames directly in the source folder
        for file in os.listdir(source):
            if not file.startswith('.') and os.path.isfile(os.path.join(source, file)):  # Ignore hidden files and ensure it's a file
                file_paths.append(file)  # Append only filename

    try:
        if output == 'txt':
            # Write file paths to a plain text file
            with open(filename, 'w', encoding='utf-8') as file:
                file.writelines(f"{path}\n" for path in file_paths)
                # for path in file_paths:
                #     file.write(path + '\n')
        elif output == 'csv':
            # Write file paths to a CSV file using a safer delimiter
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                csv.writer(file, delimiter='|', quoting=csv.QUOTE_MINIMAL).writerows([path] for path in file_paths)
                # for path in file_paths:
                #     writer.writerow([path])
    except IOError as e:
        logger.error(f"Failed to write files to {filename}: {e}")
        raise

    # print(f"file '{filename}' has been created with file names from '{source}'.")
    logger.info(f"{output.upper()} file '{filename}' has been created with file names from '{source}'.")


def remove_extension(filename: str) -> str:
    """
    Remove the file extension from a given filename.

    This function extracts the part of the filename before the last period (.), which is typically where the file extension starts.
    If the file name starts with a period (.) and does not have any other periods, or does not have a period, the original filename is returned.

    :param filename: The complete filename from which to remove the extension.
    :type filename: str
    :return: The filename stripped of its extension.
    :rtype: str

    Examples:
        remove_extension("example.txt")
        'example'
        remove_extension("archive.tar.gz")
        'archive.tar'
        remove_extension(".hidden_file")
        '.hidden_file'
        remove_extension("no_extension")
        'no_extension'
    """
    return Path(filename).stem


def is_valid_filename(filename: str, os_type: str = 'windows') -> bool:
    """
    Check if the provided filename is valid based on the specified operating system type.

    The function checks for characters that are not allowed in filenames for 'windows' and 'unix'.
    For 'windows', it checks for the presence of characters such as \\/:*?"<>| which are not allowed.
    For 'unix', it checks for the presence of / or null characters (\x00), which are not allowed.

    :param filename: The filename to validate.
    :type filename: str
    :param os_type: The type of operating system ('windows' or 'unix'). Default is 'windows'.
    :type os_type: str
    :return: True if the filename is valid for the given OS type, otherwise False.
    :rtype: bool

    Examples:
        is_valid_filename("example.txt", "windows")
        True
        is_valid_filename("example<>.txt", "windows")
        False
        is_valid_filename("example.txt", "unix")
        True
        is_valid_filename("example.txt\\0", "unix")
        False
    """
    if os_type == 'windows' and re.search(pattern=r'[\\/*?:"<>|]', string=filename):
        return False
    if os_type == 'unix' and ('/' in filename or '\x00' in filename):
        return False
    return True


def normalize_string(s: str, filter_pattern: str = r'[^a-z0-9]+') -> str:
    """
    Normalize a string by converting to lowercase and removing characters that do not match the filter pattern.

    :param s: The string to be normalized.
    :param filter_pattern: Regex pattern defining characters to keep. Characters not matching this pattern will be removed.
    :return: The normalized string.
    """
    # 're.sub(pattern, '', s.lower())'
    # replace all characters matching the pattern in the string s (converted to lowercase) with an empty string (''), effectively removing characters.
    # return re.sub(r'[^a-z0-9.,]+', '', s.lower())
    return re.sub(pattern=filter_pattern, repl='', string=s.lower())


def string_matching(base_list: List[str], target_list: List[str],
                    library: str, match_method: str, similarity_threshold: float,
                    normalization_pattern: str = r'[^a-z0-9]+', filename_mode: bool = True) -> Tuple[List[Dict[str, str]], List[str]]:
    """
    Perform string matching using specified library and method, and can operate in filename-specific mode.

    :param base_list: List of base strings to match against target_list.
    :param target_list: List of target strings to be matched.
    :param library: Name of the library to use for matching.
    :param match_method: Matching method as defined in the library.
    :param similarity_threshold: Threshold for considering a match as valid.
    :param normalization_pattern: Regex pattern defining characters to keep. Characters not matching this pattern will be removed.
    :param filename_mode: Flag to treat strings as filenames (default True).
    :return: A tuple containing a list of matches (dictionaries with 'name' and 'matched_name') and a list of unmatched strings.
    """

    matched_results = []
    unmatched_names = []

    for base_name in base_list:
        normalized_name = normalize_string(s=base_name, filter_pattern=normalization_pattern)
        # logger.debug(f'Base name: {base_name} - Normalized: {normalized_name}')
        best_match = None
        highest_score = 0

        for target_name in target_list:
            if filename_mode:
                if not is_valid_filename(filename=target_name, os_type="windows"):
                    logger.debug(f"Warning: Filename invalid, contains illegal characters: {target_name}")
                    continue
                # target_name = remove_extension(filename=target_name)
                # logger.debug(f'Target name without extension: {remove_extension(filename=target_name)}')
                normalized_target = normalize_string(s=remove_extension(filename=target_name), filter_pattern=normalization_pattern)
            else:
                normalized_target = normalize_string(s=target_name, filter_pattern=normalization_pattern)

            # normalized_target = normalize_string(s=target_name, filter_pattern=normalization_pattern)
            score = get_score(library=library, match_method=match_method, normalized_name=normalized_name, normalized_target=normalized_target)
            # logger.debug(f'Target name: {target_name} - Normalized: {normalized_target} - score: {score}')

            if score > highest_score:
                highest_score = score
                if score >= similarity_threshold:
                    best_match = target_name

        if best_match:
            matched_results.append({'name': base_name, 'matched_name': best_match})
        else:
            unmatched_names.append(base_name)

    return matched_results, unmatched_names


def get_score(library: str, match_method: str, normalized_name: str, normalized_target: str) -> float:
    """
    Calculate match score between two normalized strings based on the specified library and matching method.

    The function supports multiple libraries ('rapidfuzz', 'thefuzz', 'difflib') and matching methods ('exact', 'partial').

    :param library: The text matching library to use. Options are 'rapidfuzz', 'thefuzz', 'difflib'.
    :type library: str
    :param match_method: The matching method to apply. Options are 'exact' for full ratio or 'partial' for partial ratio.
    :type match_method: str
    :param normalized_name: The first string to compare.
    :type normalized_name: str
    :param normalized_target: The second string to compare.
    :type normalized_target: str
    :return: The matching score as a percentage between 0 and 100.
    :rtype: float
    :raises ValueError: If an unsupported library or matching method is specified.

    Examples:
        get_score('rapidfuzz', 'exact', 'example file', 'example file test')
        66.66666666666666
        get_score('thefuzz', 'partial', 'example', 'sample example')
        100.0
    """
    valid_libraries = ['rapidfuzz', 'thefuzz', 'difflib']
    valid_methods = ['exact', 'partial']

    if library not in valid_libraries:
        raise ValueError(f"Error: Python library '{library}' does not exist. Please select between {', '.join(valid_libraries)}.")
    if match_method not in valid_methods:
        raise ValueError(f"Error: Match method '{match_method}' is not supported. Options are {', '.join(valid_methods)}.")

    if library == 'rapidfuzz':
        if match_method == 'exact':
            return fuzz.ratio(s1=normalized_name, s2=normalized_target)
        else:
            return fuzz.partial_ratio(s1=normalized_name, s2=normalized_target)

    elif library == 'thefuzz':
        if match_method == 'exact':
            return tfuzz.ratio(s1=normalized_name, s2=normalized_target)
        else:
            return tfuzz.partial_ratio(s1=normalized_name, s2=normalized_target)

    elif library == 'difflib':
        matcher = difflib.SequenceMatcher(isjunk=None, a=normalized_name, b=normalized_target, autojunk=False)
        if match_method == 'exact':
            return matcher.ratio() * 100
        else:
            return matcher.quick_ratio() * 100


def match_names_to_filenames(name_list_file: str, filename_list_file: str, library: str = 'rapidfuzz',
                             match_method: str = 'exact', similarity_threshold: float = 80.0,
                             normalization_pattern: str = r'[^a-z0-9]+', sort: bool = True, verbose: bool = True,
                             output_to_file: bool = False) -> Tuple[Optional[List[Dict[str, str]]], Optional[List[str]]]:
    """
    Compares a list of names with a list of filenames to find matches based on a specified matching method and identifies unmatched names.
    The results can be optionally sorted, printed verbosely, and/or output to files.

    :param name_list_file: Path to the file containing the list of names.
    :type name_list_file: str
    :param filename_list_file: Path to the file containing the list of filenames.
    :type filename_list_file: str
    :param library: Library to use for string matching. Defaults to 'rapidfuzz'.
    :type library: str
    :param match_method: Matching method to use ('exact' or 'partial'). Defaults to 'exact'.
    :type match_method: str
    :param similarity_threshold: The minimum similarity percentage to consider a match. Defaults to 80.0.
    :type similarity_threshold: float
    :param normalization_pattern: Regex pattern defining characters to keep. Characters not matching this pattern will be removed.
    :type normalization_pattern: str
    :param sort: Whether to sort the matched results by name. Defaults to True.
    :type sort: bool
    :param verbose: Whether to print the match results to the console. Defaults to True.
    :type verbose: bool
    :param output_to_file: Whether to write the results to files. Defaults to False.
    :type output_to_file: bool
    :return: A tuple containing a list of matched results and a list of unmatched names.
    :rtype: Tuple[Optional[List[Dict[str, str]]], Optional[List[str]]]
    :raises FileNotFoundError: If any input files are not found.
    :raises ValueError: If an invalid library or matching method is provided.

    Example:
        match_names_to_filenames('names.txt', 'filenames.txt', similarity_threshold=85)
        (List of matches, List of unmatched names)
    """
    # Implement file reading with exception handling
    if not os.path.exists(name_list_file) or not os.path.exists(filename_list_file):
        raise FileNotFoundError("One or more input files do not exist.")

    try:
        with open(name_list_file, 'r', encoding='utf-8') as f:
            name_list = [line.strip() for line in f.readlines()]  # line.strip() removes only leading and trailing whitespaces
        with open(filename_list_file, 'r', encoding='utf-8') as f:
            filename_list = [line.strip() for line in f.readlines()]    # line.strip() removes only leading and trailing whitespaces
    except Exception as e:
        raise IOError(f"Error reading files: {e}")

    matched_results, unmatched_results = string_matching(base_list=name_list, target_list=filename_list,
                                                         library=library, match_method=match_method,
                                                         similarity_threshold=similarity_threshold,
                                                         normalization_pattern=normalization_pattern,
                                                         filename_mode=True)

    if sort:
        matched_results.sort(key=lambda x: x['name'])

    if verbose:
        for result in matched_results:
            logger.debug(f"Matched: {result['name']} ---> {result['matched_name']}")
        for name in unmatched_results:
            logger.debug(f"Unmatched: {name}")

    if output_to_file:
        try:
            with open("output_matched.txt", 'w', encoding='utf-8') as file:
                for result in matched_results:
                    file.write(f"{result['name']} -> {result['matched_name']}\n")

            with open("matched_list.txt", 'w', encoding='utf-8') as file:
                for result in matched_results:
                    file.write(f"{result['matched_name']}\n")

            with open("output_unmatched.txt", 'w', encoding='utf-8') as file:
                for name in unmatched_results:
                    file.write(name + '\n')
        except IOError as e:
            raise IOError(f"Error writing output files: {e}")

    return matched_results, unmatched_results


def copy_matched_files(filename_matched_list: str, source: str, destination: str, enforce_extension: bool = False, extension: str = None) -> None:
    """
    Copies each filename listed in a text file from the source to the destination directory using rsync.
    This function uses load_filenames_from_file to load and optionally filter filenames before copying.

    :param filename_matched_list: Path to the text file containing filenames.
    :type filename_matched_list: str
    :param source: Path of the source directory where files are located.
    :type source: str
    :param destination: Path of the destination directory where files should be copied.
    :type destination: str
    :param enforce_extension: Whether to enforce that filenames end with a specific extension.
    :type enforce_extension: bool
    :param extension: File extension to check for if enforce_extension is True.
    :type extension: str
    """

    with open(filename_matched_list, 'r', encoding='utf-8') as f:
        filenames = [line.strip() for line in f.readlines()]  # line.strip() removes only leading and trailing whitespaces

    for filename in filenames:
        if enforce_extension and not filename.endswith(extension):
            logger.warning(f"Skipped {filename}: does not end with {extension}")
            continue

        source_file = os.path.join(source, filename)
        dest_file = os.path.join(destination, filename)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

        if not os.path.exists(source_file):
            logger.error(f"Source file does not exist - {source_file}")
            continue

        try:
            # Execute rsync to copy the file
            subprocess.run(['rsync', '-avh', '--progress', source_file, dest_file], check=True)
            logger.info(f"Successfully copied {source_file} to {dest_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to copy {source_file} to {dest_file}. Error: {e}")
