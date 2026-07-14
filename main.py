# ====================================
# main.py
# ====================================

import os
import sys
import subprocess
import time
import threading

import uvicorn

from runtime.runtime_bootstrap import (
    RuntimeBootstrap
)

from utils.logger import (
    SystemLogger
)


# ====================================
# LOGGER
# ====================================

logger = (
    SystemLogger()
)


# ====================================
# PYTHON EXECUTABLE
# ====================================

PYTHON_EXECUTABLE = (
    r"D:\Miniconda\python.exe"
)


# ====================================
# ENGINE DIRECTORY
# ====================================

ENGINE_DIR = (
    r"D:\python\机器学习-0\.vscode\execution-simulator\engine"
)


# ====================================
# ENSURE PYTHON PATH
# ====================================

if ENGINE_DIR not in sys.path:

    sys.path.insert(
        0,
        ENGINE_DIR
    )


# ====================================
# START FASTAPI
# ====================================

def start_fastapi():

    logger.info(
        "Starting FastAPI..."
    )

    uvicorn.run(

        "api.execution_api:app",

        host=
        "127.0.0.1",

        port=
        8000,

        reload=
        False,

        log_level=
        "info"
    )


# ====================================
# START FASTAPI THREAD
# ====================================

def start_fastapi_thread():

    api_thread = threading.Thread(

        target=
        start_fastapi,

        daemon=True
    )

    api_thread.start()

    return api_thread


# ====================================
# START DASHBOARD
# ====================================

def start_dashboard():

    logger.info(
        "Starting Dashboard..."
    )

    return subprocess.Popen(

        [

            PYTHON_EXECUTABLE,

            "-m",

            "streamlit",

            "run",

            "dashboard/app.py",

            "--server.address",

            "127.0.0.1",

            "--server.port",

            "8501"
        ],

        cwd=
        ENGINE_DIR
    )


# ====================================
# MAIN
# ====================================

def main():

    bootstrap = None

    dashboard_process = None

    try:

        logger.warning(
            "Launching Trading Runtime"
        )

        os.chdir(
            ENGINE_DIR
        )

        # ====================================
        # BOOTSTRAP RUNTIME
        # ====================================

        bootstrap = (
            RuntimeBootstrap()
        )

        bootstrap.bootstrap()

        logger.info(
            "Runtime Started"
        )

        # ====================================
        # START FASTAPI THREAD
        # ====================================

        start_fastapi_thread()

        # ====================================
        # WAIT FOR API
        # ====================================

        time.sleep(
            3
        )

        # ====================================
        # START DASHBOARD
        # ====================================

        dashboard_process = (
            start_dashboard()
        )

        logger.warning(
            "Platform Fully Started"
        )

        logger.warning(
            "FastAPI: http://127.0.0.1:8000"
        )

        logger.warning(
            "Dashboard: http://127.0.0.1:8501"
        )

        # ====================================
        # KEEP MAIN ALIVE
        # ====================================

        while True:

            time.sleep(
                1
            )

    except KeyboardInterrupt:

        logger.warning(
            "System Interrupted"
        )

    except Exception as error:

        logger.error(

            f"Fatal Runtime Error | "

            f"{error}"
        )

    finally:

        # ====================================
        # SHUTDOWN DASHBOARD
        # ====================================

        try:

            if dashboard_process:

                dashboard_process.terminate()

                logger.warning(
                    "Dashboard Stopped"
                )

        except Exception as error:

            logger.error(

                f"Process Shutdown Failed | "

                f"{error}"
            )

        # ====================================
        # CLEAN RUNTIME SHUTDOWN
        # ====================================

        try:

            if bootstrap:

                bootstrap.shutdown()

                logger.warning(
                    "Runtime Shutdown Complete"
                )

        except Exception as error:

            logger.error(

                f"Runtime Shutdown Failed | "

                f"{error}"
            )

        logger.warning(
            "Platform Shutdown Complete"
        )


# ====================================
# ENTRYPOINT
# ====================================

if __name__ == "__main__":

    main()