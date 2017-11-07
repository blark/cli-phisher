#!/usr/bin/env python3
import sys
import yaml
import smtplib
from base64 import urlsafe_b64encode
from Crypto.Cipher import ARC4
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import logging
import click
from markdown import markdown

class CliPhisher:
    def __init__(self, config, email, server, test, send):
        # load SMTP configuration file
        cfg = yaml.load(config)
        try:
            self.server = cfg['smtp'][server]
        except KeyError:
            click.secho('I can\'t find the SMTP server "{0}" in config.yml'.format(server), fg='red')
            raise click.Abort()
        # load email and related configuration
        front_matter, self.email_body = email.read().split('---')[1:3]
        self.email_cfg = yaml.load(front_matter)
        # load targets
        self.targets = self.load_targets(self.email_cfg['targets'])
        # configure logger
        self.logger = logging.getLogger('mailer')
        handler = logging.FileHandler('{0}.log'.format(self.email_cfg['name']))
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.smtp_log = open('{0}_smtp.log'.format(self.email_cfg['name']), 'a')
        sys.stderr = self.smtp_log
        # start sending tests / phishing emails
        self.go(test, send)

    def load_targets(self, f):
        """ Eventually this function will be used to create a dict for each target as it is loaded
            the dict will be passed to the send_email func to customize each phishing email.
        """
        with open(f) as target_file:
            targets = [line.rstrip('\n') for line in target_file]
        click.secho('Read {0} targets from {1}'.format(len(targets), self.email_cfg['targets']))
        return targets

    def uid(self, addr, key):
        # encrypt email address with RC4 and then base64 encode it
        cipher = ARC4.new(key)
        return urlsafe_b64encode(cipher.encrypt(addr)).decode('utf-8')

    def send_email(self, smtp, to_addr, body, email_cfg):
        from_addr = email_cfg['from']
        subject = email_cfg['subject']
        # insert customizations into email here
        first_name = to_addr.split('.')[0].capitalize()
        body = body.replace('{{firstname}}', first_name)
        body = body.replace('{{uid}}', self.uid(to_addr, email_cfg['key']))
        # end email customizations
        msg = MIMEMultipart('related')
        msg['To'] = to_addr
        msg['From'] = from_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(markdown(body), 'html'))
        smtp.sendmail(from_addr, to_addr, msg.as_string())
        self.logger.info('Sent email to {0}'.format(to_addr))
        self.logger.debug('Email body:\n{0}'.format(body))
        return

    def smtp_connect(self, user, pw, server, port, dbg=False):
        s = smtplib.SMTP_SSL(host=server, port=port)
        if True:
            s.set_debuglevel(2)
        s.login(user, pw)
        return s

    def go(self, test, send):
        server = self.server
        # establish connection to SMTP server if necessary
        if test or send:
            click.secho('Initiating SMTP connection to {0}'.format(server['host']))
            smtp = self.smtp_connect(server['user'], server['pass'], server['host'], server['port'])
        else:
            click.secho('No emails to send.')
        # send test email
        for addr in test:
            click.secho('Sending test email to {0}'.format(addr), fg='green')
            self.send_email(smtp, addr, self.email_body, self.email_cfg)
        # send emails
        if send:
            if click.confirm('I\'m about to send emails, do you want to continue?'):
                with click.progressbar(self.targets, label='Sending emails',
                                       length=len(self.targets)) as bar:
                    for addr in bar:
                        self.send_email(smtp, addr, self.email_body, self.email_cfg)
            else:
                click.secho('Not sending any emails')
        else:
            click.secho('Cowardly refusing to send phishing emails without the --send flag...', fg='red')
        try:
            smtp.quit()
            click.secho('Closing connection to SMTP server')
        except NameError:
            pass
        self.smtp_log.close()


@click.command()
@click.argument('email', type=click.File('r'))
@click.option('--test', '-t', multiple=True, help='Email address to send test message to.'
              ' Multiple -t options are allowed (--send is not required for test emails).')
@click.option('--send', is_flag=True, default=False,
              help='Required command line option to arm email sending.')
@click.option('--server', default='default', help='SMTP server to use'
              ' (default: "default")')
@click.option('--config', '-c', default='config.yml', type=click.File('r'),
              help='Configuration file name to use (default: config.yml)')
def cli(test, send, email, server, config):
    mailer = CliPhisher(config, email, server, test, send)

if __name__ == '__main__':
    cli()
