import concurrent.futures
import requests

from fp.fp import FreeProxy


proxies = ["41.33.47.146:1981", "217.146.217.178:3128", "103.126.87.47:8080"]


urls = []
for i in range(2016, 2023):
    for j in range(1, 13):
        for k in range(1, 32):
            if i == 2022 and j == 12 and k == 22:
                break
            urls.append(f"https://gz.blockchair.com/bitcoin/transactions/blockchair_bitcoin_transactions_{i}{j:02}{k:02}.tsv.gz")


urls = [
    'https://www.example1.com/file1.txt',
    'https://www.example2.com/file2.txt',
    'https://www.example3.com/file3.txt',
]


# change proxies object to a list of proxies

# proxy = {
#     'http': '41.33.47.146:1981',
#     'https': '217.146.217.178:3128'
# }

# def download_file(url):
#     response = requests.get(url, proxies=proxy)
#     filename = url.split("/")[-1]
#     open(filename, "wb").write(response.content)
#     return filename
#
# with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#     results = [executor.submit(download_file, url) for url in urls]
#
#     for f in concurrent.futures.as_completed(results):
#         print(f.result())


proxies = FreeProxy().get()

print(proxies)

# for proxy in proxies:
#     try:
#         proxy_address = "http://" + proxy.host + ":" + proxy.port
#         response = requests.get(url, proxies={'http': proxy_address, 'https': proxy_address})
#         with open("file.txt", "wb") as file:
#             file.write(response.content)
#         print("File downloaded successfully using proxy", proxy)
#         break
#     except requests.exceptions.RequestException as e:
#         print("Error using proxy", proxy, ":", e)