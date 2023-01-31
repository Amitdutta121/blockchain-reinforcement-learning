import os

import requests
import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


# start = "blockchair_bitcoin_transactions_20160226.tsv.gz
# end = "blockchair_bitcoin_transactions_20221221.tsv.gz"

# generate urls
urls = []
for i in range(2016, 2023):
    for j in range(1, 13):
        for k in range(1, 32):
            if i == 2022 and j == 12 and k == 22:
                break
            urls.append(f"https://gz.blockchair.com/bitcoin/transactions/blockchair_bitcoin_transactions_{i}{j:02}{k:02}.tsv.gz")


# generate file names

fns = []
for i in range(2016, 2023):
    for j in range(1, 13):
        for k in range(1, 32):
            if i == 2022 and j == 12 and k == 22:
                break
            fns.append(f"blockchair_bitcoin_transactions_{i}{j:02}{k:02}.tsv.gz")


inputs = zip(urls, fns)

def download_url(args):
    t0 = time.time()
    url, fn = args[0], args[1]
    try:
        r = requests.get(url)
        with open(fn, 'wb') as f:
            f.write(r.content)
        return(url, time.time() - t0)
    except Exception as e:
        print('Exception in download_url():', e)


# print(urls)

# exclude already downloaded files
inputs = [i for i in inputs if i[1] not in os.listdir()]
# print(inputs)
#
t0 = time.time()
for i in inputs:
    result = download_url(i)
    print('url:', result[0], 'time:', result[1])
print('Total time:', time.time() - t0)

# def download_parallel(args):
#     cpus = cpu_count()
#     results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
#     for result in results:
#         print('url:', result[0], 'time (s):', result[1])
#

# Download in parallel only 3 files at a time

# def download_files_in_parallel(inputs, n=3):
#     cpus = 4
#     results = ThreadPool(cpus - 1).imap_unordered(download_url, inputs)
#     for result in results:
#         print('url:', result[0], 'time (s):', result[1])
#
#
# download_files_in_parallel(inputs, n=3)
# download_parallel(inputs)
