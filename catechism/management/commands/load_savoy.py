import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

CHAPTERS = [
    {"name": "Of the Holy Scriptures", "slug": "of-the-holy-scriptures",
     "order": 1, "description": "The authority, sufficiency, and perspicuity of Scripture"},
    {"name": "Of God and of the Holy Trinity", "slug": "of-god-and-the-holy-trinity",
     "order": 2, "description": "The being, attributes, and persons of the Godhead"},
    {"name": "Of God's Eternal Decree", "slug": "of-gods-eternal-decree",
     "order": 3, "description": "God's eternal decrees, including predestination and election"},
    {"name": "Of Creation", "slug": "of-creation",
     "order": 4, "description": "The creation of all things by God"},
    {"name": "Of Providence", "slug": "of-providence",
     "order": 5, "description": "God's preservation and governing of all creatures"},
    {"name": "Of the Fall of Man, of Sin, and of the Punishment thereof",
     "slug": "of-the-fall-of-man",
     "order": 6, "description": "The fall and original sin"},
    {"name": "Of God's Covenant", "slug": "of-gods-covenant",
     "order": 7, "description": "The covenant of works and the covenant of grace"},
    {"name": "Of Christ the Mediator", "slug": "of-christ-the-mediator",
     "order": 8, "description": "The person and offices of Christ as Mediator"},
    {"name": "Of Free Will", "slug": "of-free-will",
     "order": 9, "description": "The state of man's will in its various conditions"},
    {"name": "Of Effectual Calling", "slug": "of-effectual-calling",
     "order": 10, "description": "God's effectual calling of His elect"},
    {"name": "Of Justification", "slug": "of-justification",
     "order": 11, "description": "Justification by faith alone"},
    {"name": "Of Adoption", "slug": "of-adoption",
     "order": 12, "description": "The grace of adoption as children of God"},
    {"name": "Of Sanctification", "slug": "of-sanctification",
     "order": 13, "description": "The renewal of the whole man after the image of God"},
    {"name": "Of Saving Faith", "slug": "of-saving-faith",
     "order": 14, "description": "The grace of faith wrought by the Spirit of God"},
    {"name": "Of Repentance unto Life and Salvation",
     "slug": "of-repentance-unto-life",
     "order": 15, "description": "The evangelical grace of repentance"},
    {"name": "Of Good Works", "slug": "of-good-works",
     "order": 16, "description": "Good works as the fruit of faith and obedience"},
    {"name": "Of the Perseverance of the Saints",
     "slug": "of-the-perseverance-of-the-saints",
     "order": 17, "description": "The perseverance of the elect in the state of grace"},
    {"name": "Of the Assurance of Grace and Salvation",
     "slug": "of-the-assurance-of-grace-and-salvation",
     "order": 18, "description": "The assurance of salvation grounded on God's promises"},
    {"name": "Of the Law of God", "slug": "of-the-law-of-god",
     "order": 19, "description": "The moral law and its uses under the covenant of grace"},
    {"name": "Of the Gospel, and of the Extent of the Grace Thereof",
     "slug": "of-the-gospel",
     "order": 20, "description": "The gospel of grace and its universal offer"},
    {"name": "Of Christian Liberty and Liberty of Conscience",
     "slug": "of-christian-liberty",
     "order": 21, "description": "The liberty purchased by Christ for believers"},
    {"name": "Of Religious Worship and the Sabbath Day",
     "slug": "of-religious-worship",
     "order": 22, "description": "The regulation of worship and the Sabbath"},
    {"name": "Of Lawful Oaths and Vows", "slug": "of-lawful-oaths-and-vows",
     "order": 23, "description": "The right use of lawful oaths and vows"},
    {"name": "Of the Civil Magistrate", "slug": "of-the-civil-magistrate",
     "order": 24, "description": "The authority and duties of the civil magistrate"},
    {"name": "Of Marriage", "slug": "of-marriage",
     "order": 25, "description": "The institution and regulation of marriage"},
    {"name": "Of the Church", "slug": "of-the-church",
     "order": 26, "description": "The visible and invisible Church"},
    {"name": "Of the Communion of Saints", "slug": "of-the-communion-of-saints",
     "order": 27, "description": "The fellowship of believers united to Christ"},
    {"name": "Of the Sacraments", "slug": "of-the-sacraments",
     "order": 28, "description": "The nature and efficacy of the sacraments"},
    {"name": "Of Baptism", "slug": "of-baptism",
     "order": 29, "description": "The sacrament of baptism and its administration"},
    {"name": "Of the Lord's Supper", "slug": "of-the-lords-supper",
     "order": 30, "description": "The sacrament of the Lord's Supper"},
    {"name": "Of the State of Man After Death, and of the Resurrection of the Dead",
     "slug": "of-the-state-of-man-after-death",
     "order": 31, "description": "The state of the soul after death and the resurrection"},
    {"name": "Of the Last Judgment", "slug": "of-the-last-judgment",
     "order": 32, "description": "The appointed day of the last judgment"},
]


class Command(BaseCommand):
    help = "Load Savoy Declaration of Faith into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "savoy_declaration.json"
        if data_is_current("catechism-savoy", data_path):
            self.stdout.write("Savoy Declaration data unchanged, skipping.")
            return

        with open(data_path) as f:
            data = json.load(f)

        total = sum(len(ch["Sections"]) for ch in data["Data"])

        catechism, _ = Catechism.objects.update_or_create(
            slug='savoy',
            defaults={
                'name': 'Savoy Declaration',
                'abbreviation': 'SD',
                'description': (
                    'The Savoy Declaration (1658), produced by a conference of '
                    'Congregational churches at the Savoy Palace in London, is a '
                    'modification of the Westminster Confession for Congregational '
                    'polity. Drafted by Thomas Goodwin and John Owen, it represents '
                    'the confessional standard of English Congregationalism.'
                ),
                'year': 1658,
                'total_questions': total,
                'document_type': Catechism.CONFESSION,
            }
        )

        seq = 0
        for chapter_data in data["Data"]:
            ch_num = int(chapter_data["Chapter"])
            ch_info = CHAPTERS[ch_num - 1]

            section_count = len(chapter_data["Sections"])
            start = seq + 1
            end = seq + section_count

            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=ch_info["slug"],
                defaults={
                    "name": ch_info["name"],
                    "order": ch_info["order"],
                    "question_start": start,
                    "question_end": end,
                    "description": ch_info["description"],
                }
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} chapter: {topic.name}")

            for section in chapter_data["Sections"]:
                seq += 1
                Question.objects.update_or_create(
                    catechism=catechism,
                    number=seq,
                    defaults={
                        "question_text": chapter_data["Title"],
                        "answer_text": section["Content"],
                        "topic": topic,
                    }
                )

        mark_data_current("catechism-savoy", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {seq} Savoy Declaration sections"))
