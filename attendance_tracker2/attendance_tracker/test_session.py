import urllib.request, urllib.parse, http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
url = 'http://127.0.0.1:5000/login'
data = urllib.parse.urlencode({'username':'alice','password':'pw'}).encode()
resp = opener.open(url, data)
print('login status', resp.getcode(), '->', resp.geturl())
r = opener.open('http://127.0.0.1:5000/dashboard')
print('dashboard status', r.getcode())
text = r.read(800).decode(errors='ignore')
print(text)
