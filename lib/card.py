import os
import requests

CARD_API_URL = os.getenv("CARD_API_URL")
MOCKUP = os.getenv("MOCKUP", "false").lower() == "true"

MOCK_CARD_DATA = {
    "id": "1ee156bb-7d22-4e30-9443-99d1e9a1f3ca",
    "type": "teacher",
    "institution": "smkn1ngawi",
    "schoolName": "SMKN 1 NGAWI",
    "schoolAddress": "Jl. Pendidikan No. 1, Jawa Timur",
    "schoolCity": "Ngawi",
    "schoolLatitude": -7.4014644,
    "schoolLongitude": 111.4439616,
    "cardTitle": "KARTU TANDA DOSEN",
    "name": "SARI HARTONO",
    "nisn": "8735384229",
    "kelas": None,
    "jurusan": None,
    "jabatan": "Dosen",
    "teacherId": "4132715887",
    "issuedStatus": "06 May 2021 / Aktif",
    "ttl": "Tangerang, 4 Oktober 1975",
    "tahun": "06 May 2021",
    "status": "Aktif",
    "validUntil": "31 DESEMBER 2028",
    "photoUrl": "http://img.b2bpic.net/free-photo/happy-young-girl-white-t-shirt-looking-camera-smiling-confident-standing-blue-background_141793-118096.jpg",
    "downloadUrl": "https://idgen-cyan.vercel.app/api/card/download/1ee156bb-7d22-4e30-9443-99d1e9a1f3ca",
    "imageBase64": "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt",
}


def get_card_data(app_type="faculty"):
    if MOCKUP:
        data = MOCK_CARD_DATA
    else:
        api_type = "teacher" if app_type == "faculty" else "student"
        resp = requests.get(f"{CARD_API_URL}?type={api_type}")
        resp.raise_for_status()
        data = resp.json()
    print(f"Card: {data.get('name')} — {data.get('schoolName')}")
    return data
