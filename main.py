"""Ручные тестовые запросы к API из консоли.

Запуск: python main.py
В main выбираем, какую функцию вызвать: GET, POST или страна.
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Старые адреса /v3.1 на restcountries.com отключены.
# Живые данные теперь на поддомене api, версия v5.
BASE_URL = "https://api.restcountries.com"
# Публичный демо-ключ из документации сервиса. Свой ключ — в .env, он его заменит.
DEMO_API_KEY = "rc_live_demo"
# Сколько секунд ждать ответ. Иначе скрипт может зависнуть на недоступном адресе.
TIMEOUT_SECONDS = 15


def api_key() -> str:
    """Ключ из .env, если он задан. Иначе демо-ключ для пробных запросов."""
    return os.getenv("RESTCOUNTRIES_API_KEY") or DEMO_API_KEY


def show_response(response: requests.Response) -> None:
    """Печатает статус и тело ответа. Статус — это код вроде 200 или 404."""
    print(f"\nСтатус: {response.status_code}")

    try:
        body = response.json()
    except ValueError:
        # Сервер ответил не JSON, а обычным текстом или HTML.
        print(response.text)
        return

    print(json.dumps(body, ensure_ascii=False, indent=2))


def send_get(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
) -> None:
    """GET: забираем данные по адресу, своё тело не отправляем.

    params — это query-параметры, они дописываются к адресу как ?q=germany.
    headers — служебные заголовки, для v5 туда кладётся ключ доступа.
    """
    print(f"GET {url}")
    response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT_SECONDS)
    show_response(response)


def send_post(url: str, payload: dict) -> None:
    """POST: отправляем JSON и смотрим, что сервер вернул.

    json=payload сам ставит заголовок Content-Type: application/json
    и превращает словарь Python в текст JSON.
    """
    print(f"POST {url}")
    print("Тело:", json.dumps(payload, ensure_ascii=False))
    response = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    show_response(response)


def make_get_country_request(country: str) -> None:
    """GET страны по имени в актуальной версии API.

    Адрес: https://api.restcountries.com/countries/v5/name?q={country}
    q — поиск по имени, без учёта регистра. Ключ уходит в заголовке Authorization.
    """
    country = country.strip()
    if not country:
        print("Название страны пустое, запрос не отправлен.")
        return

    url = f"{BASE_URL}/countries/v5/name"
    send_get(
        url,
        params={"q": country},
        headers={"Authorization": f"Bearer {api_key()}"},
    )


def read_post_body() -> dict:
    """Спрашивает JSON одной строкой. Пустой ввод — пустой объект {}."""
    raw = input("JSON-тело (пусто = {}): ").strip()
    if not raw:
        return {}

    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Тело POST должно быть JSON-объектом, например {\"name\": \"test\"}")
    return data


def main() -> None:
    """Точка входа: здесь только выбор, какую функцию запустить."""
    while True:
        print("\n1 — GET")
        print("2 — POST")
        print("3 — Страна")
        print("4 — Выйти")
        choice = input("Какой запрос запускаем: ").strip()

        if choice == "4":
            print("Выход.")
            return

        try:
            if choice == "1":
                url = input("URL: ").strip()
                if not url:
                    print("URL пустой, запрос не отправлен.")
                    continue
                send_get(url)
            elif choice == "2":
                url = input("URL: ").strip()
                if not url:
                    print("URL пустой, запрос не отправлен.")
                    continue
                send_post(url, read_post_body())
            elif choice == "3":
                country = input("Страна: ").strip()
                make_get_country_request(country)
            else:
                print("Нужно ввести 1, 2, 3 или 4.")
        except requests.RequestException as error:
            # Сеть, таймаут, неверный адрес — requests собирает это в один тип ошибок.
            print(f"Запрос не выполнился: {error}")
        except json.JSONDecodeError:
            print("Тело не похоже на JSON. Пример: {\"name\": \"test\"}")
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    main()
