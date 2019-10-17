import requests
user='studentotlichnik'
GitApiUrl='https://api.github.com/users/'
req = requests.get(GitApiUrl+user+'/repos')
with open('git_repos (ver.1).html','wb') as file:
    file.write(req.content)
