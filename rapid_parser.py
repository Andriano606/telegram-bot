import json
from typing import List, Dict, Any

class User:
    def __init__(self, data: Dict[str, Any]):
        self.full_name = data.get('full_name')
        self.id = data.get('id')
        self.is_private = data.get('is_private')
        self.is_verified = data.get('is_verified')
        self.profile_pic_url = data.get('profile_pic_url')
        self.username = data.get('username')

class Caption:
    def __init__(self, data: Dict[str, Any]):
        self.content_type = data.get('content_type')
        self.created_at = data.get('created_at')
        self.text = data.get('text')
        self.user = User(data.get('user'))

class Item:
    def __init__(self, data: Dict[str, Any]):
        self.can_reshare = data.get('can_reshare')
        self.can_save = data.get('can_save')
        self.caption = Caption(data.get('caption'))
        self.comment_count = data.get('comment_count')
        self.id = data.get('id')
        self.is_video = data.get('is_video')
        self.like_count = data.get('like_count')
        self.play_count = data.get('play_count')
        self.video_duration = data.get('video_duration')
        self.video_url = data.get('video_url')
        self.user = User(data.get('user'))
        self.image_urls = self.extract_image_urls(data.get('image_versions'))

    @staticmethod
    def extract_image_urls(image_versions: Dict[str, Any]) -> List[str]:
        urls = []
        if image_versions:
            # Add URLs from 'additional_items' if present
            additional_items = image_versions.get('additional_items', {})
            for key, value in additional_items.items():
                if value and 'url' in value:
                    urls.append(value['url'])
            # Add URLs from 'items'
            items = image_versions.get('items', [])
            for image in items:
                if image and 'url' in image:
                    urls.append(image['url'])
            # Add URLs from 'scrubber_spritesheet_info_candidates' if present
            scrubber_candidates = image_versions.get('scrubber_spritesheet_info_candidates', {})
            default_candidate = scrubber_candidates.get('default', {})
            sprite_urls = default_candidate.get('sprite_urls', [])
            for url in sprite_urls:
                if url:
                    urls.append(url)
        return urls

class Data:
    def __init__(self, data: Dict[str, Any]):
        self.count = data.get('count')
        self.items = [Item(item) for item in data.get('items', [])]
        self.user = User(data.get('user'))

class RapidParser:
    def __init__(self, data: Dict[str, Any]):
        self.data = Data(data.get('data'))
        self.pagination_token = data.get('pagination_token')