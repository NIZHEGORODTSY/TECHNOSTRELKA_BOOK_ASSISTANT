def format_library(library: dict[str, list[str]]) -> list[list[str, str]]:
    formatted_library = []
    for author in library.keys():
        for book in library[author]:
            formatted_library.append([author, book])
    return formatted_library

def get_books_amount(library: dict[str, list[str]]) -> int:
    amount = 0
    for author in library.keys():
        amount += len(library[author])
    return amount

def read_requests_count() -> int:
    with open('addition_data.txt', 'a+') as f:
        cnt = f.read()
        if cnt == '':
            f.write('0')
            return 0
        return int(cnt)

def increase_requests_count(cur_cnt: int) -> int:
    with open('addition_data.txt', 'w+') as f:
        f.write(str(cur_cnt + 1))
        return cur_cnt + 1
