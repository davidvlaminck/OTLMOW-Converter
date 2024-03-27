from otlmow_model.OtlmowModel.Classes.Onderdeel.Boom import Boom

from otlmow_converter.OtlmowConverter import OtlmowConverter

if __name__ == '__main__':
    boom = Boom()
    boom.boomspiegel = ['gras']
    boom.toestand = 'in-gebruik'
    boom.takvrijeStamlengte.waarde = 2.0
    boom.soortnaam.soortnaamNederlands = 'eik'
    boom.niet_conform_attribute = 'niet_conform'

    print(f'boom:\n{boom}\n')

    boom_dicts = OtlmowConverter.to_dicts([boom])
    print(f'boom_dict:\n{next(boom_dicts)}\n')

    print('boom_dotnotation_dict:\n')
    boom_dotnotation_dicts = OtlmowConverter.to_dotnotation_dicts([boom])
    for k, v in next(boom_dotnotation_dicts).items():
        print(f'{k}: {v}')

    print('\nDataframe:\n')
    boom_dataframe = OtlmowConverter.to_dataframe([boom])
    print(boom_dataframe.to_string())

