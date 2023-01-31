import os
import requests
import time


# Look into the /blockchaindata/tranactions folder and find the missing files from 2016 to 2022
# and download them
def missingPart():
    # generate urls
    urls = []
    for i in range(2016, 2023):
        for j in range(1, 13):
            for k in range(1, 32):
                if i == 2023 and j == 1 and k == 27:
                    break
                urls.append(f"http://blockdata.loyce.club/transactions/blockchair_bitcoin_transactions_{i}{j:02}{k:02}.tsv.gz")

    # generate file names
    fns = []
    for i in range(2016, 2023):
        for j in range(1, 13):
            for k in range(1, 32):
                if i == 2022 and j == 12 and k == 22:
                    break
                fns.append(f"/content/drive/MyDrive/blockchaindata/transaction_dump/blockchair_bitcoin_transactions_{i}{j:02}{k:02}.tsv.gz")

    # exclude already downloaded files
    inputs = [i for i in zip(urls, fns) if "/content/drive/MyDrive/blockchaindata/transaction_dump/"+i[1] not in os.listdir("/content/drive/MyDrive/blockchaindata/transaction_dump")]

    return inputs


# convert file urls to human-readable dates in new line

# format date string  to DD-MM-YYYY
def formatDate(date):
    return date[6:8] + '-' + date[4:6] + '-' + date[0:4]

def convertToDates(inputs):
    dates = []
    for i in inputs:
        dates.append( formatDate(i[1].split('_')[3].split('.')[0]))
    return dates


# print_list after every month end print ------------ to separate months
def print_list(l):
    for i in range(len(l)):
        if i % 31 == 0:
            print('============================')
        print(l[i])

# print_list(convertToDates(missingPart()))
# print(len(missingPart()))

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
#
# t0 = time.time()
# for i in missingPart():
#     result = download_url(i)
#     print('url:', result[0], 'time:', result[1])
# print('Total time:', time.time() - t0)


print(missingPart())