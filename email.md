---
#
# this is a yaml front matter, for setting email configuration variables.
#
name: test
from: Example User <example@phishing.com>
subject: This is a test email
targets: test_targets.txt
key: b'\x04\xfad\xe5'
# provide a python function to return the first name from the email address. the function will be passed the email as an argument
get_name: "lambda e: e.split('.')[0]"
#
# everything below the three dashes is the phishing email body (using Markdown) 
# it will be converted to HTML before sending the email.
#
---
Dear {{firstname}},

Example email body text.

[Example phishing link using markdown](http://test.com/test?uid={{uid}})

Regards,
Test

--  
Signature  
Goes  
Here
