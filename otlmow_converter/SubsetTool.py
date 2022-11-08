import json
import os
from os.path import abspath
from pathlib import Path
from typing import List

from otlmow_modelbuilder.OSLOInMemoryCreator import OSLOInMemoryCreator
from otlmow_modelbuilder.SQLDataClasses.OSLOCollector import OSLOCollector
from otlmow_modelbuilder.SQLDbReader import SQLDbReader

from otlmow_converter.AssetFactory import AssetFactory
from otlmow_converter.FileExporter import FileExporter
from otlmow_converter.FileFormats.CsvExporter import CsvExporter


class SubsetTool:
    def __init__(self, settings_path: Path = None):
        if settings_path is None:
            raise FileNotFoundError(
                "Instantiating this class requires a settings file. Please give a valid path to a settings file")
        self.settings: dict = {}
        self._load_settings(settings_path)

    def _load_settings(self, settings_path):
        if settings_path == '':
            current_file_path = Path(__file__)
            directory = current_file_path.parents[0]
            settings_path = abspath(f'{directory}\\settings_sample.json')

        if not os.path.isfile(settings_path):
            raise FileNotFoundError(settings_path + " is not a valid path. File does not exist.")

        try:
            with open(settings_path) as settings_file:
                self.settings = json.load(settings_file)
        except OSError:
            raise ImportError(f'Could not open the settings file at {settings_file}')

    @staticmethod
    def _load_collector_from_subset_path(path_to_subset: Path) -> OSLOCollector:
        sql_reader = SQLDbReader(path_to_subset)
        oslo_creator = OSLOInMemoryCreator(sql_reader)
        collector = OSLOCollector(oslo_creator)
        collector.collect()
        return collector

    def generate_template_from_subset(self, path_to_subset: Path, path_to_template_file_and_extension: Path,
                                      **kwargs):
        collector = self._load_collector_from_subset_path(path_to_subset=path_to_subset)
        otl_objects = []

        for class_object in list(filter(lambda cl: cl.abstract == 0, collector.classes)):
            class_directory = None
            if kwargs is not None and 'class_directory' in kwargs:
                class_directory = kwargs['class_directory']
            instance = AssetFactory.dynamic_create_instance_from_uri(class_object.objectUri, directory=class_directory)
            if instance is None:
                continue
            instance._assetId.fill_with_dummy_data()
            otl_objects.append(instance)

            attributen = collector.find_attributes_by_class(class_object)
            for attribute_object in attributen:
                attr = getattr(instance, '_' + attribute_object.name)
                attr.fill_with_dummy_data()

        # TODO relaties

        exporter = FileExporter(settings=self.settings)
        exporter.create_file_from_assets(filepath=path_to_template_file_and_extension,
                                         list_of_objects=otl_objects, **kwargs)

    @classmethod
    def filters_assets_by_subset(cls, path_to_subset: Path, list_of_otl_objects: List):
        raise NotImplementedError
