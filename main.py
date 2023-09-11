from src.scraper import GAScraper
import csv


def main():

    scrapper = GAScraper()

    numbered_dict = {i + 1: key for i, key in enumerate(scrapper.get_categories.keys())}
    print('Категории:')
    for num, value in numbered_dict.items():
        print(f'{num}. {value}')

    while True:
        user_number = int(input("\nВведите номер категории из списка: "))

        if user_number in numbered_dict:
            key = numbered_dict[user_number]
            break
        else:
            print(f"Номер {user_number} не найден в списке категорий.")

    scrapper.get_products_list(key)
    data = scrapper.get_product_info

    with open(f'{key}.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = data[0].keys() if data else []
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for row in data:
            writer.writerow(row)

    print(f"Данные сохранены в файл: {key}.csv")


if __name__ == '__main__':
    main()