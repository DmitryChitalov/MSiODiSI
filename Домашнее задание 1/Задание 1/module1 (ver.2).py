from github import Github

g = Github("studentotlichnik", "passwrd")

with open('git_repos (ver.2).html','w') as file:
    for repo in g.get_user().get_repos():
        print(repo.name)
        file.write(repo.name+'\n')
