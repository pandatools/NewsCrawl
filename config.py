from dynaconf import Dynaconf




dy_settings = Dynaconf(
    envvar_prefix="",
    environments=True,
    env_switcher="ENV",
    settings_files=['settings.yaml'],
)
