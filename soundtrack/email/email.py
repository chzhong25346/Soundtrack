import smtplib
import logging
import yaml,os
import sys
import pandas as pd
import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil import parser
from ..models import Holding, Report
logger = logging.getLogger('main.email')

def sendMail(object, session):
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
    rcpt = object.EMAIL_TO
    try:
        s.login(user,pwd)
    except Exception as e:
        logger.error(e)

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = today
    msg['From'] = user
    msg['To'] = rcpt

    html = generate_html(session)
    attachment = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(attachment)

    # send the email
    s.sendmail(user, rcpt, msg.as_string())
    # we're done
    s.quit()


def generate_html(session):
    # Nasdaq100
    tsxci_holding = pd.read_sql(session.query(Holding).statement, session.bind, index_col='symbol')
    uptrend = [Report.symbol for Report in session.query(Report).filter(Report.uptrend == 1)]
    downtrend = [Report.symbol for Report in session.query(Report).filter(Report.downtrend == 1)]
    high_volume = [Report.symbol for Report in session.query(Report).filter(Report.high_volume == 1)]

    html = """\
    <html>
    <head></head>
    <body>
        <h3>NASDAQ 100</h3>
        {tsxci_holding}<br>
        <table border="1" class="dataframe">
          <tr>
            <th>Uptrend:</th>
            <td>{uptrend}</td>
          </tr>
          <tr>
            <th>Downtrend:</th>
            <td>{downtrend}</td>
          </tr>
          <tr>
            <th>High Volume:</th>
            <td>{high_volume}</td>
          </tr>
        </table>
    </body>
    </html>
    """

    html = html.format(tsxci_holding=tsxci_holding.to_html(),
                      uptrend=",".join(uptrend),
                      downtrend=",".join(downtrend),
                      high_volume=",".join(high_volume))

    return html
