import smtplib
import logging
import yaml,os
import sys
import pandas as pd
import datetime as dt
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil import parser
from ..models import Holding, Report
logger = logging.getLogger('main.email')

def sendMail(object, s_nasdaq, s_tsxci):
    # today's datetime
    day = dt.datetime.today().strftime("%Y-%m-%d")
    dow = parser.parse(day).strftime("%a")
    today = day + ' ' + dow
    # start talking to the SMTP server for Gmail
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.ehlo()
    # now login as my gmail user
    user = object.EMAIL_USER
    pwd = object.EMAIL_PASS
    # rcpt = object.EMAIL_TO
    rcpt = [i for i in object.EMAIL_TO.split(',')]
    try:
        s.login(user,pwd)
    except Exception as e:
        logger.error(e)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = today
    msg['From'] = user
    msg['To'] = ", ".join(rcpt)

    html = generate_html(s_nasdaq, s_tsxci)
    attachment = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(attachment)

    # send the email
    s.sendmail(user, rcpt, msg.as_string())
    # we're done
    s.quit()


def generate_html(s_nasdaq, s_tsxci):
    # Nasdaq100
    nasdaq_holding = pd.read_sql(s_nasdaq.query(Holding).statement, s_nasdaq.bind, index_col='symbol')
    # nasdaq_uptrend = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.uptrend == 1)]
    # nasdaq_downtrend = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.downtrend == 1)]
    # nasdaq_high_volume = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.high_volume == 1)]
    # nasdaq_support = [Report.symbol for Report in s_nasdaq.query(Report).filter(Report.support == 1)]
    # TSXCI
    tsxci_holding = pd.read_sql(s_tsxci.query(Holding).statement, s_tsxci.bind, index_col='symbol')
    # tsxci_uptrend = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.uptrend == 1)]
    # tsxci_downtrend = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.downtrend == 1)]
    # tsxci_high_volume = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.high_volume == 1)]
    # tsxci_support = [Report.symbol for Report in s_tsxci.query(Report).filter(Report.support == 1)]

    html = """\
    <html>
    <head></head>
    <body>
        <h3>NASDAQ 100</h3>
        {nasdaq_holding}<br>

        <h3>TSXCI</h3>
        {tsxci_holding}<br>

        <p>{trade_list}</p>

    </body>
    </html>
    """

    html = html.format(nasdaq_holding=nasdaq_holding.to_html(),
                      tsxci_holding=tsxci_holding.to_html(),
                      trade_list = read_log()
                      )

    return html


def read_log():
    s = 'DEBUG - '
    html =''
    day = dt.datetime.today().strftime("%Y-%m-%d")
    fh = open('log.log', 'r')
    with fh as file:
        for line in file:
            if((day in line) and ('Half' in line) or ('All' in line) ):
                html += "<li>" + line[line.index(s) + len(s):] + "</li>"
    fh.close()

    return html
