import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time


# pip install openpyxl, google

# def fetch_google_results(query, num_results=10):
#     try:
#         search_results = search(query, num=num_results, stop=num_results)
#         return list(search_results)
#     except Exception as e:
#         print("An error occurred:", e)
#         return []
#
#
# def main(query):
#     num_results = 10  # change this if you want different number of results
#     results = fetch_google_results(query, num_results)
#
#     if results:
#         print("\nTop", num_results, "results for:", query)
#         for idx, result in enumerate(results, start=2):
#             print(idx, "-", result)
#     else:
#         print("No results found.")


def get_product_link(query):
    try:
        # The search() function returns a generator, so use next() to get the first result
        product_url = next(search(query, num=1, stop=1))
        # print(product_url)
        return product_url
    except Exception as e:
        print("No result found", e)
        return None


def get_brandName(soup):
    brand_name = soup.find_all('div', class_='cell-content-value')[0]
    brand_name_value = brand_name.get_text().strip()
    return brand_name_value


def get_productName(soup):
    product_name = soup.find('h1', class_='product-heading')
    product_name_value = product_name.get_text().strip()
    return product_name_value



def get_ean_price(soup, url):
    if "getic" in url:
        ean_number_soup = soup.find('div', class_='section-cell product-ean order-4')
        ean_number = ean_number_soup.find('div', {'class': 'cell-content-value'}).text

        currency = soup.find(class_="product-price-currency").text
        value = soup.find(class_="product-price-value").text

        # Concatenate currency and value
        price = currency + value
        return ean_number, price

    # elif "microless" in url:
    #     ean_number = soup.find_all('div', class_='section-cell product-ean order-4')
    #     ean_number = ean_number.find('div', {'class': 'cell-content-value'}).text
    #     return "to do"
    # elif "hubx"
    else:
        return "N/A",'N/A'


if __name__ == "__main__":

    urls = [
        "https://www.getic.com/product/",
        # "https://uae.microless.com",
        # "https://hubx.com",
        # "https://texub.com",
        # "https://gear-up.me"
    ]
    df = pd.read_csv("./TopSKU.csv")
    df_list = []
    print(df)
    for url in urls:
        extract_df = {"EAN/BARCODE": [], "PRICE WITH CURRENCY": [], "PRODUCT_LINK": []}
        for product in df['SKU']:
            # query = f'USW-Pro-24-POE site:https://www.getic.com/'
            query = f'{product} {url}'
            print(query)
            # time.sleep(0.1)
            product_url = get_product_link(query)
            print("product:",  product_url)
            if product_url:
                page = requests.get(product_url)
                soup = BeautifulSoup(page.content, "html.parser")
                ean,price = get_ean_price(soup, product_url)
                if ean is None:
                    extract_df['EAN/BARCODE'].append('N/A')
                    extract_df['PRICE WITH CURRENCY'].append('N/A')
                    extract_df['PRODUCT_LINK'].append('N/A')
                    continue
                print(ean,price)
                extract_df['EAN/BARCODE'].append(ean)
                extract_df['PRICE WITH CURRENCY'].append(price)
                extract_df['PRODUCT_LINK'].append(product_url)
            # else:
            #     for product1 in df['ITEM NAME']:
            #         # query = f'USW-Pro-24-POE site:https://www.getic.com/'
            #         query = f'{product1} {url}'
            #         print(query)
            #         product_url = get_product_link(query)
            #         print("product:" + product_url)
            #         page = requests.get(product_url)
            #         soup = BeautifulSoup(page.content, "html.parser")
            #         ean = get_ean_price(soup, url)

            else:
                extract_df['EAN/BARCODE'].append('N/A')
                extract_df['PRICE WITH CURRENCY'].append('N/A')
                extract_df['PRODUCT_LINK'].append('N/A')

        # globals()[url] = pd.concat([df, pd.DataFrame.from_dict(extract_df)], axis=1)
        concatenated_df = pd.concat([df, pd.DataFrame.from_dict(extract_df)], axis=1, ignore_index=True)

        # Append the concatenated DataFrame to the df_list
        df_list.append(concatenated_df)

    with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
        for df, url in zip(df_list, urls):
            url = url.replace('-', '_')
            site = url.split('/')[2]
            df.to_excel(writer, sheet_name=site, index=True)

    # with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    #     df1.to_excel(writer, sheet_name='Sheet1', index=False)
    #     df2.to_excel(writer, sheet_name='Sheet2', index=False)
    #     df3.to_excel(writer, sheet_name='Sheet3', index=False)
