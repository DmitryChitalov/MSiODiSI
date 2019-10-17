import requests

username="studentotlichnik"
password=""

req = requests.get('https://api.github.com/user', auth=(username, password))
with open('git_authorisation.html','wb') as file:
    file.write(req.content)


