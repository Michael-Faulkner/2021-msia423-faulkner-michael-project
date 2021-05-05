import requests
import zipfile
import gzip
import json
import shutil
import ast


def download(url, gzip_save_path, unzipped_save_path, json_save_path):

    r = requests.get(url)
    gzip = r.content

    json_string = ''
    shutil.copyfileobj(gzip, json_string)

    with open(gzip_save_path, "wb") as f:
        r = requests.get(url)
        f.write(r.content)

    with gzip.open(gzip_save_path, 'rb') as f_in:
        with open(unzipped_save_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    with open(unzipped_save_path) as f:
        lines = f.readlines()

    chunks = len(lines) // 5000 + 1
    data_dict = []
    for i in range(chunks):
        start_index = 0 + i * 5000
        end_index = 5000 + i * 5000
        current_chunk = '[' + ",".join(lines[start_index:end_index]) + ']'
        data_dict = data_dict + ast.literal_eval(current_chunk)

    with open(json_save_path, 'w') as json_file:
        json.dump(data_dict, json_file)