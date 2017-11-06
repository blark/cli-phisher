---
name: test_campaign
from: Example <example@securefile.io>
subject: This is a test email
targets: test_targets.txt
key: b'\x04\xfad\xe5' 
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
