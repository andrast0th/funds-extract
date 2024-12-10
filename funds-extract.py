import requests
import pandas as pd
import argparse
import urllib3

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

urllib3.disable_warnings()

def fetch_and_save_funds_data(api_url, max_page, pagesize, proxy, outputFile):
    all_items = []  # To collect all items across pages

    for page in range(1, max_page + 1):

        # Parse the URL to modify its query parameters
        url_parts = list(urlparse(api_url))
        query = parse_qs(url_parts[4])

        # Update the 'page' and 'pagesize' parameters
        query['page'] = [str(page)]
        query['pagesize'] = [str(pagesize)]

        # Rebuild the URL with the new parameters
        url_parts[4] = urlencode(query, doseq=True)
        modified_url = urlunparse(url_parts)

        print(f"Fetching data from: {modified_url}")

        # Make the GET request

        proxies = {}
        if proxy is not None:
            print("Using HTTP Proxy...")
            proxies = {
                "http": proxy,
                "https": proxy,
                "ftp": None
            }

        response = requests.get(modified_url, verify=False, proxies=proxies)

        # Check if the request was successful
        if response.status_code == 200:

            # Parse the JSON response
            data = response.json()

            # Extract the ITEMS from the response
            items = data.get("FinderV2", {}).get("ITEMS", [])
            if not items:
                items = data.get("FinderV1", {}).get("ITEMS", [])

            # Add items to the collection if any
            if items:
                all_items.extend(items)

            else:
                print(f"No items found on page {page}.")

        else:
            print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")

    # If there are any items collected, create a DataFrame and export it to Excel

    if all_items:
        df = pd.DataFrame(all_items)

        # Export to Excel
        file_path = outputFile
        df.to_excel(file_path, index=False)
        print(f"Excel file created successfully with data from pages 1 to {max_page} at: {file_path}")

    else:
        print("No data collected from any of the pages.")


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract funds data from API, write data to Excel file.')
    parser.add_argument("-u", "--url", help="API URL", type=str, required=True)
    parser.add_argument("-ps", "--pagesize", help="Page size.", type=int, required=True)
    parser.add_argument("-maxp", "--maxpage", help="Max page number.", type=int, required=True)
    parser.add_argument("-x", "--proxy", help="HTTP Proxy, ex: http://user:pass@proxy:port", type=str, required=False)
    parser.add_argument("-o", "--output", help="Output file name / path.", type=str, required=False,
                        default="./Funds_Data.xlsx")
    args = parser.parse_args()
    fetch_and_save_funds_data(args.url, args.maxpage, args.pagesize, args.proxy, args.output)
