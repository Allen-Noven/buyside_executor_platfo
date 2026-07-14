# ====================================
# reconciliation_worker.py
# ====================================

import threading
import time

from utils.logger import (
    SystemLogger
)


class ReconciliationWorker:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        broker_position_service,

        reconciliation_engine,

        interval=30
    ):

        self.logger = (
            SystemLogger()
        )

        self.broker_position_service = (
            broker_position_service
        )

        self.reconciliation_engine = (
            reconciliation_engine
        )

        self.interval = (
            interval
        )

        self.running = False

        self.thread = None


    # ====================================
    # RUN LOOP
    # ====================================

    def run(self):

        self.logger.info(
            "Reconciliation Worker Started"
        )

        while self.running:

            try:

                # ====================================
                # REFRESH BROKER POSITIONS
                # ====================================

                self.broker_position_service.refresh()

                # ====================================
                # RECONCILE
                # ====================================

                self.reconciliation_engine.reconcile_positions()

            except Exception as error:

                self.logger.error(

                    f"Reconciliation Worker Failed | "

                    f"{error}"
                )

            time.sleep(
                self.interval
            )


    # ====================================
    # START
    # ====================================

    def start(self):

        if self.running:

            self.logger.warning(
                "Reconciliation Worker Already Running"
            )

            return

        self.running = True

        self.thread = threading.Thread(

            target=
            self.run,

            daemon=True
        )

        self.thread.start()

        self.logger.info(
            "Reconciliation Worker Thread Started"
        )


    # ====================================
    # STOP
    # ====================================

    def stop(self):

        self.running = False

        self.logger.warning(
            "Reconciliation Worker Stopped"
        )