import requests

class InstagramManager:
  def __init__(self):
    self.url_info = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
    self.url = "https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts"
    self.headers = {
      "x-rapidapi-key": "4075c383camsh302abf637f0d153p19d0cejsn4219a6036f55",
      "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
    }

  def fetch_posts(self, username_or_id_or_url):
    querystring = {"username_or_id_or_url": username_or_id_or_url}
    response = requests.get(self.url, headers=self.headers, params=querystring)
    data = response.json()
    return data
  
  def check_channel_exists(self, username_or_id_or_url):
        querystring = {"username_or_id_or_url": username_or_id_or_url}
        response = requests.get(self.url_info, headers=self.headers, params=querystring)
        data = response.json()

        return data != {'detail': 'Not found'}