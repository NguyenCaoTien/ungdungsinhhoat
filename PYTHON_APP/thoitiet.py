import requests
import json

OUTPUT_FILE = "datarac/weather.json"

def fetch_weather_data():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 10.8231,
        "longitude": 106.6297,
        "current_weather": True,
        "timezone": "Asia/Ho_Chi_Minh"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ Dữ liệu thời tiết đã được lưu vào", OUTPUT_FILE)

    except requests.RequestException as e:
        print("❌ Lỗi khi lấy dữ liệu thời tiết:", e)

if __name__ == "__main__":
    fetch_weather_data()
