import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search


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
        print(product_url)
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
        ean_number = soup.find('div', class_='section-cell product-ean order-4')
        ean_number = ean_number.find('div', {'class': 'cell-content-value'}).text

        # currency = soup.find_all('span', class_="product-price-currency")[0]
        # currency_symbol = currency.get_text().strip()
        # amount = soup.find_all('span', class_="product-price-value")[0]
        # amount_value = amount.get_text().strip()
        # price = currency_symbol + ' ' + amount_value
        price= "$ 150"
        return ean_number, price
    elif "microless" in url:
        ean_number = soup.find_all('div', class_='section-cell product-ean order-4')
        ean_number = ean_number.find('div', {'class': 'cell-content-value'}).text
        return "to do"
    # elif "hubx"


if __name__ == "__main__":

    urls = [
        "https://getic.com",
        # "https://uae.geticmicroless.com",
        # "https://hubx.com",
        # "https://texub.com",
        # "https://gear-up.me"
    ]
    df = pd.read_csv("product.csv")
    df_list = []
    for url in urls:
        extract_df = {"EAN/BARCODE": [], "PRICE WITH CURRENCY": [], "PRODUCT_LINK": []}
        for product in df['SKU']:
            # query = f'USW-Pro-24-POE site:https://www.getic.com/'
            query = f'{product} site:{url}'
            product_url = get_product_link(query)
            if product_url:
                page = requests.get(product_url)
                soup = BeautifulSoup(page.content, "html.parser")
                ean, price = get_ean_price(soup, url)
                extract_df['EAN/BARCODE'].append(ean)
                extract_df['PRICE WITH CURRENCY'].append(price)
                extract_df['PRODUCT_LINK'].append(product_url)
            else:
                extract_df['EAN/BARCODE'].append('N/A')
                extract_df['PRICE WITH CURRENCY'].append('N/A')
                extract_df['PRODUCT_LINK'].append('N/A')

        # globals()[site] = pd.concat([df, pd.DataFrame.from_dict(extract_df)], axis=1)
        df_list.append(pd.concat([df, pd.DataFrame.from_dict(extract_df)]))

    with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
        for df, sheet_name in zip(df_list, urls):
            url = url.replace('-', '_')
            site = url.split('/')[2]
            df.to_excel(writer, sheet_name=site, index=False)

    # with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    #     df1.to_excel(writer, sheet_name='Sheet1', index=False)
    #     df2.to_excel(writer, sheet_name='Sheet2', index=False)
    #     df3.to_excel(writer, sheet_name='Sheet3', index=False)
