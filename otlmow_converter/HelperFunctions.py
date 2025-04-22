from collections import defaultdict
from pathlib import Path

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import OTLObject

from otlmow_converter.DotnotationDictConverter import DotnotationDictConverter
from otlmow_converter.Exceptions.CannotCombineAssetsError import CannotCombineAssetsError
from otlmow_converter.Exceptions.CannotCombineDifferentAssetsError import CannotCombineDifferentAssetsError
from otlmow_converter.Exceptions.NoIdentificatorError import NoIdentificatorError


def wrap_in_quotes(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError
    if text == '':
        return "''"
    singles = sum(1 for c in text if c == "'")
    doubles = sum(1 for c in text if c == '"')
    if singles > doubles:
        if doubles > 0:
            return '"' + text.replace('"', '\\"') + '"'
        return '"' + text + '"'
    else:
        if singles > 0:
            return "'" + text.replace("'", "\\'") + "'"
        return "'" + text + "'"


def combine_assets(asset_list: list[OTLObject], model_directory: Path = None) -> list[OTLObject]:
    assets = defaultdict(list)
    for asset in asset_list:
        if asset.typeURI == 'http://purl.org/dc/terms/Agent':
            assets[asset.agentId.identificator].append(asset)
        else:
            assets[asset.assetId.identificator].append(asset)
    combined_assets = []
    for asset_list in assets.values():
        if len(asset_list) == 1:
            combined_assets.append(asset_list[0])
        else:
            combined_asset = combine_two_asset_instances(asset_list[0], asset_list[1], model_directory)
            for asset in asset_list[2:]:
                combined_asset = combine_two_asset_instances(combined_asset, asset, model_directory)
            combined_assets.append(combined_asset)
    return combined_assets


def combine_two_asset_instances(asset1: OTLObject, asset2: OTLObject, model_directory: Path = None) -> OTLObject:
    if asset1 is None or asset2 is None:
        raise ValueError('One of the assets is None')

    id1 = asset1.assetId.identificator if asset1.typeURI != 'http://purl.org/dc/terms/Agent' \
        else asset1.agentId.identificator
    id2 = asset2.assetId.identificator if asset2.typeURI != 'http://purl.org/dc/terms/Agent' \
        else asset2.agentId.identificator

    if id1 is None or id2 is None:
        raise NoIdentificatorError('One of the assets has no assetId.identificator')

    if id1 != id2:
        raise CannotCombineDifferentAssetsError('The assets have different identificator values')

    if asset1.typeURI != asset2.typeURI:
        raise CannotCombineDifferentAssetsError('The assets have different types')

    ddict1 = DotnotationDictConverter.to_dict(asset1)
    ddict2 = DotnotationDictConverter.to_dict(asset2)
    if asset2.typeURI == 'http://purl.org/dc/terms/Agent':
        ddict2.pop('agentId.identificator')
    else:
        ddict2.pop('assetId.identificator')

    attribute_errors = []
    for key, value in ddict2.items():
        if value is None:
            continue
        if key == 'typeURI':
            continue

        if key in ddict1 and ddict1[key] is not None and ddict1[key] != value:
            attribute_errors.append((key, ddict1[key], value))
        else:
            ddict1[key] = value

    if attribute_errors:
        error_str = '\n'.join([f'{key}: {ddict1[key]}, {value}' for key, _, value in sorted(attribute_errors)])
        raise CannotCombineAssetsError(
            message=f'Cannot combine the assets with id {id1} because some attributes '
                    'have conflicting values:\n'
                    f'{error_str}')

    return DotnotationDictConverter.from_dict(ddict1, model_directory=model_directory)
