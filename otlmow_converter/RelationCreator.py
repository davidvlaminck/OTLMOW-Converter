import base64
import re
import warnings
from typing import Type, Optional

from otlmow_model.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.Classes.Agent import Agent
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Classes.Onderdeel.HeeftBetrokkene import HeeftBetrokkene
from otlmow_model.Helpers.AssetCreator import AssetCreator
from otlmow_model.Helpers.GenericHelper import get_ns_and_name_from_uri
from otlmow_model.Helpers.RelationValidator import RelationValidator
from typing.re import Match

from otlmow_converter.Exceptions.CouldNotCreateRelationError import CouldNotCreateRelationError


def validate_guid(uuid: str) -> Optional[Match]:
    uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return re.match(uuid_pattern, uuid)


def encode_short_uri(short_uri: str) -> str:
    short_uri_bytes = short_uri.encode('ascii')
    base64_bytes = base64.b64encode(short_uri_bytes)
    base64_short_uri = base64_bytes.decode('ascii')
    while base64_short_uri.endswith('='):
        base64_short_uri = base64_short_uri[:-1]
    return base64_short_uri


def create_relation(relation_type: Type[RelatieObject], source: Optional[RelationInteractor] = None,
                    target: Optional[RelationInteractor] = None,
                    source_uuid: Optional[str] = None, source_typeURI: Optional[str] = None,
                    target_uuid: Optional[str] = None, target_typeURI: Optional[str] = None,
                    class_directory: str = None) -> RelatieObject:

    if source is None and (source_typeURI is None or source_uuid is None):
        raise ValueError('Exactly one of source or (source_typeURI + source_uuid) needs to be not None.')
    if target is None and (target_typeURI is None or target_uuid is None):
        raise ValueError('Exactly one of target or (target_typeURI + target_uuid) needs to be not None.')

    if source is not None and source_typeURI is not None:
        warnings.warn('both source and source_typeURI are not None. Using source and ignoring source_typeURI.',
                      RuntimeWarning)
    if target is not None and target_typeURI is not None:
        warnings.warn('both target and target_typeURI are not None. Using source and ignoring target_typeURI.',
                      RuntimeWarning)

    source_is_legacy, target_is_legacy = False, False
    source_aim_id, target_aim_id = None, None

    if source is None:
        if not validate_guid(source_uuid):
            raise ValueError('source_uuid is not a valid guid format.')

        ns, name = get_ns_and_name_from_uri(source_typeURI)
        encoded_uri = encode_short_uri(f'{ns}#{name}')
        source_aim_id = f'{source_uuid}-{encoded_uri}'

        if 'lgc.' in source_typeURI:
            source_is_legacy = True
        else:
            source = AssetCreator.dynamic_create_instance_from_uri(source_typeURI, directory=class_directory)
            source.assetId.identificator = source_aim_id
            source.assetId.toegekendDoor = 'AWV'

    if target is None:
        if not validate_guid(target_uuid):
            raise ValueError('target_uuid is not a valid guid format.')

        ns, name = get_ns_and_name_from_uri(target_typeURI)
        encoded_uri = encode_short_uri(f'{ns}#{name}')
        target_aim_id = f'{target_uuid}-{encoded_uri}'

        if 'lgc.' in target_typeURI:
            target_is_legacy = True
        else:
            target = AssetCreator.dynamic_create_instance_from_uri(target_typeURI, directory=class_directory)
            target.assetId.identificator = target_aim_id
            target.assetId.toegekendDoor = 'AWV'

    if not(source_is_legacy and target_is_legacy):
        valid = RelationValidator.is_valid_relation(source=source, target=target, relation_type=relation_type)
        if not valid:
            raise CouldNotCreateRelationError("Can't create an invalid relation_type, please validate relations first")

    relation_type = AssetCreator.dynamic_create_instance_from_uri(class_uri=relation_type.typeURI, directory=class_directory)

    if not source_is_legacy and source.assetId.identificator is None:
        raise AttributeError('In order to create a relation_type, the source needs to have a valid assetId '
                             '(source.assetId.identificator)')
    if not target_is_legacy and target.assetId.identificator is None:
        raise AttributeError(
            'In order to create a relation_type, the target needs to have a valid assetId '
            '(target.assetId.identificator)')

    relation_id = ''
    if source_is_legacy:
        relation_type.bronAssetId.identificator = source_aim_id
        relation_type.bronAssetId.toegekendDoor = 'AWV'
        relation_id += source_aim_id
    else:
        relation_type.bronAssetId.identificator = source.assetId.identificator
        relation_type.bronAssetId.toegekendDoor = source.assetId.toegekendDoor
        relation_id += source.assetId.identificator

    relation_id += '_-_'

    if target_is_legacy:
        relation_type.bronAssetId.identificator = target_aim_id
        relation_type.bronAssetId.toegekendDoor = 'AWV'
        relation_id += target_aim_id
    else:
        relation_type.doelAssetId.identificator = target.assetId.identificator
        relation_type.doelAssetId.toegekendDoor = target.assetId.toegekendDoor
        relation_id += target.assetId.identificator

    relation_type.assetId.identificator = relation_id
    relation_type.assetId.toegekendDoor = 'OTLMOW'

    if relation_type.bronAssetId.toegekendDoor != 'AWV':
        relation_type.bron.typeURI = source.typeURI
    if relation_type.doelAssetId.toegekendDoor != 'AWV':
        relation_type.doel.typeURI = target.typeURI
    return relation_type

def create_betrokkenerelation(source: RelationInteractor, target: RelationInteractor) -> RelatieObject:
    valid = RelationValidator.is_valid_relation(source=source, target=target, relation_type=HeeftBetrokkene)
    if not valid:
        raise CouldNotCreateRelationError("Can't create an invalid relation_type, please validate relations first")

    relatie = AssetCreator.dynamic_create_instance_from_uri(class_uri=HeeftBetrokkene.typeURI)

    if isinstance(source, Agent):
        relatie.bronAssetId.identificator = source.agentId.identificator
        relatie.bronAssetId.toegekendDoor = source.agentId.toegekendDoor
    else:
        relatie.bronAssetId.identificator = source.assetId.identificator
        relatie.bronAssetId.toegekendDoor = source.assetId.toegekendDoor

    relatie.doelAssetId.identificator = target.agentId.identificator
    relatie.doelAssetId.toegekendDoor = target.agentId.toegekendDoor

    relatie.assetId.identificator = relatie.bronAssetId.identificator + '_-_' + relatie.doelAssetId.identificator
    relatie.assetId.toegekendDoor = 'OTLMOW'

    #if relation_type.bronAssetId.toegekendDoor != 'AWV':
    relatie.bron.typeURI = source.typeURI
    #if relation_type.doelAssetId.toegekendDoor != 'AWV':
    relatie.doel.typeURI = target.typeURI
    return relatie
