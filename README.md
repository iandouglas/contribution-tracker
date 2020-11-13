# GitHub Contribution Tracker

Goal: scan an organization's repos to build some basic stats about who has contributed.

Secondary goal: enter a single repo to gain similar stats

## Installation and Setup

Requires Python 3.7 or newer

You will need to install the PyGithub module in the requirements file using
`pip`, preferably in a `pyenv` environment or `virtualenv` or `pipenv` setup.

To run:

```bash
python tracker.py
```

You will be prompted for an organization name or a repo name.

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
Then you will be prompted to enter an email address. This will not be saved
for subsequent runs.

Commits which are merges done on github.com (ie, merging a pull request) is
not counted toward anyone's total.

