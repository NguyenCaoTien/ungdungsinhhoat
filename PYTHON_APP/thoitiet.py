import requests


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

        current = data.get("current_weather", {})
        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        weather_code = current.get("weathercode")

        print(f"🌡 Nhiệt độ: {temperature}°C")
        print(f"💨 Gió: {windspeed} km/h")
        print(f"☁ Mã thời tiết: {weather_code}")
        return current
    except requests.RequestException as e:
        print("❌ Lỗi khi lấy dữ liệu thời tiết:", e)
        return None

if __name__ == "__main__":
    fetch_weather_data()
