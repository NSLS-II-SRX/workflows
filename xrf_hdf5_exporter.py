from prefect import flow, task, get_run_logger

### Temporary solution until prefect deployment updates to 2024 environment ###
###############################################################################
import sys
conda_env = "2024-1.0-py310-tiled"
python_ver = "python3.10"
overlay = [
    f"/nsls2/data/srx/shared/config/bluesky_overlay/{conda_env}/lib/{python_ver}/site-packages",
    f"/nsls2/conda/envs/{conda_env}/bin",
    f"/nsls2/conda/envs/{conda_env}/lib/{python_ver}",
    f"/nsls2/conda/envs/{conda_env}/lib/{python_ver}/lib-dynload",
    f"/nsls2/conda/envs/{conda_env}/lib/{python_ver}/site-packages",
]
sys.path[:0] = overlay
###############################################################################

from tiled.client import from_profile
from pyxrf.api import make_hdf

tiled_client = from_profile("nsls2")["srx"]
tiled_client_raw = tiled_client["raw"]

@task
def export_xrf_hdf5(scanid):
    logger = get_run_logger()

    # Load header for our scan
    h = tiled_client_raw[scanid]

    if h.start["scan"]["type"] not in ["XRF_FLY", "XRF_STEP"]:
        logger.info(
            "Incorrect document type. Not running pyxrf.api.make_hdf on this document."
        )
        return

    working_dir = f"/nsls2/data/srx/proposals/{h.start['cycle']}/{h.start['data_session']}"  # noqa: E501
    prefix = "autorun_scan2D"

    logger.info(f"{working_dir =}")
    make_hdf(scanid, wd=working_dir, prefix=prefix)

@flow(log_prints=True)
def xrf_hdf5_exporter(scanid):
    logger = get_run_logger()
    logger.info("Start writing file...")
    export_xrf_hdf5(scanid)
    logger.info("Finish writing file.")
