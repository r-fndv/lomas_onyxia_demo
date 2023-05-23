from pydantic import BaseModel

# Temporary workaround this issue:
# https://github.com/pydantic/pydantic/issues/5821
# from typing import Literal
from typing_extensions import Literal
import yaml

from utils.constants import (
    CONF_RUNTIME_ARGS,
    CONF_SETTINGS,
    CONF_TIME_ATTACK,
    CONF_DB,
    CONF_DB_TYPE,
    CONF_DB_TYPE_MONGODB,
    CONF_DB_TYPE_YAML,
    CONF_SUBMIT_LIMIT,
)
import globals
from utils.constants import CONFIG_PATH
from utils.loggr import LOG


class TimeAttack(BaseModel):
    method: Literal["jitter", "stall"]
    magnitude: float = 1


class DBConfig(BaseModel):
    db_type: str = Literal["mongodb", "yaml"]


class MongoDBConfig(DBConfig):
    address: str = None
    port: int = None


class YAMLDBConfig(DBConfig):
    db_file: str = None


class Config(BaseModel):
    # Server configs
    time_attack: TimeAttack = None

    # A limit on the rate which users can submit answers
    submit_limit: float = (
        5 * 60
    )  # TODO not used for the moment, kept as a simple example field for now.

    database: DBConfig = None
    # validator example, for reference
    """ @validator('parties')
    def two_party_min(cls, v):
        assert len(v) >= 2
        return v
    """

    # Yet to determin what this was used for.
    # TODO read this https://docs.pydantic.dev/usage/settings/#secret-support
    # and update how config is loaded (similar to what is done by oblv.)
    """
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config,
                env_settings,
                file_secret_settings,
            )
    """


# Utility functions -----------------------------------------------------------


def get_config() -> dict:
    """
    Returns the global config object if not None.
    If not already loaded, loads it from disk, sets it as the global config
    and returns it.
    """
    if globals.CONFIG is not None:
        return globals.CONFIG

    try:
        with open(CONFIG_PATH, "r") as f:
            config_data = yaml.safe_load(f)[CONF_RUNTIME_ARGS][CONF_SETTINGS]

        time_attack: TimeAttack = TimeAttack.parse_obj(
            config_data[CONF_TIME_ATTACK]
        )

        db_type = config_data[CONF_DB][CONF_DB_TYPE]
        if db_type == CONF_DB_TYPE_MONGODB:
            database_config = MongoDBConfig.parse_obj(config_data[CONF_DB])
        elif db_type == CONF_DB_TYPE_YAML:
            database_config = YAMLDBConfig.parse_obj(config_data[CONF_DB])
        else:
            raise Exception(f"Database type {db_type} not supported.")

        config: Config = Config(
            time_attack=time_attack,
            submit_limit=config_data[CONF_SUBMIT_LIMIT],
            database=database_config,
        )

    except Exception as e:
        LOG.error(
            f"Could not read config from disk at {CONFIG_PATH} \
                or missing fields"
        )
        raise e

    return config


"""
def reload_config() -> Config:
    # Potentially?
    return None
"""
