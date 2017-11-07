# cli-phisher

This is a small script to facilitate sending phishing emails using SMTP from the CLI. 

Cli-Phisher assumes that you've already got a phishing site up waiting to receive credentials, record statistics, etc. It only handles actually sending phishing emails.

## Install

Python 3 is recommended, I haven't really tested this with Python 2 but in theory it should work.

After cloning the repo, install the requirements with:

`pip install -r requirements.txt`

## Help

```
./cli-phisher.py --help
Usage: cli-phisher.py [OPTIONS] EMAIL

Options:
  -t, --test TEXT        Email address to send test message to. Multiple -t
                         options are allowed.
  --send                 Required command line option to arm email sending.
  --server TEXT          SMTP server to use (default: "default")
  -c, --config FILENAME  Configuration file name to use (default: config.yml)
  --help                 Show this message and exit.
```

## Instructions

1. Setup the config.yml file with your email server configuration. The example configuration included should be self-explanatory.
2. Next create an email template based on the included email.md, again the included example should be sufficient to illustrate how email templates work.
3. Create text file containing target email addresses (one per line) 
3. Send a test with `python3 cli-phisher.py -t test.user@domain.com email.md` (note: `-t <email>` can be used multiple times) 
4. Once you're satisfied with the message to send to all targets use the `--send` option. The script will double check you really want to send them.

## Template notes

When viewing the template in GitHub make sure you view it in raw mode because the front matter and comments get mangled by GitHub's Markdown interpreter.

UIDs are encrypted just to be sure that some smartypants that recognizes base64 won't be able to easily decipher them. You can generate a key like this:

```
from os import urandom

>>> key =  urandom(4)
>>> key 
b'\x94\xd0\xb3\x10'
```

Decrypting a uid fairly straightforward (I do this automatically with a Flask phishing site):

```
from Crypto.Cipher import ARC4
from base64 import urlsafe_b64decode
cipher = ARC4.new(key)

>>> cipher.decrypt(urlsafe_b64decode(uid))
b'test@test.com'
```

Right now only {{uid}} and {{firstname}} are customized for each message. This is something I will put more effort into improving in the future.

As it stands the firstname is taken from the email format firstname.lastname@domain.com. If you want to do it any other way, the only way is to dig into the Python code. This is really easy if you know a bit of Python. I have plans to fix this but wanted to commit the code sooner rather than later. 
