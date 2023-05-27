
from database import db
from models.ProgrammingLanguage import ProgrammingLanguage


def seed_programming_languages(programming_languages: list):
    for language in programming_languages:
        language_name = language['name']
        alt_name = language['alt_name']

        new_language = ProgrammingLanguage(
            name=language_name,
            alt_name=alt_name,
            active=1
        )
        # db.add(new_language)

    # db.commit()
