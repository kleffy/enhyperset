import ftplib
import csv
import os
import pandas as pd
from tqdm import tqdm  

def sync_download_ftps_files(download_save_path, files, ftps_server, username, password, csv_save_path):
    skipped_files = []
    downloaded_files = []
    # connect to the ftps server
    ftps = ftplib.FTP_TLS()
    ftps.connect(ftps_server)
    ftps.login(user=username, passwd=password)
    ftps.prot_p()
    # download the files one by one
    with tqdm(total=len(files)) as pbar:
        for file in files:
            if file not in downloaded_files:
                try:
                    with open(os.path.join(download_save_path, file), 'wb') as local_file:
                        ftps.retrbinary('RETR ' + file, local_file.write)
                        pbar.update()
                        downloaded_files.append(file)
                except Exception as e:
                    file_link = f'ftps://{username}@{ftps_server}/{file}'
                    skipped_files.append(file_link)
    ftps.quit()
    if skipped_files:
        columns = ['links']
        csv_file_name = 'skipped_files.csv'
        save_to_csv(csv_save_path, skipped_files, columns, csv_file_name)

def extract_info_from_link(ftps_links_path, extracted_links_save_path=None):
    link_info = []
    with open(ftps_links_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header
        for row in reader:
            link = row[0]
            server = link.split('@')[1].split('/')[0]
            username = link.split('//')[1].split('@')[0]
            file_name = link.split('//')[-1]
            link_info.append((username, server, file_name))
        
    if extracted_links_save_path:
        columns = ['username', 'server', 'file_name']
        csv_file_name = 'extracted_links_info.csv'
        save_to_csv(extracted_links_save_path, link_info, columns, csv_file_name)

    return link_info

def save_to_csv(save_path, items, columns, csv_file_name):
    items_df = pd.DataFrame(items, columns=columns)
    items_df.to_csv(os.path.join(save_path, csv_file_name), index=False)

if __name__ == '__main__':
    # Placeholder paths for external use
    csv_save_path = r'<your/csv/save/path>'
    download_save_path = r'<your/download/save/path>'
    ftps_links_path = r'<path/to/ftps_links.csv>'
    extracted_links_save_path = r'<path/to/save/extracted_links_info>' 

    # Extract links information
    links_info = extract_info_from_link(ftps_links_path=ftps_links_path, extracted_links_save_path=extracted_links_save_path)

    username = links_info[0][0]
    password = 'your_password_here'  # Replace with appropriate password logic
    server = links_info[0][1]
    file_names = [link[2] for link in links_info]
    print(f'{username} @ {server}')
    
    # Start file download
    sync_download_ftps_files(download_save_path, file_names, server, username, password, csv_save_path)
    print('Download completed successfully!')
