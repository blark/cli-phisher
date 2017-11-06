---
name: test_campaign
from: Example <example@securefile.io>
subject: This is a test email
url: "http://test.com/test?uid={{uid}}"
targets: test_targets.txt
---
Dear {{firstname}},

Example email body text.

[Example phishing link using markdown]({{url}})

Regards,
Test

--  
Signature  
Goes  
Here
