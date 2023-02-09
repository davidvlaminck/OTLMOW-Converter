from datetime import datetime
from pathlib import Path

from otlmow_model.Classes.Onderdeel.Wegkantkast import Wegkantkast

from otlmow_converter.OtlmowConverter import OtlmowConverter

uuids = ['2338d711-57ba-4a95-ba0f-9af9e1a0a0ba', 'cf8e794e-7f71-42f4-92f4-6d969e746602',
         'cacd2351-7ec4-48a2-a529-c2d17208fba9', 'f1cd7072-bf6b-475b-992d-f552bfabb776',
         '24614784-68e2-469e-a813-8440a0d11c2a', '7ecbda14-649b-419b-9c61-46800a8e305a',
         '00031dbf-0d37-4dc6-9a4b-44cb8129f67e', 'e6a15ca0-a837-44ba-8551-79d2643cbbd1',
         '918f3a85-15c6-41b9-997c-5c6049648d5e', '278ea911-c3fb-4c75-9077-2f929a1d44a4',
         'afa49055-0656-43d6-bbf2-aa419fd7424e', '116eae82-a4a5-438a-813a-003be826d9e5',
         '9aa70626-e5ee-49d6-9b08-bc64a621d3f7', '4833b9db-c712-4dbc-94f8-3e737a2a4071',
         '73af9f72-5423-4f9a-9288-539b6e024d32', 'cd7df513-89a1-4714-bd75-d470c202e470',
         'f075e22e-ca31-4402-a9bd-d0f8f978a6d2', '8eca110d-8467-4113-831b-3c936e671b7c',
         'b3c72cb9-0c1e-4a12-b13b-ffe36e42d84b', '963a324a-3330-40c3-8c16-0e02307dade2',
         '6fa0c873-20ef-4005-958c-6d2832b06443', 'fd19154f-a38b-4aa8-9b72-f04e34d8d144',
         '647d9c22-79cc-4f96-805c-bf5e702536e5', '0a20bd73-1c04-4ec1-a639-f823da55bd2f',
         '26c1fbd8-a355-47d3-8908-44ac7af7b560', '29752f31-42a0-4f6f-88fc-c947b1a40bb6',
         '97553d87-ef5f-4ca8-83df-7f2f378f8984', '46641260-4d17-4675-889d-959a909ea09f',
         'ad391e78-b26e-422d-9fa1-8d666b76fe49', '4f797402-ea07-4b54-9b01-3aaae43f1977',
         '9546d7cf-9cbe-401d-9674-0e64d1ed1f78', 'b5239a56-7229-457d-acc4-0717d3fce829',
         'ecf0f409-8446-4b1e-9139-009966d631c2', '0f9b7f17-2351-4da6-9298-2ad952e082a0',
         '65c70135-82a0-406d-b5e7-f4b8779118c6', '0da87167-01e1-4343-834b-bee3312c0a97',
         '577a6f23-3077-43e1-bcc7-0eb9fde22cab', '39cc70f7-6d74-4ed9-9d87-6a14e50ea52f',
         '4af387ca-fe4c-486e-bb90-bae81e07eb88', '4f2417dc-804c-4ea7-a736-faff05383d52',
         '852298bc-7946-416a-b06b-fffdb2828d67', 'e02e118a-3cd4-4401-9351-666805847469',
         'ea7919f3-8c95-48d7-acac-c0ade1e9dbad', '3aaccedd-ffb9-4371-8977-48aa22becbe3',
         'bd8798bb-66df-4cc0-b3a8-f9289df93586', 'd2ddfa23-8e22-4330-939b-67f4d57bb4e2',
         'd5c62f39-5308-46e3-bfe8-dbfffe4eaa02', 'e2dfa587-cbd8-42a5-a88f-174d69d05e4a',
         'b9107d90-6b66-4e14-b2f9-c5213045adee', 'f282a39d-6d86-4068-a681-c7919350d912',
         '1c7572c1-c6bf-40e5-a19e-16916a2bdbdc', '512b911e-8e64-42e4-bdf6-a1bca543250d',
         'e8d5ff97-3982-4ab7-929c-ecf20ca17a02', 'bdc9945b-35ee-4fe0-a7b5-79c862dace91',
         'fdbfca04-5966-4c39-b17f-0bfbbfc0a250', 'c72821d7-47bb-4c37-853a-09113acf627e',
         '377afb42-d459-42b8-a8ba-e637f6bbe148', 'b1114593-1d6d-4e7f-9051-ecf3d102037d',
         'd9e44276-70d8-4d5a-b783-3be50a913881', 'b6e64cf7-5157-41fe-88db-facb76476b8f',
         'f3e87d42-3e66-42bc-8481-088872eb9166', '9aa7ca05-6a99-4315-b5a5-243bcfc61756',
         '736ae053-35f6-4630-9b33-8af7c5c296e6', 'f2cf4ca1-e7ac-4e2f-9aaf-7ca87c54d7a9',
         '8234e782-72a8-4a18-9273-004ea0edb9fd', '3d17088f-c29a-4d40-b777-2b6696bbe8a8',
         '91e59c82-6415-4661-9d0e-8ef93b9abac1', 'b5889bf1-784b-4a8d-8c19-6ccdaf702a3e',
         'decb85ce-93a6-40a7-81dd-8452d4ff316a', '7572adf6-e003-43b9-97a2-49070b3ba4b4',
         'd5181756-588a-446c-b4af-31f229ef688c']

if __name__ == '__main__':
    assets_to_create = []
    otlmow_converter = OtlmowConverter()

    for uuid in uuids:
        kast = Wegkantkast()
        kast.isActief = False
        kast.assetId.identificator = f'{uuid}-b25kZXJkZWVsI1dlZ2thbnRrYXN0'
        assets_to_create.append(kast)

    # export
    file_path = Path(f'/home/davidlinux/Documents/AWV/{datetime.now().strftime("%Y%m%d%H%M%S")}_export.xlsx')
    otlmow_converter.create_file_from_assets(filepath=file_path, list_of_objects=assets_to_create)


