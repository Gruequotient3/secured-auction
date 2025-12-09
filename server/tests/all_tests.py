import time
from typing import Optional

import requests

BASE_URL = "http://localhost:8000"


# ========== AUTH ==========

def register_user(username: str, password: str):
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": username,
        "password": password,
    }
    resp = requests.post(url, data=data)
    print("REGISTER:", resp.status_code, resp.text)
    return resp


def login_user(username: str, password: str) -> Optional[str]:
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password,
    }
    resp = requests.post(url, data=data)
    print("LOGIN:", resp.status_code, resp.text)
    if resp.status_code != 200:
        return None
    body = resp.json()
    return body.get("access_token")


# ========== AUCTIONS ==========

def create_auction(token: str, title: str, description: str, price: float, seconds_from_now: int, image_path: str):
    url = f"{BASE_URL}/create-auction"

    timestamp = int(time.time()) + seconds_from_now  # end_at

    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "title": title,
        "description": description,
        "price": str(price),       # Form → str
        "timestamp": str(timestamp),
    }
    files = {
        "image": open(image_path, "rb"),
    }

    resp = requests.post(url, headers=headers, data=data, files=files)
    print("CREATE AUCTION:", resp.status_code, resp.text)
    if files["image"]:
        files["image"].close()
    return resp


def list_auctions():
    url = f"{BASE_URL}/list-auctions"
    resp = requests.post(url)
    print("LIST AUCTIONS:", resp.status_code, resp.text)
    return resp


def get_auction(auction_id: int):
    url = f"{BASE_URL}/get-auction"
    data = {
        "auction_id": str(auction_id),
    }
    resp = requests.post(url, data=data)
    print("GET AUCTION:", resp.status_code, resp.text)
    return resp


def edit_auction(token: str, auction_id: int,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 base_price: Optional[float] = None,
                 end_at: Optional[int] = None,
                 status: Optional[str] = None):
    """
    Отправляет JSON под EditAuctionSchema.
    Поля, которые не хочешь менять, можно не передавать (оставить None).
    """
    url = f"{BASE_URL}/edit-auction"
    headers = {
        "Authorization": f"Bearer {token}",
    }

    payload = {"id": auction_id}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if base_price is not None:
        payload["base_price"] = base_price
    if end_at is not None:
        payload["end_at"] = end_at
    if status is not None:
        payload["status"] = status

    resp = requests.post(url, headers=headers, json=payload)
    print("EDIT AUCTION:", resp.status_code, resp.text)
    return resp


def delete_auction(token: str, auction_id: int):
    url = f"{BASE_URL}/delete-auction"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "auction_id": str(auction_id),
    }
    resp = requests.post(url, headers=headers, data=data)
    print("DELETE AUCTION:", resp.status_code, resp.text)
    return resp


# ========== BIDS ==========

def create_bid(token: str, auction_id: int, price: float):
    """
    CreateBidSchema: { "auction_id": int, "price": float }
    user_id подставляется на бэке через get_current_user.
    """
    url = f"{BASE_URL}/bid"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    json_payload = {
        "auction_id": auction_id,
        "price": price,
    }
    resp = requests.post(url, headers=headers, json=json_payload)
    print("CREATE BID:", resp.status_code, resp.text)
    return resp


def cancel_bid(token: str, bid_id: int):
    """
    RemoveBidSchema: { "id": int }
    """
    url = f"{BASE_URL}/cancel-bid"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    json_payload = {
        "id": bid_id,
    }
    resp = requests.post(url, headers=headers, json=json_payload)
    print("CANCEL BID:", resp.status_code, resp.text)
    return resp


# ========== DEMO FLOW ==========

if __name__ == "__main__":
    # 1. Регистрируем пользователя
    username = "testuser"
    password = "testpassword123"

    print("=== REGISTER USER ===")
    register_user(username, password)

    # 2. Логинимся, получаем JWT
    print("\n=== LOGIN USER ===")
    token = login_user(username, password)
    print("TOKEN:", token)

    if not token:
        print("Не удалось получить токен, остальные проверки бессмысленны.")
        exit(1)

    # 3. Создаём аукцион
    print("\n=== CREATE AUCTION ===")
    # укажи реальный путь к картинке:
    image_path = "test.jpg"
    resp_auction = create_auction(
        token=token,
        title="Test Auction",
        description="Some description",
        price=10.0,
        seconds_from_now=3600,
        image_path=image_path,
    )

    if resp_auction.status_code != 200:
        print("Аукцион не создался, дальше будет больно, но идём дальше :)")
        auction_id = None
    else:
        auction_id = resp_auction.json()["id"]

    # 4. Список аукционов
    print("\n=== LIST AUCTIONS ===")
    list_auctions()

    # 5. Получаем аукцион по id
    if auction_id is not None:
        print("\n=== GET AUCTION ===")
        get_auction(auction_id)

        # 6. Делаем ставку
        print("\n=== CREATE BID ===")
        resp_bid = create_bid(token, auction_id, price=15.0)
        if resp_bid.status_code == 200:
            bid_id = resp_bid.json()["id"]
        else:
            bid_id = None

        # 7. Отменяем ставку
        if bid_id is not None:
            print("\n=== CANCEL BID ===")
            cancel_bid(token, bid_id)

        # 8. Удаляем аукцион
        print("\n=== DELETE AUCTION ===")
        delete_auction(token, auction_id)

    print("\n=== DONE ===")

