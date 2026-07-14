# ====================================
# logger.py
# ====================================

import os

from datetime import datetime

import pytz

from utils.config import (

    MARKET_TIMEZONE,

    LOG_LEVEL
)

from utils.runtime_mode import (
    RUNTIME_MODE
)


# ====================================
# TIMEZONE
# ====================================

MARKET_TZ = pytz.timezone(
    MARKET_TIMEZONE
)


# ====================================
# LOG ROOT DIRECTORY
# ====================================

LOG_ROOT_DIR = "logs"


# ====================================
# LOGGER
# ====================================

class SystemLogger:


    # ====================================
    # INIT
    # ====================================

    def __init__(

        self,

        log_type="runtime"
    ):

        self.log_type = (
            log_type
        )

        self.runtime_mode = (
            RUNTIME_MODE
        )

        # ====================================
        # MODE LOG DIRECTORY
        # ====================================

        self.log_dir = os.path.join(

            LOG_ROOT_DIR,

            self.runtime_mode
        )

        os.makedirs(

            self.log_dir,

            exist_ok=True
        )

        # ====================================
        # LOG FILES
        # ====================================

        self.runtime_log_file = os.path.join(

            self.log_dir,

            "runtime.log"
        )

        self.execution_log_file = os.path.join(

            self.log_dir,

            "execution.log"
        )

        self.error_log_file = os.path.join(

            self.log_dir,

            "error.log"
        )

        # ====================================
        # ACTIVE LOG FILE
        # ====================================

        if self.log_type == "execution":

            self.log_file = (
                self.execution_log_file
            )

        else:

            self.log_file = (
                self.runtime_log_file
            )


    # ====================================
    # CURRENT TIME
    # ====================================

    def _current_time(self):

        return datetime.now(
            MARKET_TZ
        )


    # ====================================
    # FORMAT MESSAGE
    # ====================================

    def _format_message(

        self,

        level,

        message
    ):

        return (

            f"[{level}] "

            f"[{self.runtime_mode}] "

            f"{self._current_time()} "

            f"{message}"
        )


    # ====================================
    # WRITE LOG
    # ====================================

    def _write_log(

        self,

        file_path,

        formatted_message
    ):

        with open(

            file_path,

            "a",

            encoding="utf-8"
        ) as file:

            file.write(

                formatted_message
                + "\n"
            )


    # ====================================
    # WRITE STANDARD LOG
    # ====================================

    def _write_standard_log(

        self,

        formatted_message
    ):

        self._write_log(

            self.log_file,

            formatted_message
        )


    # ====================================
    # WRITE ERROR LOG
    # ====================================

    def _write_error_log(

        self,

        formatted_message
    ):

        self._write_log(

            self.error_log_file,

            formatted_message
        )


    # ====================================
    # INFO
    # ====================================

    def info(

        self,

        message
    ):

        formatted_message = (

            self._format_message(

                "INFO",

                message
            )
        )

        print(
            formatted_message
        )

        self._write_standard_log(
            formatted_message
        )


    # ====================================
    # WARNING
    # ====================================

    def warning(

        self,

        message
    ):

        formatted_message = (

            self._format_message(

                "WARNING",

                message
            )
        )

        print(
            formatted_message
        )

        self._write_standard_log(
            formatted_message
        )

        # ====================================
        # ALSO WRITE WARNING TO ERROR LOG
        # ====================================

        self._write_error_log(
            formatted_message
        )


    # ====================================
    # ERROR
    # ====================================

    def error(

        self,

        message
    ):

        formatted_message = (

            self._format_message(

                "ERROR",

                message
            )
        )

        print(
            formatted_message
        )

        self._write_standard_log(
            formatted_message
        )

        self._write_error_log(
            formatted_message
        )


    # ====================================
    # DEBUG
    # ====================================

    def debug(

        self,

        message
    ):

        if LOG_LEVEL != "DEBUG":

            return

        formatted_message = (

            self._format_message(

                "DEBUG",

                message
            )
        )

        print(
            formatted_message
        )

        self._write_standard_log(
            formatted_message
        )