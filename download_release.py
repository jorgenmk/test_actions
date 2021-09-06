import requests
import os
import io
import zipfile
import pprint

token = os.getenv("THINGY91_ARTIFACT_TOKEN_GH")

url = "https://api.github.com/repos/jorgenmk/test_actions/actions/artifacts"
headers = {"Accept":"application/json", "Authorization": f"token {token}"}

try:
	os.mkdir("release")
except FileExistsError:
	pass

r = requests.get(url, headers=headers)
r.raise_for_status()
data = r.json()

for artifact in data["artifacts"][0:2]:
	pprint.pprint(artifact)
	r = requests.get(artifact["archive_download_url"], headers=headers)
	r.raise_for_status()
	with zipfile.ZipFile(io.BytesIO(r.content), "r") as z:
		for fileinfo in z.infolist():
			with zipfile.ZipFile(io.BytesIO(z.read(fileinfo))) as z2:
				z2.extractall("release")

