import json
import os
import sys
from os import path
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
    contribs = {}
    for contributor in repo.get_contributors():
        login = contributor.login.lower()
        if login not in contribs:
            contribs[login] = {
                'name': contributor.name,
                'authored': {
                    'add': 0,
                    'del': 0,
                    'total': 0,
                },
                'co-authored': {
                    'add': 0,
                    'del': 0,
                    'total': 0,
                },
            }
        anon_email = f'{contributor.id}+{login}' \
                     f'@users.noreply.github.com'.lower()
        contribs[login]['emails'] = [anon_email]
        emails[anon_email] = login
        if contributor.email is not None:
            email = contributor.email.lower()
            contribs[login]['emails'].append(email)
            emails[email] = login

    if len(emails) > 0:
        print('known contributors:')
        for email, login in emails.items():
            print(f'  {email}: {login}')

    users = []
    commits = repo.get_commits().reversed
    print(f'processing {commits.totalCount} commits:')
    for commit in commits.reversed:
        print('.', end='', flush=True)
        message = commit.commit.message
        stats = commit.stats
        users.append(commit.committer)
        user = commit.committer

        if user is None:
            continue
        login = user.login.lower()

        if login == 'web-flow':
            # print(message)
            # print('skipping stats since it was a github web merge')
            # if login not in contributors:
            #     contributors[login] = {
            #         'web merges': 0
            #     }
            # contributors[login]['web merges'] += 1
            continue

        # print(f'commit by {user.login}')
        contribs[login]['authored']['add'] += stats.additions
        contribs[login]['authored']['del'] += stats.deletions
        contribs[login]['authored']['total'] += stats.total

        for line in message.split("\n"):
            email = None
            if 'Co-authored-by' in line:
                try:
                    email = line.split('<')[1].split('>')[0].lower()
                except IndexError:
                    print('')
                    print(f'{login} made a commit that cannot be processed:')
                    print(message)
                    print('')
                    print('specifically, this line:')
                    print(line)
                    email = input('please enter an email to use here: ')
                login = None
                if email in emails:
                    if emails[email] == user.login.lower():
                        continue
                else:
                    if email not in global_users:
                        print('found a contributor email that did not match:')
                        print(line)
                        login = input(f'enter github username for {email}: ')
                        emails[email] = login.strip().lower()
                        remember = input('remember for next time? y/n ')
                        remember = remember.strip().lower()
                        if remember == 'y':
                            global_users[email] = login
                            f = open('users.json', 'w')
                            f.write(json.dumps(global_users, sort_keys=True,
                                               indent=2))
                            f.close()
                    emails[email] = global_users[email]
                co_author = emails[email]
                if co_author not in contribs:
                    contribs[co_author] = {
                        'name': co_author,
                        'authored': {
                            'add': 0,
                            'del': 0,
                            'total': 0,
                        },
                        'co-authored': {
                            'add': 0,
                            'del': 0,
                            'total': 0,
                        },
                    }
                contribs[co_author]['co-authored']['add'] += stats.additions
                contribs[co_author]['co-authored']['del'] += stats.deletions
                contribs[co_author]['co-authored']['total'] += stats.total

    details = {
        'archived': repo.archived,
        'contributors': contribs
    }


    return details


if __name__ == '__main__':
    if path.exists('auth.py'):
        from auth import access_token
    else:
        print('create auth.py with the following inside it:')
        print('')
        print('access_token = "<token>"')
        print('')
        print('(replace <token> with an actual personal token created at')
        print('https://github.com/settings/tokens/new and give it full "repo"')
        print('and "admin:org" scopes)')
        sys.exit()

    repo_or_org = input('Enter GitHub Organization or Repo URL, ie "turingschool" or "turingschool/backend-curriculum-site": ')
    repo_or_org = repo_or_org.strip()
    # repo_or_org = "My-Solar-Garden"

    print(f'Checking {repo_or_org} for access...')

    g = Github(access_token)

    repo = None
    org = None
    stats = {}

    if '/' in repo_or_org:
        print('getting stats for single repo')
        repo = g.get_repo(repo_or_org)
        stats = repo_stats(repo)
        org_name = repo_or_org.split("/")[0].lower()
        try:
            os.mkdir(f'stats/{org_name}')
        except FileExistsError:
            pass
        with open(f'stats/{org_name}/{repo.name.lower()}.json', 'w') as f:
            f.write(json.dumps(stats, sort_keys=True, indent=2))

    else:
        print('getting stats for organization')
        org = g.get_organization(repo_or_org)
        org_stats = {}
        for repo in org.get_repos():
            print('')
            print('')
            print(f'Processing {repo.name}')
            try:
                os.mkdir(f'stats/{org.login.lower()}')
            except FileExistsError:
                pass
            stats = repo_stats(repo)
            with open(f'stats/{org.login.lower()}/'
                      f'{repo.name.lower()}.json', 'w') as f:
                f.write(json.dumps(stats, sort_keys=True, indent=2))
            org_stats[repo.name.lower()] = stats
            break

        print('')
        consolodate = input('Want me to combine all stats by user? y/n ')
        if consolodate.strip().lower() == 'y':
            users = {}
            for repo in org_stats:
                contribs = org_stats[repo]['contributors']
                for user in contribs:
                    if user not in users:
                        users[user] = {
                            'name': '',
                            'authored': {
                                'add': 0,
                                'del': 0,
                                'total': 0,
                            },
                            'co-authored': {
                                'add': 0,
                                'del': 0,
                                'total': 0,
                            },
                            'repos': []
                        }
                    if 'name' in contribs[user]:
                        users[user]['name'] = contribs[user]['name']
                    elif 'login' in contribs[user]:
                        users[user]['name'] = contribs[user]['login']
                    users[user]['authored']['add'] += contribs[user]['authored']['add']
                    users[user]['authored']['del'] += contribs[user]['authored']['del']
                    users[user]['authored']['total'] += contribs[user]['authored']['total']
                    users[user]['co-authored']['add'] += contribs[user]['co-authored']['add']
                    users[user]['co-authored']['del'] += contribs[user]['co-authored']['del']
                    users[user]['co-authored']['total'] += contribs[user]['co-authored']['total']
                    users[user]['repos'].append(repo)
            with open(f'stats/{org.login.lower()}/'
                      f'_org_stats.json', 'w') as f:
                f.write(json.dumps(stats, sort_keys=True, indent=2))


    print("\ndone, check stats folder for output")
