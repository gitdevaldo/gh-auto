# GitHub Education Faculty Application - cURL Request

> **Important:** Update `authenticity_token` before running.

## Step 1: Export the ID card image as base64

```bash
ID_CARD_B64=$(base64 -w 0 attached_assets/ID_Card_1775826138_1775830085724.png)
```

## Step 2: Run the cURL request

```bash
curl 'https://github.com/settings/education/developer_pack_applications' \
  -X POST \
  -H 'authority: github.com' \
  -H 'accept: text/vnd.turbo-stream.html, text/html, application/xhtml+xml' \
  -H 'accept-encoding: gzip, deflate, br, zstd' \
  -H 'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'cookie: _octo=GH1.1.2049350369.1775031132; GHCC=Required:1-Analytics:1-SocialMedia:1-Advertising:1; MicrosoftApplicationsTelemetryDeviceId=994ff2f5-612b-43d1-9638-058d8e3c26d9; MSFPC=GUID=6785cbfc955746e09a4aaafd557d5d10&HASH=6785&LV=202604&V=4&LU=1775031148495; _device_id=66185fd411ec6318e2db9f46f13696a2; saved_user_sessions=272754949%3AndrcVERmQquyhAOsQR2lCexaGMtdDIf2nhxix_60HS-Az0mm; user_session=ndrcVERmQquyhAOsQR2lCexaGMtdDIf2nhxix_60HS-Az0mm; __Host-user_session_same_site=ndrcVERmQquyhAOsQR2lCexaGMtdDIf2nhxix_60HS-Az0mm; logged_in=yes; dotcom_user=gitcanadadev; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; cpu_bucket=md; preferred_color_mode=dark; tz=Asia%2FBangkok; last_write_ms=1775829027485; _gh_sess=GJM2LkpwR3kE0bvRhUG0pArfs5JG%2FVhlQvKbaOHia4upWJUY8yXo8qlwnoSLQsepR6QCC06T7HKKRx76eXQ0kb2aC0KkyUPwBdxlOSMxdqtXay6ENzvRudjAwbCcdNsm0ugjxStapwlC%2FMN8o3qy98AY0DBvjlDdqMTkgK9Sk6r9xB7d4iAHEi9%2FX%2Fehr6HRmOZp6XCqevRdwwi2%2Bdj3yAIo6QbrtUBdRnGDCEUVj62mtqeRndqYlxfy0hCAEDR8bKf9KEZZKFfknVUgeVtAwWhMWJCe5hvhc1TQ9vQjGjDSPL5U8fhFxC%2BGWEAPxomH98eZW2BBdX1bbg0%2B5QM41%2FR69SbHpOoMiEPYmRwFbE9vhqb9qRehPMhu2OKbK%2BFGT58n6NTrEKRw1svX8riQQpmDju6ihBftNi%2BtlIfB6G2yiyAqOS45vye%2FigXuMP2SFEQGjA' \
  -H 'origin: https://github.com' \
  -H 'priority: u=1, i' \
  -H 'referer: https://github.com/settings/education/benefits' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'turbo-frame: dev-pack-form' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'x-fetch-nonce: v2:011cee76-c244-a5fb-be4d-5f7312599083' \
  -H 'x-github-client-version: 57aa204034d2b037c33554f883740396c0ff9993' \
  --data-urlencode 'submit=Submit Application' \
  --data-urlencode 'authenticity_token=UPDATE_ME' \
  --data-urlencode 'dev_pack_form[proof_type]=1. Dated school ID' \
  --data-urlencode "dev_pack_form[photo_proof]={\"image\":\"data:image/png;base64,${ID_CARD_B64}\",\"metadata\":{\"filename\":\"camera.png\",\"type\":\"camera\",\"mimeType\":\"image/png\",\"deviceLabel\":\"USB2.0 HD UVC WebCam (322e:2103)\"}}" \
  --data-urlencode 'dev_pack_form[application_type]=faculty' \
  --data-urlencode 'dev_pack_form[browser_location]=' \
  --data-urlencode 'dev_pack_form[camera_required]=false' \
  --data-urlencode 'dev_pack_form[email_domains]=[]' \
  --data-urlencode 'dev_pack_form[form_variant]=initial_form' \
  --data-urlencode 'dev_pack_form[latitude]=-7.781354691702329' \
  --data-urlencode 'dev_pack_form[location_shared]=true' \
  --data-urlencode 'dev_pack_form[longitude]=112.12809680508624' \
  --data-urlencode 'dev_pack_form[new_school]=false' \
  --data-urlencode 'dev_pack_form[override_distance_limit]=false' \
  --data-urlencode 'dev_pack_form[school_email]=gitsparkdev@gmail.com' \
  --data-urlencode 'dev_pack_form[school_name]=SMKN 1 Ngawi' \
  --data-urlencode 'dev_pack_form[selected_school_id]=18635' \
  --data-urlencode 'dev_pack_form[two_factor_required]=false' \
  --data-urlencode 'dev_pack_form[user_too_far_from_school]=false' \
  --data-urlencode 'dev_pack_form[utm_content]=' \
  --data-urlencode 'dev_pack_form[utm_source]=' \
  --data-urlencode 'dev_pack_form[form_variant]=upload_proof_form' \
  --data-urlencode 'submit=Submit Application' \
  --compressed \
  -v
```

## Values to update before running

| Field | Where |
|-------|-------|
| `authenticity_token` | `--data-urlencode` |
