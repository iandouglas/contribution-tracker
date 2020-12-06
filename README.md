# GitHub Contribution Tracker

Goal: scan an organization's repos to build some basic stats about who has contributed.

Secondary goal: enter a single repo to gain similar stats

## Installation and Setup

Requires Python 3.7 or newer

You will need to install the PyGithub module in the requirements file using
`pip`, preferably in a `pyenv` environment or `virtualenv` or `pipenv` setup.

You'll need to create a file called `auth.py` which contains a personal access
token in order to use GitHub's API to pull these stats. The format of the file
will look like this:
```python
access_token = "abc123"
```

Get an access token from https://github.com/settings/tokens/new and give it 
full "repo" and "admin:org" scopes.

If you don't have this file, you'll be prompted by the software to create it
and include it.

## To run the tracker

```bash
python tracker.py -h h
```
The `-h` switch will display command-line help.

Typical usage will be something like this:

```
python tracker.py https://github.com/iandouglas/contribution-tracker
```

There are switches to turn on/off co-author checking, supression of stats if no co-authoring was done, and more.

If you include the `-i` switch, the application will run in 'interactive' mode.

You will be prompted for a URL of a GitHub organization name or a repo name, for example:

Organization:
* https://github.com/TuringSchool

or

Individual Repo:
* https://github.com/iandouglas/contribution-tracker

If co-authored commits are used, it will attempt to parse those. However, if
the GitHub user hides their email address from being public and your commit
message uses their real email address, we can only construct their "anonymous"
GitHub email (like `168030+iandouglas@users.noreply.github.com`) and you will
be prompted to enter the GitHub username that matches the real email address.
You will then be prompted for whether you want to save this email address for
the next time you run the software. If you say yes to this prompt, it will be
saved in the `users.json` file.

Likewise, if the co-authored-by string doesn't follow the proper syntax of
```
Co-authored-by: Real Name <email@address.com>
```
Then you will be prompted to enter an email address. You will be asked if you want to save this for the future.

Since some plugins for Atom and VS Code are notorious for wrapping co-author lines onto new lines, the application will do its best to spot when this is happening, and correct the commit message.

Commits which are merges done on github.com (ie, merging a pull request) is
not counted toward anyone's total.

## Output Format

Each repo will have a JSON file output under the `stats/` folder. If you
run the script for a whole organization (*) then you'll get a file for each
repo and prompted whether to consolidate the stats per user afterward.

The format for a single repo will look like this:
```json
{
  "archived": false,
  "contributors": {
    "iandouglas": {
      "authored": {
        "add": 9792,
        "del": 678,
        "total": 10470
      },
      "co-authored": {
        "add": 0,
        "del": 0,
        "total": 0
      },
      "emails": [
        "168030+iandouglas@users.noreply.github.com"
      ],
      "name": "ian douglas"
    }
  }
}
```

Consolidated organization output will look like:

```json
{
  "iandouglas": {
    "authored": {
      "add": 6669,
      "del": 1545,
      "total": 8214
    },
    "co-authored": {
      "add": 3162,
      "del": 29,
      "total": 3191
    },
    "name": "Ian Douglas",
    "repos": [
      "front_end",
      "microservice",
      "backend"
    ]
  }
}
```

The consolidation process will also prompt you if you want to skip any "archived"
repos

---

(*) you're on your own for hitting rate limits on the API.

## Future Feature Ideas

* if co-author commits are going to be scanned:
  * better handling of repetitive errors in co-author commits
* move users with no contributions to a different subset of the data structure
* prompt users to sort the data by contribution counts instead of alphabetical
* if a repo was forked, only draw stats from the data the repo was forked, if
  that information is available
