from datetime import datetime
import os
import time
import pandas as pd
import shutil
import json
import requests

# Any logging activities inside functions should use this global logger.
from .config import get_global_logger
logger = get_global_logger()

# region dataframes methods


def write_dataframe_to_file(df: pd.DataFrame, filepath: str, **kwargs):
    # keyword arguments
    # index = True for having a rolling counter index
    # vcs = version control

    logger.debug(f'Start write_dataframe_to_file')

    filetype = os.path.splitext(filepath)[1][1:]
    filepath = os.path.splitext(filepath)[0]
    path = os.path.join(os.getcwd(), os.path.dirname(filepath))
    logger.debug(f'filename : {filepath}, filetype : {filetype}, path : {path}')

    # Check if create_dir argument is passed to create directory if it does not exist
    if 'create_dir' not in kwargs.keys():
        kwargs['create_dir'] = False
    elif not isinstance(kwargs['create_dir'], bool):
        print('Warning : kwargs "create_dir" is not a boolean')
        kwargs['create_dir'] = False
    logger.debug(f'create_dir : {kwargs["create_dir"]}')

    if kwargs['create_dir']:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f'creating {path}...')

    # Check absolute path exist
    isdir = os.path.isdir(path)
    logger.debug(f'isdir : {isdir}')

    # check type is a dataframe
    isdf = isinstance(df, pd.DataFrame)
    logger.debug(f'isdf : {isdf}')

    # Check if index argument is passed to save index colum
    if 'index' not in kwargs.keys():
        kwargs['index'] = False
    elif not isinstance(kwargs['index'], bool):
        print('Warning : kwargs "index" is not a boolean')
        kwargs['index'] = False
    logger.debug(f'index : {kwargs["index"]}')

    # Check if vcs argument is passed to use version control
    if 'vcs' not in kwargs.keys():
        kwargs['vcs'] = False
    elif not isinstance(kwargs['vcs'], bool):
        print('Warning : kwargs "vcs" is not a boolean')
        kwargs['vcs'] = False
    logger.debug(f'vcs : {kwargs["vcs"]}')

    # Check filetype is of corret type
    if filetype == 'feather' or filetype == 'csv' or filetype == 'parquet' or filetype == 'json':
        if filetype == 'feather' and not kwargs['index']:
            filetype_chk = False
            logger.error(f'Error: Feather does not support storing dataframe without index, try with')
        else:
            filetype_chk = True
    else:
        filetype_chk = False
    logger.debug(f'filetype_chk : {filetype_chk}({filetype})')

    if kwargs['vcs']:
        # Version Control System
        # current   : "abs_path"/"filepath"."filetype"
        # prior     : "abs_path"/"filepath"_prior."filetype"
        # filepath  : "filepath"_"datetime"."filetype"
        # abs       : "abs_path"/"filepath"_"datetime"."filetype"

        # Example
        # filepath: data/data_carmac_tools/df                                       # Note: filepath include filename excl. extension.
        # filetype: csv
        # abs_filepath_current      : "abs_path"/data/data/data_carmac_tools/df.csv
        # abs_filepath_prior        : "abs_path"/data/data/data_carmac_tools/df_prior.csv
        # filepath                  : data/data_carmac_tools/df_01-May-2023_17-51.csv
        # abs_filepath              : "abs_path"/data/data/data_carmac_tools/df_01-May-2023_17-51.csv

        # Creation of filepaths at the same time, do NOT modify path creation order
        abs_filepath_current = os.path.join(os.getcwd(), ".".join([filepath, filetype]))
        abs_filepath_prior = os.path.join(os.getcwd(), ".".join(["_".join([filepath, 'prior']), filetype]))
        now_str = datetime.now().strftime("%d-%b-%Y_%H-%M")  # current date and time converted to an equivalent string
        filepath = ".".join(["_".join([filepath, now_str]), filetype])
        abs_filepath = os.path.join(os.getcwd(), filepath)
    else:
        # None is assigned to avoid the warning of local variable might be referenced before assignment
        abs_filepath_current = None
        abs_filepath_prior = None
        filepath = os.path.join(os.getcwd(), ".".join([filepath, filetype]))
        abs_filepath = None

    logger.debug(f'\ncurrent   : {abs_filepath_current}\nprior     : {abs_filepath_prior}\nfilepath  : {filepath}\nabs       : {abs_filepath}')

    if isdir and isdf and filetype_chk:  # if path exists, type is dataframe and filetype is accepted
        if not kwargs['index']:
            df = df.set_index(df.columns[0], drop=True)

        start = time.perf_counter()                                             # start timer

        # Write dataframe to file
        if filetype == 'feather':
            df.to_feather(filepath)                                             # write feather file
        elif filetype == 'csv':
            # df.to_csv(filepath, encoding='utf-8', index=kwargs['index'])      # write csv file
            df.to_csv(filepath, encoding='utf-8')                               # write csv file
        elif filetype == 'parquet':
            df.to_parquet(filepath)                                             # write parquet file
        elif filetype == 'json':
            df.to_json(filepath)                                                # write json file

        stop = time.perf_counter()                                              # stop timer

        elapsed = stop - start                                                  # calculate elapse time

        # Checking Filesize
        file_size = os.path.getsize(filepath) / 1048576
        if file_size >= 1262485504:
            logger.info(f'writing dataframe...\n{filepath}\nTime : {elapsed} s\nFilesize : {file_size / 1262485504} GB\n')
        elif file_size >= 1048576:
            logger.info(f'writing dataframe...\n{filepath}\nTime : {elapsed} s\nFilesize : {file_size / 1048576} MB\n')
        else:
            logger.info(f'writing dataframe...\n{filepath}\nTime : {elapsed} s\nFilesize : {file_size / 1024} KB\n')

        if kwargs['vcs']:

            # Copy the content of source to destination "dest = shutil.copy(source, dest)"
            # shutil works only with absolute paths
            # if dest is a file and already exists then it will replace it with the source, or create new one.
            try:
                shutil.copy(abs_filepath_current, abs_filepath_prior)  # copy old current and renames it to "path_prior.ext"
            except FileNotFoundError:
                logger.warning(f'Warning : {abs_filepath_current}\nFile not found, 1st time running tool...')
            try:
                shutil.copy(abs_filepath, abs_filepath_current)  # copy actual current and renames it to "path_current.ext"
            except FileNotFoundError:
                logger.error(f'Error : {abs_filepath} File not found')

    elif not isdf:
        logger.error(f'object is not of type dataframe \n')
    elif not isdir:
        logger.error(f'relative path {filepath} does not exist\n')
    elif not filetype:
        logger.error(f'filetype {filetype} is not accepted\n')
    logger.info(f'Finish write_dataframe_to_file\n')


def read_dataframe_from_file(filepath):
    logger.info(f'Start read_dataframe_from_file')

    isfile = os.path.isfile(os.path.join(os.getcwd(), filepath))  # checks file absolute path
    filetype = os.path.splitext(filepath)[1][1:]

    # Check filetype is of corret type
    if filetype == 'feather' or filetype == 'csv' or filetype == 'parquet' or filetype == 'json':
        filetype_chk = True
    else:
        filetype_chk = False
    logger.debug(f'filetype_chk : {filetype_chk}({filetype})')

    df = pd.DataFrame()
    if isfile and filetype_chk:

        start = time.perf_counter()

        if filetype == 'feather':
            df = pd.read_feather(filepath)
        elif filetype == 'parquet':
            df = pd.read_parquet(filepath)
        elif filetype == 'json':
            df = pd.read_json(filepath)
        elif filetype == 'csv':
            # option index_col=0 is to use the first column as index without creating a new one.
            # if the dataframe was saved without index first column will be used as index
            # if the dataframe was saved with index, then first column (index) will be used as index
            df = pd.read_csv(filepath, encoding='utf-8', index_col=0)

        stop = time.perf_counter()

        elapsed = stop - start
        logger.info(f'reading dataframe...\n{filepath}\nTime : {elapsed}')

    elif not isfile:
        logger.error(f'relative path {filepath} does not exist\n')
    elif not filetype:
        logger.error(f'filetype {filetype} is not accepted\n')

    logger.info(f'Finish read_dataframe_from_file\n')
    return df


def print_df(dframe: pd.DataFrame):
    # Function to display a full (non-truncated) dataframe
    if isinstance(dframe, pd.DataFrame):
        with pd.option_context('display.max_rows', None,
                               'display.max_columns', None,
                               'display.width', 1000,
                               'display.precision', 3,
                               'display.colheader_justify', 'left'):
            logger.info(f'printing dataframe... \n{dframe}')
    else:
        logger.warning(f'\n object to print is not a dataframe\n')


def multi_level_column_dfchk(df_i):  # To check if a dataframe has multi-level columns
    if isinstance(df_i.columns, pd.MultiIndex):
        logger.debug("The DataFrame has multi-level columns.")
    else:
        logger.debug("The DataFrame has single-level columns.")


def df_search_column_by_string(df: pd.DataFrame, col_name: str, substring_filter: str):
    # Filters the DataFrame to select only the rows where the column "col_name" contains,
    # the "substring_filter" string variable, returning a dataframe with only the filtered rows.

    # if isinstance(dframe.loc[0, col_name], str):
    #     # return dframe[dframe[col_name].str.contains(substring_filter, case=False)]

    if isinstance(df.loc[0, col_name], str):
        mask = df[col_name].str.contains(substring_filter, na=False)
        return df[mask]
    else:
        logger.error(f'dataframe column {col_name} is not of string type')
        return pd.DataFrame()

# endregion

# region response methods


def save_response_to_file(response: requests.models.Response, filepath, **kwargs):
    # This function saves response data from the request to a specific filename and data type.
    # 1 - filepath is relative with filename and extension
    # 2 - data type is determined from the file extension in the filepath

    # The response object returned by the requests module is an instance of the Response class,
    # which contains the server's response to the HTTP request made by the client.
    # It contains information such as the response status code, headers, and content.
    # The content can be of various types, such as bytes, string, or JSON.

    # Note: json type objects are dictionaries in python
    # response.json() method parses the JSON response and returns a dictionary or a list of dictionaries,
    # and it is used to extract JSON data from an HTTP response object returned by the requests' library.

    # Some APIs use only other formats, such as XML, CSV, or plain text.
    # In these cases, response.json() method is not applicable
    # other methods response.text or response.content need to be used to parse and extract the data as a string.

    logger.debug(f'Start saving response to file {filepath}')

    filetype = os.path.splitext(filepath)[1][1:]
    path = os.path.join(os.getcwd(), os.path.dirname(filepath))
    logger.debug(f'filename : {filepath}, filetype : {filetype}, path : {path}')

    # Check if create_dir argument is passed to create directory if it does not exist
    if 'create_dir' not in kwargs.keys():
        kwargs['create_dir'] = False
    elif not isinstance(kwargs['create_dir'], bool):
        print('Warning : kwargs "create_dir" is not a boolean')
        kwargs['create_dir'] = False
    logger.debug(f'create_dir : {kwargs["create_dir"]}')

    if kwargs['create_dir']:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f'creating {path}...')

    # Check absolute path exist
    isdir = os.path.isdir(path)
    logger.debug(f'isdir : {isdir}')

    # Check filetype is of corret type
    if filetype == 'txt' or filetype == 'json' or filetype == 'bin' or filetype == 'xml' or filetype == 'htm' or filetype == 'html':
        filetype_chk = True
    else:
        filetype_chk = False
    logger.info(f'filetype_chk : {filetype_chk}({filetype})')

    if isdir and filetype_chk:  # if path exists and filetype is accepted

        if filetype == "json":
            # json.dumps() returns a JSON formatted string, which can be used to serialize data to a file or send it over a network.
            # It accepts a Python object as input and returns a JSON string
            json_data = json.dumps(response.json(), indent=4)   # Convert the JSON data to a JSON-formatted string
            with open(filepath, "w") as file:                   # Write serialized JSON-formatted string to a text file
                file.write(json_data)

        elif filetype == "bin":
            byte_data = response.content
            with open(filepath, "wb") as file:                  # Write the payload data in raw bytes format to a binary file
                file.write(byte_data)

        else:
            text_data = response.text
            with open(filepath, "w") as file:                   # Write the payload data in String format to a text file
                file.write(text_data)

    elif not isdir:
        logger.error(f'relative path {filepath} does not exist\n')
    elif not filetype:
        logger.error(f'filetype {filetype} is not accepted\n')

    logger.info(f'Finish saving response to file {filepath}\n')


def load_response_from_file(filepath):

    logger.info(f'Start reading response from file {filepath}')

    filetype = os.path.splitext(filepath)[1][1:]
    logger.debug(f'filename : {filepath}, filetype : {filetype}')

    # Check absolute path exist
    isdir = os.path.isdir(os.path.join(os.getcwd(), os.path.dirname(filepath)))
    logger.debug(f'isdir : {isdir}')

    # Check filetype is of corret type
    if filetype == 'txt' or filetype == 'json' or filetype == 'bin':
        filetype_chk = True
    else:
        filetype_chk = False
    logger.info(f'filetype_chk : {filetype_chk}({filetype})')

    data = None
    if isdir and filetype_chk:  # if path exists and filetype is accepted
        if filetype == "json":
            # json.load() method reads a JSON file and deserialize its contents into a Python object,
            # returns a dictionary, list or other appropriate Python object representing the JSON data.
            with open(filepath, "r") as file:
                data = json.load(file)

        elif filetype == "txt":
            with open(filepath, 'r') as file:
                data = file.read()
        elif filetype == "bin":
            with open(filepath, 'rb') as file:
                data = file.read()
    elif not isdir:
        logger.error(f'relative path {filepath} does not exist\n')
    elif not filetype:
        logger.error(f'filetype {filetype} is not accepted\n')

    logger.info(f'Finish reading response from file {filepath}\n')
    return data

# endregion
