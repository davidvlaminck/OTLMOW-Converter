import unittest
from pathlib import Path
from typing import List


class SubsetTool:
    @classmethod
    def generate_template_from_subset(cls, path_to_subset: Path, path_to_template_file_and_extension: Path):
        raise NotImplementedError

    @classmethod
    def filters_assets_by_subset(cls, path_to_subset: Path, list_of_otl_objects: List):
        raise NotImplementedError


class SubsetToolTests(unittest.TestCase):
    def test_func1(self):
        SubsetTool.generate_template_from_subset(Path('path_to_subset'), Path('path_to_template_file_and_extension'))

    def test_func2(self):
        list_of_otl_objects = []
        SubsetTool.filters_assets_by_subset(Path('path_to_subset'), list_of_otl_objects)