import os
import requests

CARD_API_URL = os.getenv("CARD_API_URL")
MOCKUP = os.getenv("MOCKUP", "false").lower() == "true"

MOCK_CARD_DATA = {
    "id": "e4890dc0-258b-4b66-955e-36421254c7a7",
    "type": "teacher",
    "institution": "smkn1ngawi",
    "schoolName": "SMKN 1 NGAWI",
    "schoolAddress": "Jl. Pendidikan No. 1, Jawa Timur",
    "cardTitle": "KARTU TANDA DOSEN",
    "name": "AGUS HIDAYAT",
    "nisn": "2923342806",
    "kelas": None,
    "jurusan": None,
    "jabatan": "DOSEN",
    "teacherId": "4801830148",
    "issuedStatus": "28 Oct 2011 / Aktif",
    "ttl": "Semarang, 14 April 1969",
    "tahun": "28 Oct 2011",
    "status": "AKTIF",
    "validUntil": "31 DESEMBER 2028",
    "principal": "Dr. Indra, M.Pd.",
    "principalId": "Napme PEE0935",
    "photoUrl": "http://img.b2bpic.net/premium-photo/headshot-portrait-attractive-teenage-girl-smiling-with-teeth-looking-camera-light-studio-background-beautiful-female-teenager-with-healthy-skin-hair-teeth-adolescence-youth-beauty-concept_116407-24076.jpg",
    "downloadUrl": "https://localhost:3001/api/card/download/e4890dc0-258b-4b66-955e-36421254c7a7",
    "imageBase64": "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt",
}


def get_card_data():
    if MOCKUP:
        print("[MOCKUP] Using mock card data")
        data = MOCK_CARD_DATA
    else:
        resp = requests.get(CARD_API_URL)
        resp.raise_for_status()
        data = resp.json()
    print(f"Got card data: name={data.get('name')}, school={data.get('schoolName')}")
    return data


def get_card_name():
    data = get_card_data()
    return data["name"]
