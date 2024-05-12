from carmac_tools.file_tools import match_names_to_filenames, list_files_from_dir, unzip, copy_matched_files

# recommend to use exact and 80 min for exact matching
# match_names_to_filenames('dat_retool', 'database_zip_filelist.txt',
#                          'rapidfuzz', 'exact', 80, r'[^a-z0-9]+',
#                          sort=True, verbose=True, output_to_file=True)

# recommended to use partial and 60 minimum for matching not exact names
# match_names_to_filenames('gg_fav.txt', 'matched_list_.txt',
#                          'rapidfuzz', 'partial', 60, r'[^a-z0-9]+',
#                          sort=True, verbose=True, output_to_file=True)


dat_1g1r_filename_path = './dat/dat_retool.txt'      # path to DAT file in txt format with the output from a filtering tool such as ReTool
fav_filename_path = './dat/fav.txt'
dat_romset_folder_path = './full_romset'    # path to full romset
compression = 'zip'     # full romset files compression, default is zip, choices zip, 7z or None
# compression = None
rom_rebuild_folder_path = './rom_rebuild'   # path to rom rebuilding

# phase 1 - match selected roms from filtered dat_file and copy from full_romset to rom_rebuild location
print(f'Phase 1 - match selected roms from {dat_1g1r_filename_path} and copy from {dat_romset_folder_path} to {rom_rebuild_folder_path} location')
filename_list_file = "romset_file_list"
list_files_from_dir(source=dat_romset_folder_path, filename=filename_list_file, output='txt', recursive=False)
match_names_to_filenames(name_list_file=dat_1g1r_filename_path, filename_list_file=f'{filename_list_file}.txt',
                         library='rapidfuzz', match_method='exact',
                         similarity_threshold=80, normalization_pattern=r'[^a-z0-9]+', sort=True, verbose=True, output_to_file=True)
copy_matched_files(filename_matched_list='matched_list.txt', source=dat_romset_folder_path, destination=rom_rebuild_folder_path,
                   enforce_extension=False, extension=None)

# phase 2 - extract roms from rom_rebuild location
print(f'Phase 2 - extract roms from {rom_rebuild_folder_path} location')
if compression == 'zip':
    unzip(source=rom_rebuild_folder_path, destination=f'{rom_rebuild_folder_path}/extract/', separate_dirs=False)
    rom_rebuild_folder_path = f'{rom_rebuild_folder_path}/extract'     # points to extracted folder

# phase 3 - match selected roms from favourite txt file and copy from rom_rebuild location to favourite location
print(f'phase 3 - match selected roms from {fav_filename_path} and copy from {rom_rebuild_folder_path} to {rom_rebuild_folder_path}/fav/ location')
rom_rebuild_filename_list_file = "1g1r_file_list"
list_files_from_dir(source=rom_rebuild_folder_path, filename=rom_rebuild_filename_list_file, output='txt', recursive=False)
match_names_to_filenames(name_list_file=fav_filename_path, filename_list_file=f'{rom_rebuild_filename_list_file}.txt',
                         library='rapidfuzz', match_method='partial',
                         similarity_threshold=60, normalization_pattern=r'[^a-z0-9]+', sort=True, verbose=True, output_to_file=True)
copy_matched_files(filename_matched_list='matched_list.txt', source=rom_rebuild_folder_path, destination=f'{rom_rebuild_folder_path}/fav/',
                   enforce_extension=False, extension=None)
