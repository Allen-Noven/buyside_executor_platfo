# ====================================
# execution_repository.py
# ====================================

import os

import json

from utils.logger import (
    SystemLogger
)

from utils.helpers import (
    get_current_timestamp
)


# ====================================
# STORAGE DIRECTORY
# ====================================

EXECUTION_STORAGE_DIR = (
    "storage/executions/"
)

os.makedirs(

    EXECUTION_STORAGE_DIR,

    exist_ok=True
)


class ExecutionRepository:


    # ====================================
    # INIT
    # ====================================

    def __init__(self):

        self.logger = (
            SystemLogger()
        )


    # ====================================
    # SAVE EXECUTION
    # ====================================

    def save_execution(

        self,

        execution_data
    ):

        timestamp = (

            get_current_timestamp()

            .replace(":", "-")

            .replace(" ", "_")
        )

        execution_id = (

            execution_data.get(

                "execution_id",

                "UNKNOWN"
            )
        )

        file_name = (

            f"{EXECUTION_STORAGE_DIR}"

            f"{execution_id}_"

            f"{timestamp}.json"
        )

        try:

            with open(

                file_name,

                "w"
            ) as file:

                json.dump(

                    execution_data,

                    file,

                    indent=4
                )

            self.logger.info(

                f"Execution Saved | "

                f"{file_name}"
            )

        except Exception as error:

            self.logger.error(

                f"Execution Save Failed | "

                f"{error}"
            )


    # ====================================
    # LOAD EXECUTION
    # ====================================

    def load_execution(

        self,

        file_name
    ):

        try:

            with open(

                file_name,

                "r"
            ) as file:

                execution_data = (
                    json.load(file)
                )

            return execution_data

        except Exception as error:

            self.logger.error(

                f"Execution Load Failed | "

                f"{error}"
            )

            return None


    # ====================================
    # LIST EXECUTIONS
    # ====================================

    def list_executions(self):

        try:

            execution_files = os.listdir(

                EXECUTION_STORAGE_DIR
            )

            return execution_files

        except Exception as error:

            self.logger.error(

                f"Execution List Failed | "

                f"{error}"
            )

            return []


    # ====================================
    # DELETE EXECUTION
    # ====================================

    def delete_execution(

        self,

        file_name
    ):

        try:

            file_path = (

                EXECUTION_STORAGE_DIR
                + file_name
            )

            os.remove(file_path)

            self.logger.warning(

                f"Execution Deleted | "

                f"{file_name}"
            )

        except Exception as error:

            self.logger.error(

                f"Execution Delete Failed | "

                f"{error}"
            )


    # ====================================
    # SHOW EXECUTIONS
    # ====================================

    def show_executions(self):

        execution_files = (
            self.list_executions()
        )

        print(

            "\n========== "
            "EXECUTION HISTORY "
            "==========\n"
        )

        for file_name in execution_files:

            print(file_name)

        print(

            "\n==============================="
            "===================\n"
        )
