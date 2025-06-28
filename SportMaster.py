# Спортмастер оказался шляпой и требовал кукис, что и впендюрили.
# Также не пускал поскрапить по ХТМЛ, нашел конечную точку АПИ которая выдавала джсон продукта
# В итоге по хтмл собрали ИД продукта, и через функцию просканили каждый товар и отфильтровали нужные данные

import httpx
import time
import json
from selectolax.parser import HTMLParser

headers = {
    "User-Agent": "***",
}
cookes = {
    "***",
}

# Получаем данные из джсонов, фильтруем и записываем в свой
def get_json_data():
    api = "https://www.sportmaster.ru/ga-api/v1/products/"
    with open("KrossIds.json", "r", encoding="utf-8") as f:
        ids = json.load(f)
    krossData = []
    for i in ids:
        resp = httpx.get(api + i, headers=headers, cookies=cookes)
        raw = resp.json()
        filtered = {
            "Id": raw.get("productId"),
            "Наименование": raw.get("productName"),
            "Полная стоимость": raw.get("productPrice"),
            "По скидке": raw.get("productSalePrice"),
            "Наличие": "В наличии" if any(val == 1 for val in raw.get("availability", {}).values()) else "Нет в наличии",
        }
        krossData.append(filtered)

    with open("KrossData.json", "w", encoding="utf-8") as f:
        json.dump(krossData, f, ensure_ascii=False, indent=4)
    print(json.dumps(krossData, ensure_ascii=False, indent=4))

# Смотрим на страницу и выуживаем ссылку на продукт, цифры в ссылке подходят для эндпоинта АПИ
def parse_page(html):
    ids = []
    for node in html.css('a[data-selenium="product-name"]'):
        href = node.attributes.get('href')
        ids.append(href.strip("/").split("/")[-1])
    return ids

# Двигаемся по страницам
def get_page(baseurl, page):
    resp = httpx.get(baseurl + str(page), headers=headers, cookies=cookes, follow_redirects=True)
    # если упремся в 404 во время перебора страниц
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as err:
        print(f"Error {err.response.status_code} while request {err.request.url!r} Page limit!")
        return False
    html = HTMLParser(resp.text)
    return html

# Наше тело, основной урл, собиратель айди all_ids, перебор страниц(отправляем полный урл, полученный респорс парсим),
# полученные айди из parse_page добавляем в собиратель айдишников, сохраняем джсон с списком айди и вызываем извлекатель данных.
def main():
    baseurl = "https://www.sportmaster.ru/catalog/krossovki_/?page="
    all_ids = []
    for x in range(1,2):
        print(f"Page {x}")
        html = get_page(baseurl, x)
        if html is False:
            break
        data = parse_page(html)
        if not data:  # если список пустой
            print("Товаров больше нет, остановка.")
            break
        all_ids.extend(data)
        print(data)

    with open("KrossIds.json", "w", encoding="utf-8") as f:
        json.dump(all_ids, f, ensure_ascii=False, indent=4)

    get_json_data()

if __name__ == "__main__":
    main()
