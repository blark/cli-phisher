# cli-phisher

This is a small script to facilitate sending phishing emails from the CLI.

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
2. Next create an email template based on the included email.md, again it should be pretty straightforward.
3. Create text file containing target email addresses (one per line)
3. Send a test with `python3 cli-phisher.py -t test.user@domain.com` (note: `-t <email>` can be used multiple times)
4. Once you're satisfied with the message to send to all targets use the `--send` option. The script will double check you really want to send them.

## Template notes

The UID is encrypted just to be sure that some smartypants that recognizes base64 won't be able to read them. You can generate a key like this:

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
