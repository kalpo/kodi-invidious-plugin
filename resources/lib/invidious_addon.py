import sys

import invidious_plugin
import invidious_api
import xbmcplugin
import xbmcaddon
def update_SID():
    addon = xbmcaddon.Addon('plugin.video.invidious')
    instance_url = addon.getSetting("instance_url")
    auth_username = addon.getSetting("auth_user")
    auth_password = addon.getSetting( "auth_password")

    sid = invidious_api.InvidiousAPIClient.fetch_SID_from_login(instance_url, auth_username, auth_password)
    addon.setSetting("auth_sid", sid)
    print(sid, file=sys.stderr)

def main():

    if sys.argv[1] == "getSID":
        update_SID()
        sys.exit()
    
    plugin = invidious_plugin.InvidiousPlugin.from_argv()

    xbmcplugin.setContent(plugin.addon_handle, "videos")

    return plugin.run()


if __name__ == "__main__":
    sys.exit(main())
