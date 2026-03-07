import os
import csv
import datetime

def get_file_attributes(filepath):
    """
    Returns the Windows file attributes for a given file path.
    """
    try:
        # On Windows, os.stat().st_file_attributes gives the attributes.
        # On other OS, this attribute might not exist.
        if hasattr(os.stat(filepath), 'st_file_attributes'):
            return os.stat(filepath).st_file_attributes
        else:
            return 0 # Default to 0 if not on Windows or attribute not available
    except OSError:
        return 0 # Return 0 if file not found or other OS error

def create_efu_file(startpath, output_file):
    header = ["Filename", "Size", "Date Modified", "Date Created", "Attributes"]

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        efu_writer = csv.writer(csvfile)
        efu_writer.writerow(header)

        for root, _, files in os.walk(startpath):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    stat_info = os.stat(filepath)
                    
                    # Filename: Relative path from startpath
                    relative_filepath = os.path.relpath(filepath, startpath)
                    
                    # Size in bytes
                    size = stat_info.st_size
                    
                    # Date Modified: ISO 8601 format
                    date_modified = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                    
                    # Date Created: ISO 8601 format
                    date_created = datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat()
                    
                    # Attributes
                    attributes = get_file_attributes(filepath)
                    
                    efu_writer.writerow([relative_filepath, size, date_modified, date_created, attributes])
                except FileNotFoundError:
                    # Skip files that might have been deleted during the walk
                    continue
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
                    continue

# Assuming the script is run from the repository root or startpath is explicitly set
# The output file will be in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_efu_path = os.path.join(script_dir, 'file_list.efu')

# Use the repository root as the startpath for listing files
repository_root = "C:\\Users\\takashi\\Documents" # This should be dynamically determined if possible
create_efu_file(repository_root, output_efu_path)
