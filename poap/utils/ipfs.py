import mimetypes

import requests

HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweEVlMTUxODM4NDcyNTU3RWZmOEQ1MmZkMzY3NGVDZTcyMkU3OEI5MzEiLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY3ODQzOTUzMTU4NSwibmFtZSI6IlBPQVAifQ.jYVCWoZDHHXviHogqTrD6nD3CV1qmCiRyimnlSyENnU",
}


def upload(file_stream, content_type: str = None):
    if not content_type:
        content_type = mimetypes.guess_type(file_stream.name)[0]
    file_stream.seek(0)
    HEADER["Content-Type"] = content_type
    resp = requests.post("https://api.nft.storage/upload", data=file_stream, headers=HEADER)
    return resp.json()


if __name__ == "__main__":
    with open("/Users/haohao/Downloads/Conight-2021.stl", "rb") as f:
        resp = upload(f)
        print(resp)
