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