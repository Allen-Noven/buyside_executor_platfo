# ====================================
# news_monitor.py
# ====================================

import requests

from datetime import (

    datetime,

    timedelta
)

from utils.config import (

    FINNHUB_API_KEY,

    NEWS_PROVIDER
)

from utils.logger import (
    SystemLogger
)


class NewsMonitor:

    def __init__(self):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )


        # ====================================
        # NEWS PROVIDER
        # ====================================

        self.provider = (
            NEWS_PROVIDER
        )

        self.api_key = (
            FINNHUB_API_KEY
        )


        # ====================================
        # TRACK LAST HEADLINE
        # ====================================

        self.last_headline = None


    # ====================================
    # FETCH COMPANY NEWS
    # ====================================

    def fetch_company_news(

        self,

        symbol,

        days_back=1

    ):

        # ====================================
        # DYNAMIC DATE RANGE
        # ====================================

        end_date = (
            datetime.utcnow()
        )

        start_date = (

            end_date
            - timedelta(days=days_back)
        )


        # ====================================
        # FINNHUB URL
        # ====================================

        url = (

            "https://finnhub.io/api/v1/company-news"
        )


        params = {

            "symbol":
            symbol,

            "from":
            start_date.strftime(
                "%Y-%m-%d"
            ),

            "to":
            end_date.strftime(
                "%Y-%m-%d"
            ),

            "token":
            self.api_key
        }


        self.logger.info(

            f"Fetching News | "
            f"{symbol}"
        )


        response = requests.get(

            url,

            params=params
        )


        # ====================================
        # API FAILURE
        # ====================================

        if response.status_code != 200:

            self.logger.error(

                "News API Error"
            )

            return []


        return response.json()


    # ====================================
    # GET LATEST HEADLINE
    # ====================================

    def get_latest_headline(

        self,

        symbol

    ):

        news_data = (

            self.fetch_company_news(
                symbol
            )
        )


        if len(news_data) == 0:

            self.logger.warning(

                "No News Found"
            )

            return None


        latest_news = news_data[0]


        headline = (

            latest_news.get(
                "headline",
                ""
            )
        )


        # ====================================
        # DUPLICATE FILTER
        # ====================================

        if headline == self.last_headline:

            return None


        self.last_headline = (
            headline
        )


        # ====================================
        # BUILD EVENT
        # ====================================

        news_event = {

            "symbol":
            symbol,

            "headline":
            headline,

            "summary":
            latest_news.get(
                "summary",
                ""
            ),

            "source":
            latest_news.get(
                "source",
                ""
            ),

            "url":
            latest_news.get(
                "url",
                ""
            ),

            "datetime":
            latest_news.get(
                "datetime",
                ""
            ),

            "risk_keywords":
            self.extract_risk_keywords(
                headline
            )
        }


        self.logger.info(

            f"News Event Detected | "

            f"{headline}"
        )

        return news_event


    # ====================================
    # RISK KEYWORD EXTRACTION
    # ====================================

    def extract_risk_keywords(

        self,

        headline

    ):

        risk_keywords = [

            "investigation",

            "SEC",

            "DOJ",

            "fraud",

            "bankruptcy",

            "lawsuit",

            "probe",

            "hack",

            "liquidity crisis"
        ]


        detected_keywords = []


        headline_lower = (
            headline.lower()
        )


        for keyword in risk_keywords:

            if keyword.lower() in headline_lower:

                detected_keywords.append(
                    keyword
                )


        return detected_keywords


    # ====================================
    # SHOW NEWS
    # ====================================

    def show_news(

        self,

        news_event

    ):

        if news_event is None:

            return


        print(

            "\n========== NEWS EVENT ==========\n"
        )

        print(

            f"Symbol: "
            f"{news_event['symbol']}"
        )

        print(

            f"Headline: "
            f"{news_event['headline']}"
        )

        print(

            f"Source: "
            f"{news_event['source']}"
        )

        print(

            f"Risk Keywords: "
            f"{news_event['risk_keywords']}"
        )

        print(

            f"Summary: "
            f"{news_event['summary']}"
        )

        print(

            f"URL: "
            f"{news_event['url']}"
        )

        print(

            "\n================================\n"
        )