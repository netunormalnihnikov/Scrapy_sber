import json

valid_categories = {
    'Автотовары',
    'Бакалея',
    'Бытовая химия, уборка',
    'Вода, соки, напитки',
    'Всё для ремонта',
    'Готовые блюда и полуфабрикаты',
    'Готовые блюда, полуфабрикаты',
    'Дача, сад',
    'Детские товары',
    'Замороженные продукты',
    'Зоотовары',
    'Канцелярия',
    'Колбасы, сосиски, деликатесы',
    'Консервы, соленья',
    'Косметика, гигиена',
    'Молочные продукты, яйца',
    'Мясо, птица',
    'Овощи, фрукты, орехи',
    'Одежда, обувь, аксессуары',
    'Рыба, морепродукты',
    'Сладости',
    'Соусы, специи, масло',
    'Спортивные товары',
    'Сыры',
    'Товары для дома',
    'Хлеб, выпечка',
    'Чай и кофе',
    'Чай, кофе',
    'Чипсы, снеки',
    'Электроника, бытовая техника'
}

sub_lst = []


def get_sub_cat(children_lst, counter=True):
    global sub_lst
    if counter:
        sub_lst = []
    for child in children_lst:
        if child["children"]:
            get_sub_cat(child["children"], counter=False)
        else:
            sub_lst.append(child)


def get_one_line_cat(file):
    final_lst = []
    for category in file:
        if category["name"] in valid_categories:
            get_sub_cat(category["children"])
            for sub_cat in sub_lst:
                final_lst.append({
                    "main_category_name": category["name"],
                    "img_main_category_url": category["icon"]["normal_url"].split("?")[0],
                    "category_name": sub_cat["name"],
                    "img_category_url": sub_cat["icon"]["normal_url"].split("?")[0],
                    "permalink": sub_cat["permalink"],
                })
    return final_lst


if __name__ == '__main__':
    with open('sber_market_categories_2.json', 'r', encoding="utf-8") as f:
        file = json.load(f)
    lst = get_one_line_cat(file)
    print(len(lst))