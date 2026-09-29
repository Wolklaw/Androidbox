import json
import urllib.request

from . import REPOSITORY, VERSION


def parse(version):
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def latest():
    request = urllib.request.Request(f"https://api.github.com/repos/{REPOSITORY}/releases/latest",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "Androidbox"})
    with urllib.request.urlopen(request, timeout=15) as response:
        release = json.loads(response.read())
    return release["tag_name"].lstrip("v"), release["html_url"]


def newer(version):
    return parse(version) > parse(VERSION)
