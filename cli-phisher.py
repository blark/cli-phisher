#!/usr/bin/env python3
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

class Mailer:
    def __init__(self):
        self.logger = logging.getLogger('mailer')
        handler = logging.FileHandler('emails.log')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

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
        if dbg:
            s.set_debuglevel(True)
        s.login(user, pw)
        return s

    def go(self, test, send, email, server, config):
        # load configuration file
        cfg = yaml.load(config)
        try:
            server = cfg['smtp'][server]
        except KeyError:
            click.secho('I can\'t find the SMTP server "{0}" in config.yml'.format(server), fg='red')
            raise click.Abort()
        # load email and related configuration
        front_matter, email_body = email.read().split('---')[1:3]
        email_cfg = yaml.load(front_matter)
        # load targets
        with open(email_cfg['targets']) as target_file:
            targets = [line.rstrip('\n') for line in target_file]
        click.secho('Read {0} targets from {1}'.format(len(targets), email_cfg['targets']))
        if test or send:
            click.secho('Initiating SMTP connection to {0}'.format(server['host']))
            smtp = self.smtp_connect(server['user'], server['pass'], server['host'], server['port'])
        # send test email
        for addr in test:
            click.secho('Sending test email to {0}'.format(addr), fg='green')
            self.send_email(smtp, addr, email_body, email_cfg)
        # send emails
        if send:
            if click.confirm('I\'m about to send emails, do you want to continue?'):
                with click.progressbar(targets, label='Sending emails',
                                       length=len(targets)) as bar:
                    for addr in bar:
                        self.send_email(smtp, addr, email_body, email_cfg)
            else:
                click.secho('Not sending any emails')
        else:
            click.secho('Cowardly refusing to send phishing emails without the --send flag...', fg='red')
        try:
            smtp.quit()
            click.secho('Closing connection to SMTP server')
        except NameError:
            pass

@click.command()
@click.argument('email', type=click.File('r'))
@click.option('--test', '-t', multiple=True, help='Email address to send test message to.'
              ' Multiple -t options are allowed.')
@click.option('--send', is_flag=True, default=False,
              help='Required command line option to arm email sending.')
@click.option('--server', default='default', help='SMTP server to use'
              ' (default: "default")')
@click.option('--config', '-c', default='config.yml', type=click.File('r'),
              help='Configuration file name to use (default: config.yml)')
def cli(test, send, email, server, config):
    mailer = Mailer()
    mailer.go(test, send, email, server, config)

if __name__ == '__main__':
    cli()
