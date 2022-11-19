from otlmow_model.Classes.ImplementatieElement.AIMObject import AIMObject

from otlmow_converter.FileFormats.DictDecoder import DictDecoder
from otlmow_converter.HelperFunctions import get_ns_and_name_from_uri, get_titlecase_from_ns


class AssetFactory:
    @staticmethod
    def dynamic_create_instance_from_ns_and_name(namespace: str, class_name: str, directory: str = 'otlmow_model.Classes'):
        """Loads the OTL class module and attempts to instantiate the class using the name and namespace of the class

        :param namespace: namespace of the class
        :type: str
        :param class_name: class name to instantiate
        :type: str
        :param directory: directory where the class modules are located, defaults to OTLMOW.OTLModel.Classes
        :type: str
        :return: returns an instance of class_name in the given namespace, located from directory, that inherits from OTLObject
        :rtype: OTLObject or None
        """

        if directory is None:
            directory = 'otlmow_model.Classes'

        if namespace is None:
            namespace = ''
        else:
            namespace = get_titlecase_from_ns(namespace)

        try:
            # TODO: check https://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
            py_mod = __import__(name=f'{directory}.{namespace}.{class_name}', fromlist=f'{class_name}')
        except ModuleNotFoundError:
            return None
        class_ = getattr(py_mod, class_name)
        instance = class_()

        return instance

    @staticmethod
    def dynamic_create_instance_from_uri(class_uri: str, directory: str = None):
        if directory is None:
            directory = 'otlmow_model.Classes'

        if not class_uri.startswith('https://wegenenverkeer.data.vlaanderen.be/ns'):
            raise ValueError(
                f'{class_uri} is not valid uri, it does not begin with "https://wegenenverkeer.data.vlaanderen.be/ns"')
        ns, name = get_ns_and_name_from_uri(class_uri)
        created = AssetFactory.dynamic_create_instance_from_ns_and_name(ns, name, directory=directory)
        if created is None:
            raise ValueError(f'{class_uri} is likely not valid uri, it does not result in a created instance')
        return created

    @staticmethod
    def create_aimObject_using_other_aimObject_as_template(orig_aim_object: AIMObject, typeURI: str = '',
                                                           fields_to_copy: [str] = None,
                                                           directory: str = None):
        """Creates an AIMObject, using another AIMObject as template.
        The parameter typeURI defines the type of the new AIMObject that is created.
        If omitted, it is assumed the same type as the given aimObject
        The parameter fields_to_copy dictates what fields are copied from the first object
        When the types do not match, fields_to_copy can not be empty"""

        if directory is None:
            directory = 'otlmow_model.Classes'
        if fields_to_copy is None:
            fields_to_copy = []

        if not isinstance(orig_aim_object, AIMObject):
            raise ValueError(f'{orig_aim_object} is not an AIMObject, not supported')

        if typeURI != '':
            if typeURI != orig_aim_object.typeURI and (fields_to_copy == [] or fields_to_copy is None):
                raise ValueError("parameter typeURI is different from orig_aim_object. parameter fields_to_copy cannot be empty")

        if typeURI == '':
            typeURI = orig_aim_object.typeURI
        new_asset = AssetFactory.dynamic_create_instance_from_uri(typeURI, directory=directory)

        if len(fields_to_copy) == 0:
            fields_to_copy = AssetFactory.get_attribute_list_from_object(orig_aim_object)

        if 'typeURI' in fields_to_copy:
            fields_to_copy.remove('typeURI')
        if 'assetId' in fields_to_copy:
            fields_to_copy.remove('assetId')

        AssetFactory.copy_fields_from_object_to_new_object(orig_aim_object, new_asset, fields_to_copy)
        return new_asset

    @staticmethod
    def get_attribute_list_from_object(orig_asset: AIMObject):
        if orig_asset is None:
            raise ValueError("input can't be None")

        return list(orig_asset.create_dict_from_asset().keys())

    @staticmethod
    def copy_fields_from_object_to_new_object(orig_object: AIMObject, new_object: AIMObject, field_list: [str]):
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
            DictDecoder.set_value_by_dictitem(new_object, k, v, waarde_shortcut=False)
