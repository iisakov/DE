import config
from . import STL
from . import sqltools


def run(argv, main_cli_param):
    params = STL.get_params(argv, main_cli_param)
    print(params)
