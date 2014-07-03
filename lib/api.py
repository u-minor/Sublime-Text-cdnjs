import sublime

import json
import os
import threading
import time

from .http import get
from .loading import CdnjsLoadingAnimation
from .cache import get_cache_path
from .cache import get_package_list
from .cache import set_package_list
from .cache import time_has_passed
from .cache import optimize_cache


class CdnjsApiCall(threading.Thread):
    PACKAGES_URL = 'http://www.cdnjs.com/packages.json'

    def __init__(self, view, timeout, onlyURL=False, wholeFile=False):
        self.settings = sublime.load_settings("cdnjs.sublime-settings")
        self.view = view
        self.timeout = timeout
        self.onlyURL = onlyURL
        self.wholeFile = wholeFile
        self.proxies = self.settings.get("proxies", {})
        self.cachedResponse = False
        self.cacheTime = self.settings.get("cache_ttl", 600)
        self.cacheDisabled = self.settings.get("cache_disabled", False)
        self.cacheFilePath = get_cache_path()
        threading.Thread.__init__(self)
        CdnjsLoadingAnimation(self)

    def run(self):
        result = self.get_result()
        self.packages = json.loads(result)['packages'][:-1]
        sublime.set_timeout(self.callback, 10)

    def get_result(self):
        result = self.get_packagelist_cache()
        if not result:
            result = self.get_result_from_cdn()
        return result

    def get_result_from_cdn(self):
        result = get(self.PACKAGES_URL, self.proxies, self.timeout)
        if result:
            result = optimize_cache(result)
            set_package_list(self.cacheFilePath, result)
        return result

    def callback(self):
        self.view.run_command('cdnjs_library_picker', {
            "packages": self.packages,
            "onlyURL": self.onlyURL,
            "wholeFile": self.wholeFile
        })

    def get_packagelist_cache(self):
        if self.cacheDisabled:
            return None

        try:
            # check if the last save is older than the cacheTime
            if time_has_passed(os.stat(self.cacheFilePath).st_mtime, self.cacheTime):
                # missed cache, clear file
                os.remove(self.cacheFilePath)
                return None
            else:
                # hit cache, return cached data
                self.cachedResponse = True
                return get_package_list(self.cacheFilePath)
        except IOError as e:
            # there was no file found, no cache is set
            return None
        except Exception as e:
            print('Uncaught exception in cdnjs get cache: {0}'.format(e))
            return None
