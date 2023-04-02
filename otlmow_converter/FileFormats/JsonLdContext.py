from typing import Optional


class JsonLdContext:
    context_dict = {
        'asset': 'https://data.awvvlaanderen.be/id/asset/',
        'assetrelatie': 'https://data.awvvlaanderen.be/id/assetrelatie/',
        'onderdeel': 'https://wegenenverkeer.data.vlaanderen.be/ns/onderdeel#',
        'installatie': 'https://wegenenverkeer.data.vlaanderen.be/ns/installatie#',
        'imel': 'https://wegenenverkeer.data.vlaanderen.be/ns/implementatieelement#',
        'kl': 'https://wegenenverkeer.data.vlaanderen.be/id/concept/',
        'abs': 'https://wegenenverkeer.data.vlaanderen.be/ns/abstracten#',
        'pem': 'https://wegenenverkeer.data.vlaanderen.be/ns/proefenmeting#',
        'loc': 'https://loc.data.wegenenverkeer.be/ns/implementatieelement#'
    }

    @staticmethod
    def replace_context(short_uri: str, context_dict: dict) -> Optional[str]:
        if short_uri is None:
            return None
        if ':' not in short_uri:
            return short_uri
        context = short_uri.split(':')[0]
        if context not in context_dict:
            return short_uri
        return short_uri.replace(f'{context}:', context_dict[context])
