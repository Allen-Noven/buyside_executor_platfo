# ====================================
# email_service.py
# ====================================

import smtplib

from email.mime.text import (
    MIMEText
)

from email.mime.multipart import (
    MIMEMultipart
)

from utils.config import (

    EMAIL_SENDER,

    EMAIL_PASSWORD,

    PM_EMAIL,

    TRADER_EMAIL
)

from utils.logger import (
    SystemLogger
)


class EmailService:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # EMAIL CONFIG
        # ====================================

        self.sender = (
            EMAIL_SENDER
        )

        self.password = (
            EMAIL_PASSWORD
        )


        # ====================================
        # DEFAULT RECIPIENTS
        # ====================================

        self.default_recipients = [

            PM_EMAIL,

            TRADER_EMAIL
        ]


    # ====================================
    # SEND EMAIL ALERT
    # ====================================

    def send_alert(

        self,

        subject,

        body,

        recipients=None,

        severity="WARNING"

    ):

        # ====================================
        # DEFAULT RECIPIENTS
        # ====================================

        if recipients is None:

            recipients = (
                self.default_recipients
            )


        # ====================================
        # BUILD MESSAGE
        # ====================================

        message = MIMEMultipart()

        message["From"] = (
            self.sender
        )

        message["To"] = (
            ", ".join(recipients)
        )

        message["Subject"] = (

            f"[{severity}] "
            f"{subject}"
        )


        # ====================================
        # ATTACH BODY
        # ====================================

        message.attach(

            MIMEText(

                body,

                "plain"
            )
        )


        # ====================================
        # SEND EMAIL
        # ====================================

        try:

            server = smtplib.SMTP(

                "smtp.gmail.com",

                587
            )

            server.starttls()

            server.login(

                self.sender,

                self.password
            )

            server.sendmail(

                self.sender,

                recipients,

                message.as_string()
            )

            server.quit()


            self.logger.info(

                f"Email Alert Sent | "

                f"{subject}"
            )


        except Exception as e:

            self.logger.error(

                f"Email Sending Failed | "
                f"{e}"
            )


    # ====================================
    # SEND KILL SWITCH ALERT
    # ====================================

    def send_kill_switch_alert(

        self,

        symbol,

        reason

    ):

        subject = (

            f"Execution Halted | "
            f"{symbol}"
        )


        body = f"""

Execution Halt Triggered.

Symbol:
{symbol}

Reason:
{reason}

Action Taken:
All child-order execution halted.

Please investigate immediately.

"""


        self.send_alert(

            subject=subject,

            body=body,

            severity="CRITICAL"
        )


    # ====================================
    # SEND PNL ALERT
    # ====================================

    def send_pnl_alert(

        self,

        pnl_summary

    ):

        subject = (
            "PnL Alert"
        )


        body = f"""

PnL Threshold Alert.

Position:
{pnl_summary['position']}

Realized PnL:
{pnl_summary['realized_pnl']}

Unrealized PnL:
{pnl_summary['unrealized_pnl']}

Total PnL:
{pnl_summary['total_pnl']}

"""


        self.send_alert(

            subject=subject,

            body=body,

            severity="WARNING"
        )


    # ====================================
    # SEND NEWS RISK ALERT
    # ====================================

    def send_news_alert(

        self,

        news_event

    ):

        subject = (

            f"News Risk Alert | "

            f"{news_event['symbol']}"
        )


        body = f"""

Potential Risk News Detected.

Headline:
{news_event['headline']}

Risk Keywords:
{news_event['risk_keywords']}

Source:
{news_event['source']}

URL:
{news_event['url']}

"""


        self.send_alert(

            subject=subject,

            body=body,

            severity="CRITICAL"
        )