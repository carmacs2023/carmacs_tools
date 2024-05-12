from lxml import etree
from typing import Dict, Optional
import os
import json
from dotenv import load_dotenv
import hashlib
import zlib

# Any logging activities inside functions should use this global logger.
# from .config import get_global_logger
from carmac_tools.config import get_global_logger   # use only when using doctests
logger = get_global_logger()


# region environment

# Load environment variables from .env file
dotenv_path = '/Users/juanan/Library/Mobile Documents/com~apple~CloudDocs/Python/40_Py_Projects/carmacs_tools/dat_tools.env'
# logger.debug(dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

# Access your environment variables as global variables
doctest_dir = os.getenv('DOCTEST_DIR')
test_dir = os.getenv('TEST_DIR')
doctest_output_dir = f'{doctest_dir}dat_tools/tests/'
rom_file_dir = f'{doctest_dir}dat_tools/src/rom_rebuild/'
dat_file_dir = f'{doctest_dir}dat_tools/src/dat/'

rom_file = f'{rom_file_dir}5 in One FunPak (USA).gg'
dat_file = f'{dat_file_dir}dat_short_file.dat'
# endregion


def load_xml_dat_file(file_path: str) -> etree.Element:
    """
    Load and parse an XML DAT file using lxml for enhanced parsing capabilities.

    :param file_path: The path to the XML file.
    :type file_path: str
    :return: The root element of the XML tree.
    :rtype: etree._ElementTree

    Example:
    --------
    >>> root = load_xml_dat_file(dat_file)
    >>> print(type(root))
    <class 'lxml.etree._Element'>
    """
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except IOError as e:
        raise FileNotFoundError(f"The file at {file_path} could not be opened.") from e
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Provided file contains invalid XML.") from e


# def list_games(xml_root: etree.Element) -> List[Dict[str, Optional[str]]]:
#     """
#     List games and their metadata from an XML DAT file parsed by lxml.
#
#     :param xml_root: The root element of the XML tree.
#     :type xml_root: lxml.etree._Element
#     :return: A list of dictionaries, each containing game details and associated ROMs.
#     :rtype: list
#
#     Example:
#     --------
#     >>> root = load_xml_dat_file(get_dat_file_path())
#     >>> games = list_games(root)
#     >>> for game in games:
#     ...     print(game['name'], game['description'])
#     Game1 Description1
#     Game2 Description2
#     """
#     games_list: List[Dict[str, Optional[str]]] = []  # Type hint in a variable annotation
#     header = xml_root.find('header')
#     if header is not None and header.find('name') is not None:
#         game_collection: str = header.find('name').text  # Type hint in a variable annotation
#     else:
#         game_collection = "Unknown"
#
#     for game in xml_root.findall('game'):
#         game_info: Dict[str, Optional[str]] = {
#             'name': game.get('name'),
#             'description': game.find('description').text if game.find('description') is not None else "No description",
#             'roms': [{'name': rom.get('name'), 'size': rom.get('size')} for rom in game.findall('rom')]
#         }
#         games_list.append(game_info)
#
#     return games_list

def parse_dat_to_json(xml_root: etree.Element) -> Dict[str, any]:
    """
    Parse an XML DAT file and convert it to a JSON serializable dictionary.

    :param xml_root: The root element of the XML tree.
    :type xml_root: lxml.etree._Element
    :return: A dictionary formatted for JSON serialization, containing game and header details.
    :rtype: dict

    Example:
    --------
    # >>> root = load_xml_dat_file(get_dat_file_path())
    >>> root = load_xml_dat_file(dat_file)
    >>> dat_json = parse_dat_to_json(root)
    >>> with open(f'{doctest_output_dir}output.json', 'w') as f:
    ...     json.dump(dat_json, f, indent=4)
    """
    header = xml_root.find('header')
    header_info = {
        'name': header.find('name').text if header.find('name') is not None else "Unknown",
        'description': header.find('description').text if header.find('description') is not None else "No description",
        'version': header.find('version').text if header.find('version') is not None else "Unknown",
        'date': header.find('date').text if header.find('date') is not None else "Unknown"
    }

    games_list = []
    for game in xml_root.findall('game'):
        roms = []
        for rom in game.findall('rom'):
            roms.append({
                'rom_name': rom.get('name'),
                'size': rom.get('size'),
                'crc': rom.get('crc', 'Not available'),
                'md5': rom.get('md5', 'Not available'),
                'sha1': rom.get('sha1', 'Not available')
            })

        game_info = {
            'description': game.find('description').text if game.find('description') is not None else "No description",
            'roms': roms
        }
        games_list.append(game_info)

    return {'header': header_info, 'games': games_list}


# This function can then be used to convert an XML file directly to JSON:
def convert_dat_to_json(file_path: str, output_json_path: str) -> None:
    """
    Converts an XML file to a JSON file.

    Reads an XML file from the specified path, converts its structure to JSON format, and writes the resulting JSON to a new file.
    This function provides detailed error handling for common issues such as file not found, read/write errors, and XML parsing errors.

    :param file_path: The path to the XML file that needs to be converted.
    :type file_path: str
    :param output_json_path: The destination path for the JSON file to be saved.
    :type output_json_path: str
    :return: None
    :raises FileNotFoundError: Raised if the XML file does not exist at `file_path`.
    :raises IOError: Raised if there are issues reading from or writing to the file.
    :raises etree.XMLSyntaxError: Raised if the XML file is not well-formed.

    Example usage:
        >>> convert_dat_to_json(dat_file, f'{doctest_output_dir}output.json')
        >>> os.path.exists(f'{doctest_output_dir}output.json')
        True
    """

    try:
        # Parse the XML file using lxml's etree
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Convert the XML tree to a JSON-compatible dictionary format
        dat_json = parse_dat_to_json(root)

        # Open the output file in write mode and dump the JSON data with indentation
        with open(output_json_path, 'w') as json_file:
            json.dump(dat_json, json_file, indent=4)
        logger.info(f"JSON file has been successfully created at {output_json_path}")

    except etree.XMLSyntaxError as e:
        logger.error(f"XML Syntax Error: {str(e)}")
        raise
    except FileNotFoundError:
        logger.error("The specified XML file does not exist.")
        raise
    except IOError as e:
        logger.error(f"File input/output error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise


def calculate_checksum(file_path: str, checksum_type: str = 'sha1') -> Optional[str]:
    """
    Calculates the specified type of checksum (CRC32, MD5, or SHA1) for a given file.

    :param file_path: The path to the file for which to calculate the checksum.
    :type file_path: str
    :param checksum_type: The type of checksum to compute ('crc', 'md5', 'sha1').
    :type checksum_type: str
    :return: The calculated checksum in hexadecimal format, or None if an error occurs.
    :rtype: Optional[str]
    :raises ValueError: If the specified checksum type is not supported.
    :raises FileNotFoundError: If the file does not exist.
    :raises IOError: If there is an error reading the file.

    Example usage:
        >>> calculate_checksum(f'{rom_file}', 'sha1')
        'dc8f5848fede37a914dbf1c104c3efb5a804ccbd'
        >>> calculate_checksum(f'{rom_file}', 'crc')
        'f85a8ce8'
        >>> calculate_checksum(f'{rom_file}', 'md5')
        '4e3dfe079044737f26153615e5155214'
    """
    try:
        with open(file_path, 'rb') as file:
            if checksum_type.lower() == 'crc':
                crc_value = 0
                for chunk in iter(lambda: file.read(4096), b""):
                    crc_value = zlib.crc32(chunk, crc_value)
                # checksum = format(crc_value & 0xFFFFFFFF, '08x')
                # logger.debug(f'crc : {checksum}')
                return format(crc_value & 0xFFFFFFFF, '08x')
            elif checksum_type.lower() == 'md5':
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_md5.update(chunk)
                # logger.debug(f'md5 : {hash_md5.hexdigest()}')
                return hash_md5.hexdigest()
            elif checksum_type.lower() == 'sha1':
                hash_sha1 = hashlib.sha1()
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_sha1.update(chunk)
                # logger.debug(f'sha1 : {hash_sha1.hexdigest()}')
                return hash_sha1.hexdigest()
            else:
                raise ValueError("Unsupported checksum type specified. Choose 'crc', 'md5', or 'sha1'.")

    except FileNotFoundError:
        raise FileNotFoundError("The file does not exist at the specified path.")
    except IOError:
        raise IOError("Failed to read the file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def calculate_checksum_dir(source_dir: str, dat_filename: str, checksum_type: str = 'sha1') -> None:
    """
    Validates checksums for ROM files in a directory against checksums specified in a DAT file.

    This function performs three main steps:
    1. Load the DAT XML file to get its root element.
    2. Parse the DAT XML root into a JSON-like dictionary.
    3. Calculate and compare the SHA1 checksums for each ROM file listed in the DAT against the actual files in the source directory.

    :param source_dir: The directory containing the ROM files to validate.
    :type source_dir: str
    :param dat_filename: The filename of the DAT XML file containing metadata and checksums.
    :type dat_filename: str
    :param checksum_type: The type of checksum to compute ('crc', 'md5', 'sha1').
    :type checksum_type: str

    Example usage:
        >>> calculate_checksum_dir(f'{rom_file_dir}', f'{dat_file}')
    """

    # Step 1: Load the DAT XML file
    dat_path = os.path.join(source_dir, dat_filename)
    xml_root = load_xml_dat_file(dat_path)
    if xml_root is None:
        logger.error("Failed to load the DAT file.")
        return

    # Step 2: Parse the DAT file to JSON
    dat_json = parse_dat_to_json(xml_root)

    # Step 3: Iterate over the JSON to validate checksums
    for game in dat_json["games"]:
        for rom in game["roms"]:
            rom_name = rom["rom_name"]
            expected_checksum = rom[checksum_type]
            file_path = os.path.join(source_dir, rom_name)

            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue

            actual_checksum = calculate_checksum(file_path=file_path, checksum_type=checksum_type)
            if actual_checksum == expected_checksum:
                logger.info(f"Checksum match for {rom_name}")
                logger.debug(f"Expected {expected_checksum}, got {actual_checksum}")
            else:
                logger.info(f"Checksum mismatch for {rom_name}: Expected {expected_checksum}, got {actual_checksum}")
