from pathlib import Path
from typing import Union, List

from otlmow_model.OtlmowModel.BaseClasses.OTLObject import set_value_by_dictitem, OTLObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.AIMObject import AIMObject
from otlmow_model.OtlmowModel.Classes.ImplementatieElement.RelatieObject import RelatieObject
from otlmow_model.OtlmowModel.Helpers.AssetCreator import dynamic_create_instance_from_uri


class AssetFactory:
    @staticmethod
    def create_otl_object_using_other_otl_object_as_template(orig_otl_object: OTLObject,
                                                             typeURI: str = '', fields_to_copy: [str] = None,
                                                             model_directory: Path = None) -> OTLObject:
        """Creates an OTLObject, using another OTLObject as template.
        The parameter typeURI defines the type of the new OTLObject that is created.
        If omitted, it is assumed the same type as the given aimObject
        The parameter fields_to_copy dictates what fields are copied from the first object
        When the types do not match, fields_to_copy can not be empty"""

        if model_directory is None:
            import otlmow_model
            otlmow_path = otlmow_model.__path__
            model_directory = Path(otlmow_path._path[0])

        if fields_to_copy is None:
            fields_to_copy = []

        if not isinstance(orig_otl_object, OTLObject):
            raise ValueError(f'{orig_otl_object} is not an OTLObject, not supported')

        if typeURI != '':
            if typeURI != orig_otl_object.typeURI and (fields_to_copy == [] or fields_to_copy is None):
                raise ValueError("parameter typeURI is different from orig_otl_object. parameter fields_to_copy cannot be empty")

        if typeURI == '':
            typeURI = orig_otl_object.typeURI
        new_asset = dynamic_create_instance_from_uri(typeURI, model_directory=model_directory)

        if len(fields_to_copy) == 0:
            fields_to_copy = [orig_otl_object]

        if 'typeURI' in fields_to_copy:
            fields_to_copy.remove('typeURI')
        if 'assetId' in fields_to_copy:
            fields_to_copy.remove('assetId')

        AssetFactory.copy_fields_from_object_to_new_object(orig_otl_object, new_asset, fields_to_copy)
        return new_asset

    @staticmethod
    def copy_fields_from_object_to_new_object(orig_object: Union[AIMObject, RelatieObject],
                                              new_object: Union[AIMObject, RelatieObject], field_list: [str]):
        if orig_object is None:
            raise ValueError("parameter orig_object is None")
        if new_object is None:
            raise ValueError("parameter new_object is None")
        if field_list is None or field_list == []:
            raise ValueError("parameter field_list is empty or None")

        distinct_fieldList = list(set(field_list))
        instance_dict = orig_object.create_dict_from_asset(waarde_shortcut=False)
        new_instance_dict = {}

        if instance_dict is None:
            instance_dict = {}

        for fieldName in distinct_fieldList:
            if fieldName not in instance_dict:
                continue
            dictitem = instance_dict[fieldName]
            new_instance_dict[fieldName] = dictitem

        for k, v in new_instance_dict.items():
            set_value_by_dictitem(new_object, k, v, waarde_shortcut=False)
