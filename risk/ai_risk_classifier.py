# ====================================
# ai_risk_classifier.py
# ====================================

import json
import requests

from utils.config import (
    DEEPSEEK_API_KEY
)

from utils.constants import (
    AI_RISK_EVENT
)

from utils.logger import (
    SystemLogger
)
from core.redis_state import RedisState

class AIRiskClassifier:

    def __init__(

        self,

        event_bus=None

    ):

        # ====================================
        # LOGGER
        # ====================================

        self.logger = (
            SystemLogger()
        )

        # ====================================
        # EVENT BUS
        # ====================================

        self.event_bus = (
            event_bus
        )

        # ====================================
        # DEEPSEEK CONFIG
        # ====================================

        self.api_key = (
            DEEPSEEK_API_KEY
        )

        self.url = (
            "https://api.deepseek.com/chat/completions"
        )
# ====================================
# REDIS STATE
# ====================================

        self.redis_state = RedisState()

    # ====================================
    # SAFE DEFAULT RESPONSE
    # ====================================

    def get_safe_default(self):

        return {

            "severity":
            "UNKNOWN",

            "halt_execution":
            False,

            "liquidity_risk":
            False,

            "volatility_risk":
            False,

            "recommended_action":
            "MONITOR",

            "confidence":
            0.0,

            "reason":
            "AI classification unavailable"
        }


    # ====================================
    # VALIDATE AI RESPONSE
    # ====================================

    def validate_response(

        self,

        result

    ):

        required_fields = [

            "severity",

            "halt_execution",

            "liquidity_risk",

            "volatility_risk",

            "recommended_action",

            "confidence",

            "reason"
        ]

        for field in required_fields:

            if field not in result:

                return False

        return True


    # ====================================
    # CLASSIFY NEWS
    # ====================================

    def classify_news(

        self,

        news_event

    ):

        headline = (
            news_event["headline"]
        )

        summary = (
            news_event["summary"]
        )

        # ====================================
        # PROMPT
        # ====================================

        prompt = f"""

You are an institutional
execution risk analyst.

Analyze the following market news.

Headline:
{headline}

Summary:
{summary}

Determine:

1. Risk severity:
LOW / MEDIUM / HIGH

2. Should execution halt?
true / false

3. Is liquidity risk elevated?
true / false

4. Is volatility risk elevated?
true / false

5. Recommended execution action:
HALT /
REDUCE_AGGRESSION /
SWITCH_TO_ICEBERG /
MONITOR

6. Confidence score:
0.0 to 1.0

7. Short reasoning.

Return ONLY valid JSON.

Example:

{{
    "severity": "HIGH",

    "halt_execution": true,

    "liquidity_risk": true,

    "volatility_risk": true,

    "recommended_action":
    "HALT",

    "confidence": 0.97,

    "reason":
    "Potential DOJ investigation"
}}

"""

        # ====================================
        # HEADERS
        # ====================================

        headers = {

            "Authorization":
            f"Bearer {self.api_key}",

            "Content-Type":
            "application/json"
        }

        # ====================================
        # PAYLOAD
        # ====================================

        payload = {

            "model":
            "deepseek-chat",

            "messages": [

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            "temperature": 0
        }

        try:

            # ====================================
            # SEND REQUEST
            # ====================================

            response = requests.post(

                self.url,

                headers=headers,

                json=payload,

                timeout=10
            )

            # ====================================
            # API FAILURE
            # ====================================

            if response.status_code != 200:

                self.logger.error(

                    f"AI Classification Failed | "

                    f"{response.text}"
                )

                return self.get_safe_default()

            result = response.json()

            # ====================================
            # EXTRACT CONTENT
            # ====================================

            content = (

                result["choices"][0]
                ["message"]["content"]
            )

            # ====================================
            # PARSE JSON
            # ====================================

            classification = (
                json.loads(content)
            )

            # ====================================
            # VALIDATE
            # ====================================

            if not self.validate_response(
                classification
            ):

                self.logger.error(

                    "AI Response Validation Failed"
                )

                return self.get_safe_default()

            # ====================================
            # LOG RESULT
            # ====================================

            self.logger.info(

                f"AI Risk Classified | "

                f"Severity: "

                f"{classification['severity']}"
            )
            
            # ====================================
            # SYNC AI RISK TO REDIS
            # ====================================

            self.redis_state.set_ai_risk_result(
                classification
            )


            # ====================================
            # PUBLISH EVENT
            # ====================================

            if self.event_bus:

                self.event_bus.publish(

                    AI_RISK_EVENT,

                    classification
                )

            return classification

        except Exception as e:

            self.logger.error(

                f"AI Risk Engine Error | "
                f"{e}"
            )

            return self.get_safe_default()


    # ====================================
    # SHOW RESULT
    # ====================================

    def show_classification(

        self,

        result

    ):

        if result is None:

            return

        print(

            "\n========== AI RISK ANALYSIS ==========\n"
        )

        print(

            f"Severity: "
            f"{result['severity']}"
        )

        print(

            f"Halt Execution: "
            f"{result['halt_execution']}"
        )

        print(

            f"Liquidity Risk: "
            f"{result['liquidity_risk']}"
        )

        print(

            f"Volatility Risk: "
            f"{result['volatility_risk']}"
        )

        print(

            f"Recommended Action: "
            f"{result['recommended_action']}"
        )

        print(

            f"Confidence: "
            f"{result['confidence']}"
        )

        print(

            f"Reason: "
            f"{result['reason']}"
        )

        print(

            "\n======================================\n"
        )