import json
from collections import OrderedDict
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject


class OtlAssetJSONEncoder(json.JSONEncoder):
    def __init__(self, indent=None, settings=None):
        super().__init__(indent=indent)

