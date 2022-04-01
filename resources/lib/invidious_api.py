import time
from collections import namedtuple

import requests

VideoListItem = namedtuple("SearchResult",
    [
        "video_id",
        "title",
        "author",
        "description",
        "thumbnail_url",
        "view_count",
        "published",
    ]
)


class InvidiousAPIClient:
    def __init__(self, instance_url, is_feed_enabled, auth_token, auth_sid):
        self.instance_url = instance_url.rstrip("/")
        self.is_feed_enabled = is_feed_enabled
        self.auth_token = auth_token
        self.auth_sid = auth_sid

    def make_get_request(self, *path, **params):
        base_url = self.instance_url + "/api/v1/"

        url_path = "/".join(path)

        while "//" in url_path:
            url_path = url_path.replace("//", "/")

        assembled_url = base_url + url_path

        headers = {}

        if self.is_feed_enabled == "SID":
            headers["Cookie"] = "SID=" + self.auth_sid
        elif self.is_feed_enabled == "token":
            headers["Authentication"] = "Bearer " + self.auth_token

        print("========== request started ==========")
        start = time.time()
        response = requests.get(assembled_url, params=params, headers=headers, timeout=5)
        end = time.time()
        print("========== request finished in", end - start, "s ==========")

        response.raise_for_status()

        return response

    @staticmethod
    def parse_video_list_response(response):
        data = response.json()

        # The JSON from subscriptions comes packaged in two, 'notifications' for new videos in the feed
        # and 'videos' for the rest. So we need to put them together.
        if 'videos' in data:
            data = data['notifications'] + data['videos']

        for video in data:
            for thumb in video["videoThumbnails"]:
                # high appears to be ~480x360, which is a reasonable trade-off
                # works well on 1080p
                if thumb["quality"] == "high":
                    thumbnail_url = thumb["url"]
                    break

            # as a fallback, we just use the last one in the list (which is usually the lowest quality)
            else:
                thumbnail_url = video["videoThumbnails"][-1]["url"]

            yield VideoListItem(
                video["videoId"],
                video["title"],
                video["author"],
                video.get("description", "No description available"),
                thumbnail_url,
                video["viewCount"],
                video["published"],
            )

    def search(self, *terms):
        params = {
            "q": " ".join(terms),
            "sort_by": "upload_date",
        }

        response = self.make_get_request("search", **params)

        return self.parse_video_list_response(response)

    def fetch_SID_from_login(self, auth_username, auth_password):
        if auth_password != "" and auth_username != "":
            data = {
                    'email' : auth_username,
                    'password' : auth_password,
                    'action' : 'singin'
            }
            url = self.instance_url + "/login"
            response = requests.post(url, data)

            return response.history[0].cookies['SID']

    def fetch_subscriptions(self):
        response = self.make_get_request("auth/feed")

        return self.parse_video_list_response(response)

    def fetch_video_information(self, video_id):
        response = self.make_get_request("videos/", video_id)

        data = response.json()

        return data

    def fetch_channel_list(self, channel_id):
        response = self.make_get_request("channels/videos/", channel_id)

        return self.parse_video_list_response(response)

    def fetch_special_list(self, special_list_name):
        response = self.make_get_request(special_list_name)

        return self.parse_video_list_response(response)
