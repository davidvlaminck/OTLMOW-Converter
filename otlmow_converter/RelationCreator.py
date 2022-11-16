from typing import Type

from otlmow_model.BaseClasses.RelationInteractor import RelationInteractor
from otlmow_model.Classes.Agent import Agent
from otlmow_model.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.Classes.Onderdeel.HeeftBetrokkene import HeeftBetrokkene
from otlmow_model.Helpers.RelationValidator import RelationValidator

from otlmow_converter.AssetFactory import AssetFactory
from otlmow_converter.Exceptions.CouldNotCreateRelationError import CouldNotCreateRelationError


def create_relation(source: RelationInteractor, target: RelationInteractor, relation: Type[RelatieObject]) -> RelatieObject:
    valid = RelationValidator.is_valid_relation(source=source, target=target, relation=relation)
    if not valid:
        raise CouldNotCreateRelationError("Can't create an invalid relation, please validate relations first")
    relation = AssetFactory().dynamic_create_instance_from_uri(class_uri=relation.typeURI)

    if source.assetId.identificator is None:
        raise AttributeError('In order to create a relation, the source needs to have a valid assetId '
                             '(source.assetId.identificator)')
    if target.assetId.identificator is None:
        raise AttributeError(
            'In order to create a relation, the target needs to have a valid assetId '
            '(target.assetId.identificator)')

    relation.bronAssetId.identificator = source.assetId.identificator
    relation.bronAssetId.toegekendDoor = source.assetId.toegekendDoor

    relation.doelAssetId.identificator = target.assetId.identificator
    relation.doelAssetId.toegekendDoor = target.assetId.toegekendDoor

    relation.assetId.identificator = source.assetId.identificator + '_-_' + target.assetId.identificator
    relation.assetId.toegekendDoor = 'OTLMOW'

    if relation.bronAssetId.toegekendDoor != 'AWV':
        relation.bron.typeURI = source.typeURI
    if relation.doelAssetId.toegekendDoor != 'AWV':
        relation.doel.typeURI = target.typeURI
    return relation

def create_betrokkenerelation(source: RelationInteractor, target: RelationInteractor) -> RelatieObject:
    valid = RelationValidator.is_valid_relation(source=source, target=target, relation=HeeftBetrokkene)
    if not valid:
        raise CouldNotCreateRelationError("Can't create an invalid relation, please validate relations first")

    relatie = AssetFactory().dynamic_create_instance_from_uri(class_uri=HeeftBetrokkene.typeURI)

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

    #if relation.bronAssetId.toegekendDoor != 'AWV':
    relatie.bron.typeURI = source.typeURI
    #if relation.doelAssetId.toegekendDoor != 'AWV':
    relatie.doel.typeURI = target.typeURI
    return relatie
