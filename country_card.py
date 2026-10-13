"""Цветная карточка страны в консоли.

Запуск: python country_card.py
Запрос тот же, что в main.py: GET /countries/v5/name?q=...
Сюда попадают только поля, которые удобно читать. Переводы на десятки
языков, палитра флага и картинки лидеров в вывод не входят.
"""

import requests
from colorama import Fore, Style, init

from main import BASE_URL, TIMEOUT_SECONDS, api_key

# autoreset сбрасывает цвет после каждого print, чтобы он не «залипал» на следующие строки.
init(autoreset=True)

LABEL_WIDTH = 16


def fetch_country(country: str) -> dict:
    """GET карточки страны. Возвращает уже разобранный JSON."""
    url = f"{BASE_URL}/countries/v5/name"
    response = requests.get(
        url,
        params={"q": country},
        headers={"Authorization": f"Bearer {api_key()}"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def row(label: str, value: str) -> None:
    """Одна строка карточки: жёлтая подпись и обычное значение."""
    if not value:
        return
    title = f"{label:<{LABEL_WIDTH}}"
    print(f"{Fore.YELLOW}{title}{Style.RESET_ALL}{value}")


def join_names(items: list, key: str = "name") -> str:
    """Собирает имена из списка словарей в одну строку через запятую."""
    names = [str(item.get(key, "")).strip() for item in items if isinstance(item, dict)]
    return ", ".join(name for name in names if name)


def format_number(value: int | float | None) -> str:
    """41 798 407 вместо 41798407. Пробел — разделитель тысяч."""
    if value is None:
        return ""
    return f"{value:,.0f}".replace(",", " ")


def format_currencies(currencies: list) -> str:
    parts = []
    for item in currencies:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or ""
        code = item.get("code") or ""
        symbol = item.get("symbol") or ""
        extra = ", ".join(part for part in (code, symbol) if part)
        parts.append(f"{name} ({extra})" if extra else name)
    return "; ".join(part for part in parts if part)


def format_memberships(memberships: dict) -> str:
    """В ответе у каждой организации флаг true/false. Показываем только true."""
    titles = {
        "un": "ООН",
        "nato": "НАТО",
        "eu": "ЕС",
        "g7": "G7",
        "g20": "G20",
        "oecd": "ОЭСР",
        "opec": "ОПЕК",
        "brics": "БРИКС",
        "commonwealth": "Содружество",
        "schengen": "Шенген",
        "eurozone": "Еврозона",
        "asean": "АСЕАН",
        "arab_league": "Лига арабских государств",
        "african_union": "Африканский союз",
    }
    active = [titles.get(key, key) for key, enabled in memberships.items() if enabled]
    return ", ".join(active)


def format_leaders(leaders: list) -> str:
    parts = []
    for leader in leaders:
        if not isinstance(leader, dict):
            continue
        name = leader.get("name") or ""
        title = leader.get("title") or ""
        if name and title:
            parts.append(f"{name} — {title}")
        elif name:
            parts.append(name)
    return "; ".join(parts)


def print_demo_notice(demo: dict) -> None:
    """Демо-ключ не ищет страну: сервис присылает один пример и пишет об этом в _demo."""
    message = demo.get("message") or "Ответ получен по демо-ключу, это пример карточки."
    print(f"{Fore.LIGHTYELLOW_EX}Демо-режим. {message}")
    print()


def print_card(country: dict) -> None:
    """Печатает одну страну из списка data.objects."""
    names = country.get("names") or {}
    common = names.get("common") or "Без названия"
    official = names.get("official") or ""
    russian = ((names.get("translations") or {}).get("rus") or {}).get("common") or ""
    flag = (country.get("flag") or {}).get("emoji") or ""
    codes = country.get("codes") or {}
    area = country.get("area") or {}
    description = (country.get("descriptions") or {}).get("short") or ""

    capitals = join_names(country.get("capitals") or [])
    languages = join_names(country.get("languages") or [])
    currencies = format_currencies(country.get("currencies") or [])
    borders = ", ".join(country.get("borders") or [])
    zones = ", ".join(country.get("timezones") or [])
    calling = ", ".join(f"+{code}" for code in (country.get("calling_codes") or []))
    domains = ", ".join(country.get("tlds") or [])
    code_line = " / ".join(
        part for part in (codes.get("alpha_2"), codes.get("alpha_3")) if part
    )
    region_line = " / ".join(
        part for part in (country.get("region"), country.get("subregion")) if part
    )
    area_km = format_number(area.get("kilometers"))
    leaders = format_leaders(country.get("leaders") or [])
    memberships = format_memberships(country.get("memberships") or {})

    print(f"{Fore.CYAN}{'─' * 56}")
    print(f"{Style.BRIGHT}{Fore.CYAN}{flag}  {common}")
    subtitle = " · ".join(part for part in (russian, official) if part and part != common)
    if subtitle:
        print(f"{Fore.WHITE}{subtitle}")
    print(f"{Fore.CYAN}{'─' * 56}")

    row("Столица", capitals)
    row("Регион", region_line)
    row("Население", format_number(country.get("population")))
    row("Площадь", f"{area_km} км²" if area_km else "")
    row("Валюта", currencies)
    row("Языки", languages)
    row("Коды", code_line)
    row("Телефон", calling)
    row("Домен", domains)
    row("Границы", borders)
    row("Пояса", zones)
    row("Строй", country.get("government_type") or "")
    row("Лидеры", leaders)
    row("Организации", memberships)

    if description:
        print()
        print(f"{Fore.LIGHTBLACK_EX}{description}")
    print()


def show_country(country: str) -> None:
    """Запрашивает страну и печатает карточки либо текст ошибки."""
    try:
        body = fetch_country(country)
    except requests.RequestException as error:
        print(f"{Fore.RED}Запрос не выполнился: {error}")
        return

    errors = body.get("errors") or []
    data = body.get("data") or {}
    objects = data.get("objects") or []

    if errors and not objects:
        for error in errors:
            message = error.get("message") if isinstance(error, dict) else str(error)
            print(f"{Fore.RED}{message}")
        return

    if not objects:
        print(f"{Fore.RED}Страна «{country}» не найдена.")
        return

    demo = data.get("_demo")
    if isinstance(demo, dict):
        print_demo_notice(demo)

    for item in objects:
        if isinstance(item, dict):
            print_card(item)


def main() -> None:
    print(f"{Style.BRIGHT}{Fore.CYAN}Карточка страны")
    print(f"{Fore.WHITE}Пустой ввод завершает программу.")

    while True:
        country = input(f"{Fore.GREEN}Страна: {Style.RESET_ALL}").strip()
        if not country:
            print("Выход.")
            return
        print()
        show_country(country)


if __name__ == "__main__":
    main()
