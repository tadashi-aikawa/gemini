# -*- coding:utf-8 -*-

from owlmixin import OwlMixin, TList

from jumeaux.addons.judgement import JudgementExecutor
from jumeaux.addons.utils import when_filter
from jumeaux.logger import Logger
from jumeaux.models import JudgementAddOnPayload, JudgementAddOnReference

logger: Logger = Logger(__name__)
LOG_PREFIX = "[judgement/same]"


class Config(OwlMixin):
    when_any: TList[str]

    @classmethod
    def validate(cls, config):
        if not config or 'when_any' not in config:
            logger.error(f'{LOG_PREFIX} `config.when_any` is required !!', exit=True)


class Executor(JudgementExecutor):
    config: Config

    def __init__(self, config: dict) -> None:
        Config.validate(config)
        self.config: Config = Config.from_dict(config)

    def exec(self, payload: JudgementAddOnPayload, reference: JudgementAddOnReference) -> JudgementAddOnPayload:
        if payload.regard_as_same:
            return payload

        same: str = self.config.when_any.find(lambda x: when_filter(x, {
            "name": reference.name,
            "path": reference.path,
            "qs": reference.qs,
            "headers": reference.headers,
            "res_one": reference.res_one,
            "res_other": reference.res_other,
            "dict_one": reference.dict_one,
            "dict_other": reference.dict_other,
        }))

        if same:
            logger.info_lv3(f"{LOG_PREFIX} Regard as same by `{same}`.")

        return JudgementAddOnPayload.from_dict({
            "remaining_diff_keys": payload.remaining_diff_keys,
            "regard_as_same": bool(same),
        })
