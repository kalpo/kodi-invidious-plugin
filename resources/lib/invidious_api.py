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

        #   ===                       AUTHORIZED GET REQUESTS                              ===
        #   
        #   Headers are needed in order to get auhtorized on an instance which is needed in 
        #   order to get the user subscription feed.
        #
        #   There are two ways to get authorization, with a cookie SID or with a Bearer token
        #   More info here:   https://docs.invidious.io/authenticated-endpoints/
        #
        #   It seems only a few instances fully actively support the API there is a list
        #   here: https://api.invidious.io/
        #
        #   ====== AUTH TOKENS ======
        #   In order to get an auth token, a logged-in user must be directed to a link that
        #   creates the request on the server. This is the structure of the address:
        #   
        #   [instance]/authorize_token?scopes=[scopes]:[resources];expire=[token_lifetime]
        #   where:
        #       [instance]       :   a instance base url
        #       [scopes]         :   list of methods separated by comes (e.g. GET,POST, ...)
        #       [resources]      :   path that requires authorization (e.g. feed, playlists, ...)
        #       [token_lifetime] :   time in seconds until the token expires
        #
        #   For example: 
        #               https://invidious.osi.kr/authorize_token?scopes=GET:*;expire=0
        #               Should produce a token after a logged-in user has given permission
        # 
        #   Tokens look like this:
        #
        #         {"session":"v1:y_ITFBxpa8TW6GTydmDIc3dnISLGFHockWb95nfNr-A=","scopes":["GET:*"],
        #           "expire":0,"signature":"1lwiswyX5r4zvurkqwlsVU7Pv2s7zjfS9hpLHeYrCp8="}  
        # 
        #   In order to use the token, the request must include it in the headers. And it must 
        #   be declared as a Bearer token. The auth header would look like this:
        # 
        #   headers = {  "Authentication" : "Bearer " + auth_token, ...  }             
        #   
        #   NOTE that this tokens seem to expire much quicker than desired. No matter what
        #   expire, they seem to last around 2 h in some if not all instances. 
        #   
        #
        #   ====== COOKIE SID ======
        #   One can extract the cookie SID from a logged in browser. Probably the simplest way 
        #   is to install a browser extension that does it for you. Cookie SIDs seem to last 
        #   far longer and are more managable as they don't include too many special characters 
        #   and are way smaller, so much more manageble.
        #
        #   Cookie's SID look like this:
        #
        #           0EN4crGKextdAq0B1qwH7wGPprTFRoa1FJO-_R7Of8o=
        #
        #   In order to send the SID with the request, it must be included in the headers. 
        #   The it must be passed as an atribute called SID on the cookie header like so: 
        # 
        #   headers = {  "Cookie" : "SID=" + self.auth_sid, ...  }
        #
        #   More cookie atributes can be passed such as expiry, but they don't seem to be
        #   necesary.
        # TODO: find a more user friendly approach to logging in and auth.

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

        # The JSON from subscriptions comes packaged with an added notifications feed
        if 'videos' in data:
            data = data['videos']

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
