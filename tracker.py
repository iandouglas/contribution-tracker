import json
import os
import sys
from os import path
import getopt
import github

try:
    users_file = open('users.json', 'r')
    global_users = json.loads(users_file.read())
except FileNotFoundError:
    f = open('users.json', 'w')
    f.write('{}')
    f.close()
try:
    emails_file = open('emails.json', 'r')
    global_emails = json.loads(emails_file.read())
except FileNotFoundError:
    f = open('emails.json', 'w')
    f.write('{}')
    f.close()

verbose = False
check_for_coauthor_commits = True
strip_coauthor_if_none = True
repo = None
org = None
repo_or_org = None
combine_user_stats = True
ignore_users = []

def printv(msg):
    if verbose:
        print(msg)


def repo_stats(repo):
    emails = {}
    contributors = {}
    coauthor_messages_found = False
    for contributor in repo.get_contributors():
        login = contributor.login.lower()
        if login in ignore_users:
            continue
        if login not in contributors:
            contributors[login] = {
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
        contributors[login]['emails'] = [anon_email]
        emails[anon_email] = login
        if contributor.email is not None:
            email = contributor.email.lower()
            contributors[login]['emails'].append(email)
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
        if login in ignore_users:
            continue
        if login == 'web-flow':
            # skip merge commits done on GitHub
            continue

        contributors[login]['authored']['add'] += stats.additions
        contributors[login]['authored']['del'] += stats.deletions
        contributors[login]['authored']['total'] += stats.total

        if not check_for_coauthor_commits:
            continue

        coauthors = [login]
        new_msg = []
        if 'Co-authored-by' in message:
            combine = False
            for line in message.split("\n"):
                if 'Co-authored-by' not in line and not combine:
                    new_msg.append(line)
                if 'Co-authored-by' not in line and combine:
                    combine = False
                    prev_line = new_msg.pop()
                    prev_line += ' ' + line
                    new_msg.append(prev_line)
                if 'Co-authored-by' in line and '<' not in line:
                    combine = True
                    new_msg.append(line)
        message = "\n".join(new_msg)
        # print(message)
        for line in message.split("\n"):
            email = None
            if 'Co-authored-by' in line:
                coauthor_messages_found = True
                try:
                    first = line.split('<')
                    try:
                        second = first[1]
                        third = second.split('>')
                        fourth = third[0]
                        email = fourth.lower()
                    except IndexError:
                        print('-'*100)
                        print(login)
                        print(message)
                        print('-'*100)
                except IndexError:
                    name = lines.split("-by: ")[1]
                    if name not in global_emails:
                        print('')
                        print('-' * 10)
                        print(f'{login} made a commit that cannot be processed:')
                        print(message)
                        print('')
                        print('specifically, this line:')
                        print(line)
                        email = input('please enter an email to use here: ')
                        remember = input('remember for next time? y/n ')
                        remember = remember.strip().lower()
                        if remember == 'y':
                            global_emails[name] = email
                            gusers_file = open('emails.json', 'w')
                            gusers_file.write(json.dumps(
                                global_emails, sort_keys=True, indent=2)
                            )
                            gusers_file.close()
                    else:
                        email = global_emails[name]
                login = None
                if email in emails:
                    if emails[email] == user.login.lower():
                        continue
                else:
                    if email is None:
                        continue
                    if email not in global_users:
                        print('found a contributor email that did not match:')
                        print(line)
                        login = input(f'enter github username for {email}: ')
                        emails[email] = login.strip().lower()
                        remember = input('remember for next time? y/n ')
                        remember = remember.strip().lower()
                        if remember == 'y':
                            global_users[email] = login
                            gusers_file = open('users.json', 'w')
                            gusers_file.write(json.dumps(
                                global_users, sort_keys=True, indent=2)
                            )
                            gusers_file.close()
                    emails[email] = global_users[email]
                co_author = emails[email]
                if co_author in ignore_users:
                    continue
                if co_author not in contributors:
                    contributors[co_author] = {
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
                if co_author in coauthors:
                    continue
                else:
                    coauthors.append(co_author)
                    contributors[co_author]['co-authored']['add'] += \
                        stats.additions
                    contributors[co_author]['co-authored']['del'] += \
                        stats.deletions
                    contributors[co_author]['co-authored']['total'] += \
                        stats.additions - stats.deletions

    if strip_coauthor_if_none and not coauthor_messages_found:
        for contributor in contributors:
            del contributors[contributor]['co-authored']

    details = {
        'archived': repo.archived,
        'contributors': contributors
    }

    return details


def usage():
    print('GitHub Contribution Tracker')
    print('')
    print('Usage: tracker.py [-v] [options] github_url')
    print('-v          turn on verbose output')
    print('-i          turn on interactive mode')
    print('')
    print('-c          scan commit messages for co-author commits')
    print('--coauthor  scan commit messages for co-author commits')
    print('            default behavior is to scan for co-author commits')
    print('')
    print('-g=user1,user2               ignore a comma-delimited list of github usernames')
    print('--ignore-users=user1=user2   ignore a comma-delimited list of github usernames')
    print('')
    print('--skip-coauthor       skip processing commit messages for co-authors')
    print('')
    print('--skip-coauth-stats   remove co-author stats if there are none')
    print('                      default is to suppress stats if there are none')


if __name__ == '__main__':
    interactive_mode = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcviu:g", ['help', 'combine-user-stats', 'ignore-users=', 'do-coauthor', 'skip-coauthor', 'skip-coauth-stats'])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == '-v':
            verbose = True
        if o == '-i':
            interactive_mode = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-u', '--combine-user-stats'):
            combine_user_stats = True
        elif o in ('-g', '--ignore-users'):
            print(a)
            ignore_users = [x.lower().strip() for x in a.split(',')]
        elif o in ('-c', '--do-coauthor'):
            check_for_coauthor_commits = True
            strip_coauthor_if_none = True
        elif o in ('--skip-coauthor'):
            check_for_coauthor_commits = False
            strip_coauthor_if_none = True
        elif o in ('--skip-coauth-stats'):
            strip_coauthor_if_none = True
    
    if len(args):
        repo_or_org = args[0]

    if verbose:
        print('repo:', repo_or_org)
        print('check co-author:', check_for_coauthor_commits)
        print('skip coauth stats:', strip_coauthor_if_none)
        print('ignoring users:', ignore_users)
        print('')

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

    if interactive_mode or repo_or_org is None:
        repo_or_org = input(
            'Enter full GitHub Organization or Repo URL, ie "https://github.com/turingschool" or '
            '"https://github.com/turingschool/backend-curriculum-site": '
        )

        repo_or_org = repo_or_org.strip()

        print(f'Checking {repo_or_org} for access...')

    g = github.Github(access_token)

    if interactive_mode:
        check_for_coauthor_commits = input('Should commit messages be scanned for '
                                        'Co-authored-by tags? y/n ')
        if check_for_coauthor_commits.strip().lower() == 'y':
            check_for_coauthor_commits = True
            strip_coauthor_if_none = input('Should co-author data blocks be '
                                        'removed if none are found? y/n ')
            if strip_coauthor_if_none.strip().lower() == 'n':
                strip_coauthor_if_none = False

    slashes = sum(map(lambda x: 1 if '/' in repo_or_org else 0, repo_or_org))
    repo_or_org = repo_or_org.replace('https://github.com/', '')
    if slashes > 3:
        printv('getting stats for single repo')
        try:
            repo = g.get_repo(repo_or_org)
        except github.GithubException.UnknownObjectException:
            print('Sorry, that repo cannot be found, check spelling or '
                  'make sure you have access to the repo')
            sys.exit()

        r_stats = repo_stats(repo)
        org_name = repo_or_org.split("/")[0].lower()
        try:
            os.mkdir(f'stats/{org_name}')
        except FileExistsError:
            pass
        with open(f'stats/{org_name}/{repo.name.lower()}.json', 'w') as f:
            f.write(json.dumps(r_stats, sort_keys=True, indent=2))

    else:
        printv('getting stats for organization')
        try:
            org = g.get_organization(repo_or_org)
        except github.GithubException.UnknownObjectException:
            print('Sorry, that organization cannot be found, check spelling '
                  'or make sure you have access to the organization')
            sys.exit()

        org_stats = {}
        for repo in org.get_repos():
            printv('')
            printv('')
            printv(f'Processing {repo.name}')
            try:
                os.mkdir(f'stats/{org.login.lower()}')
            except FileExistsError:
                pass
            r_stats = repo_stats(repo)
            with open(f'stats/{org.login.lower()}/'
                      f'{repo.name.lower()}.json', 'w') as f:
                f.write(json.dumps(r_stats, sort_keys=True, indent=2))
            org_stats[repo.name.lower()] = r_stats

        printv('')
        printv('')
        if interactive_mode:
            consolidate = input('Want me to combine all stats by user? y/n ')
            skip_archived = 'n'
            for repo in org_stats:
                if org_stats[repo]['archived']:
                    skip_archived = input('Skip archived repos? y/n ')
                    skip_archived = skip_archived.strip().lower()
                    break

        if combine_user_stats or (interactive_mode and consolidate.strip().lower() == 'y'):
            users = {}
            for repo in org_stats:
                if org_stats[repo]['archived'] and skip_archived == 'y':
                    continue
                contributors = org_stats[repo]['contributors']
                for user in contributors:
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
                    if 'name' in contributors[user]:
                        users[user]['name'] = contributors[user]['name']
                    elif 'login' in contributors[user]:
                        users[user]['name'] = contributors[user]['login']
                    users[user]['authored']['add'] += \
                        contributors[user]['authored']['add']
                    users[user]['authored']['del'] += \
                        contributors[user]['authored']['del']
                    users[user]['authored']['total'] += \
                        contributors[user]['authored']['total']
                    if 'co-authored' in contributors[user]:
                        users[user]['co-authored']['add'] += \
                            contributors[user]['co-authored']['add']
                        users[user]['co-authored']['del'] += \
                            contributors[user]['co-authored']['del']
                        users[user]['co-authored']['total'] += \
                            contributors[user]['co-authored']['total']
                    users[user]['repos'].append(repo)

            with open(f'stats/{org.login.lower()}/'
                      f'_org_stats.json', 'w') as f:
                f.write(json.dumps(users, sort_keys=True, indent=2))
    print('')
    print("done, check stats folder for output")
