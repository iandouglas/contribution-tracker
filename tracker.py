import json
from github import Github

# https://api.github.com/orgs/{org_name}/members
# https://api.github.com/orgs/{org_name}/members/member
# https://api.github.com/orgs/{org_name}/repos
# https://api.github.com/repos/{org_name}/{repo_name}/git/commits
# https://api.github.com/repos/{org_name}/{repo_name}/contributors
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators/{collaborator_name}

users_file = open('users.json', 'r')
global_users = json.loads(users_file.read())

def repo_stats(repo):
    emails = {}
    contributors = {}
    for contributor in repo.get_contributors():
        if contributor.login not in contributors:
            contributors[contributor.login] = {
                'login': contributor.login,
                'add': 0,
                'del': 0,
                'total': 0,
            }
        anon_email = f'{contributor.id}+{contributor.login}@users.noreply.github.com'
        contributors[contributor.login]['emails'] = [anon_email]
        emails[anon_email] = contributor.login
        if contributor.email is not None:
            contributors[contributor.login]['emails'].append(contributor.email)
            emails[contributor.email] = contributor.login

    users = []
    for commit in repo.get_commits().reversed:
        users.append(commit.committer)
        user = commit.committer
        message = commit.commit.message
        stats = commit.stats
        contributors[user.login]['add'] += stats.additions
        contributors[user.login]['del'] += stats.deletions
        contributors[user.login]['total'] += stats.total

        for line in message.split("\n"):
            email = None
            if 'Co-authored-by' in line:
                email = message.split('<')[1].split('>')[0]
                if emails[email] == user.login:
                    continue

                if email not in emails:
                    print(emails)
                    login = input('enter the login for this user: ')
                    emails[email] = login.strip()
                    remember = input('remember for next time? y/n')
                    remember = remember.strip().lower()
                    if remember == 'y':
                        global_users[email] = login
                        f = open('users.json', 'w')
                        f.write(json.dumps(global_users))
                co_author = emails[email]
                contributors[co_author]['add'] += stats.additions
                contributors[co_author]['del'] += stats.deletions
                contributors[co_author]['total'] += stats.total

    details = {
        'contributors': contributors
    }


    return details


if __name__ == '__main__':
    # "My-Solar-Garden/rails_backend"
    repo_or_org = input('Enter GitHub Organization or Repo URL, ie "turingschool" or "turingschool/backend-curriculum-site": ')
    repo_or_org = repo_or_org.strip()

    print(f'Checking {repo_or_org} for access...')

    access_token = ""
    g = Github(access_token)

    repo = None
    org = None

    if '/' in repo_or_org:
        repo = g.get_repo(repo_or_org)
        print(repo_stats(repo))

    else:
        org = g.get_organization(repo_or_org)
        stats = {}
        for repo in org.get_repos():
            stats[repo.name] = repo_stats(repo)
        print(stats)



# contents = repo.get_top_paths()
#
# contents = repo.get_top_referrers()
#
# sha = 'abc123'
# commit = repo.get_commit(sha=sha)

# https://api.github.com/orgs/{org_name}/members
# https://api.github.com/orgs/{org_name}/members/member
# https://api.github.com/orgs/{org_name}/repos
# https://api.github.com/repos/{org_name}/{repo_name}/git/commits
# https://api.github.com/repos/{org_name}/{repo_name}/contributors
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators
# https://api.github.com/repos/{org_name}/{repo_name}/collaborators/{collaborator_name}
