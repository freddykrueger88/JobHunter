"""E-Mail-Vorlagen fuer typische Bewerbungssituationen."""
from typing import Literal

TemplateType = Literal['followup', 'nachfrage', 'absage_antwort', 'zusage', 'termin_bestaetigen', 'termin_absagen']

TEMPLATES_DE = {
    'followup': {
        'betreff': 'Nachfrage zu meiner Bewerbung als {stelle} – {vorname} {nachname}',
        'body': """Sehr geehrte {anrede},

vor {tage} Tagen habe ich Ihnen meine Bewerbung als {stelle} zugesendet und moechte mich hoeflich erkundigen, ob meine Unterlagen vollstaendig vorliegen und wie der aktuelle Stand des Auswahlverfahrens ist.

Fuer Rueckfragen stehe ich jederzeit zur Verfuegung.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
    'nachfrage': {
        'betreff': 'Status meiner Bewerbung als {stelle}',
        'body': """Sehr geehrte {anrede},

ich bewerbe mich bei {firma} fuer die Stelle als {stelle} und wuerde mich ueber eine kurze Rueckmeldung zum aktuellen Stand freuen.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
    'absage_antwort': {
        'betreff': 'Re: Ihre Entscheidung bezueglich meiner Bewerbung',
        'body': """Sehr geehrte {anrede},

vielen Dank fuer Ihre Rueckmeldung. Ich nehme Ihre Entscheidung mit Verstaendnis zur Kenntnis und bedanke mich fuer die Zeit, die Sie meiner Bewerbung gewidmet haben.

Falls sich in Zukunft eine passende Gelegenheit ergibt, wuerde ich mich freuen, erneut in Kontakt zu treten.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
    'zusage': {
        'betreff': 'Bestaetigung meiner Zusage – {stelle}',
        'body': """Sehr geehrte {anrede},

hiermit bestatige ich meine Zusage fuer die Stelle als {stelle} bei {firma}. Ich freue mich sehr auf die Zusammenarbeit und den Start am {datum}.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
    'termin_bestaetigen': {
        'betreff': 'Bestaetigung Vorstellungsgespraech am {datum}',
        'body': """Sehr geehrte {anrede},

hiermit bestatige ich den Termin fuer unser Vorstellungsgespraech am {datum} um {uhrzeit} Uhr. Ich freue mich auf das Gespraech.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
    'termin_absagen': {
        'betreff': 'Absage Vorstellungsgespraech am {datum}',
        'body': """Sehr geehrte {anrede},

leider muss ich den vereinbarten Termin am {datum} absagen. Ich entschuldige mich fuer die Unannehmlichkeiten und wuerde mich ueber einen Alternativtermin freuen.

Mit freundlichen Gruessen
{vorname} {nachname}""",
    },
}

def get_template(template_type: TemplateType, lang: str = 'de') -> dict:
    templates = TEMPLATES_DE  # EN-Templates koennen spaeter ergaenzt werden
    return templates.get(template_type, {'betreff': '', 'body': ''})

def fill_template(template_type: TemplateType, lang: str = 'de', **kwargs) -> dict:
    t = get_template(template_type, lang)
    return {
        'betreff': t['betreff'].format_map({**kwargs}),
        'body': t['body'].format_map({**kwargs}),
    }
