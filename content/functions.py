from markupsafe import Markup

from main_operations.scraper.json_save import categories_extractor


def get_list_of_categories(articles, categories):
    category_count = {category: 0 for category in categories}

    for article in articles:
        if 'category' in article and article['category'] in category_count:
            category_count[article['category']] += 1

    category_count = {category: count for category, count in category_count.items() if count > 0}

    return category_count


def split_categories_by_frequency(category_count):
    sorted_categories = sorted(category_count.items(), key=lambda item: item[1], reverse=True)

    top_5_categories = [category for category, count in sorted_categories[:5]]
    remaining_categories = [category for category, count in sorted_categories[5:]]

    return top_5_categories, remaining_categories


def get_first_n_articles_by_category(articles, category, n):
    filtered_articles = []
    count = 0

    for article in articles:
        if article.get('category') == category:
            filtered_articles.append(article)
            count += 1
            if "rewritten_content" in article:
                article["rewritten_content"] = Markup(article["rewritten_content"])
            if count == n:
                break

    return filtered_articles


async def get_categories(topic, json_data):
    get_all_categories = await categories_extractor(topic)
    items = [item.strip() for item in get_all_categories.splitlines()]
    categories_list = [item.strip('",[]') for item in items if item.strip('",[]')]
    all_categories = get_list_of_categories(json_data, categories_list)

    popular_categories, remaining_categories = split_categories_by_frequency(all_categories)
    return popular_categories, remaining_categories, all_categories


def content_all(all_categories, json_data):
    articles_with_index = []

    for category in all_categories:
        articles_with_index.extend(get_first_n_articles_by_category(json_data, category, 5))

    max_list_len = 5

    categories = {}
    for article in articles_with_index:
        category = article.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        if len(categories[category]) < max_list_len:
            categories[category].append(article)

    content = {category: articles for category, articles in categories.items() if len(articles) >= max_list_len}
    return content





