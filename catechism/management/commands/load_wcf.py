import json
from django.conf import settings
from django.core.management.base import BaseCommand
from catechism.management.commands._helpers import data_is_current, mark_data_current
from catechism.models import Catechism, Topic, Question

WCF_CHAPTERS = [
    {"name": "Of the Holy Scripture", "slug": "of-the-holy-scripture",
     "order": 1, "start": 1, "end": 10,
     "description": "The authority, sufficiency, and perspicuity of Scripture"},
    {"name": "Of God, and of the Holy Trinity", "slug": "of-god-and-the-holy-trinity",
     "order": 2, "start": 11, "end": 13,
     "description": "The being, attributes, and persons of the Godhead"},
    {"name": "Of God's Eternal Decree", "slug": "of-gods-eternal-decree",
     "order": 3, "start": 14, "end": 21,
     "description": "God's eternal decrees, including predestination and election"},
    {"name": "Of Creation", "slug": "of-creation",
     "order": 4, "start": 22, "end": 23,
     "description": "The creation of all things by God"},
    {"name": "Of Providence", "slug": "of-providence",
     "order": 5, "start": 24, "end": 30,
     "description": "God's most holy, wise, and powerful preserving and governing of all His creatures"},
    {"name": "Of the Fall of Man, of Sin, and of the Punishment thereof", "slug": "of-the-fall-of-man",
     "order": 6, "start": 31, "end": 36,
     "description": "The fall, original sin, and the punishment of sin"},
    {"name": "Of God's Covenant with Man", "slug": "of-gods-covenant-with-man",
     "order": 7, "start": 37, "end": 42,
     "description": "The covenant of works and the covenant of grace"},
    {"name": "Of Christ the Mediator", "slug": "of-christ-the-mediator",
     "order": 8, "start": 43, "end": 50,
     "description": "The person and offices of Christ as Mediator of the covenant of grace"},
    {"name": "Of Free Will", "slug": "of-free-will",
     "order": 9, "start": 51, "end": 55,
     "description": "The state of man's will in its various conditions"},
    {"name": "Of Effectual Calling", "slug": "of-effectual-calling",
     "order": 10, "start": 56, "end": 59,
     "description": "God's effectual calling of His elect by His Word and Spirit"},
    {"name": "Of Justification", "slug": "of-justification",
     "order": 11, "start": 60, "end": 65,
     "description": "Justification by faith alone through the imputed righteousness of Christ"},
    {"name": "Of Adoption", "slug": "of-adoption",
     "order": 12, "start": 66, "end": 66,
     "description": "The grace of adoption as children of God"},
    {"name": "Of Sanctification", "slug": "of-sanctification",
     "order": 13, "start": 67, "end": 69,
     "description": "The renewal of the whole man after the image of God"},
    {"name": "Of Saving Faith", "slug": "of-saving-faith",
     "order": 14, "start": 70, "end": 72,
     "description": "The grace of faith wrought by the Spirit of God"},
    {"name": "Of Repentance unto Life", "slug": "of-repentance-unto-life",
     "order": 15, "start": 73, "end": 78,
     "description": "The evangelical grace of repentance"},
    {"name": "Of Good Works", "slug": "of-good-works",
     "order": 16, "start": 79, "end": 85,
     "description": "Good works as the fruit of faith and obedience"},
    {"name": "Of the Perseverance of the Saints", "slug": "of-the-perseverance-of-the-saints",
     "order": 17, "start": 86, "end": 88,
     "description": "The perseverance of the elect in the state of grace"},
    {"name": "Of the Assurance of Grace and Salvation", "slug": "of-the-assurance-of-grace-and-salvation",
     "order": 18, "start": 89, "end": 92,
     "description": "The assurance of salvation grounded on the promises of God"},
    {"name": "Of the Law of God", "slug": "of-the-law-of-god",
     "order": 19, "start": 93, "end": 99,
     "description": "The moral law and its uses under the covenant of grace"},
    {"name": "Of Christian Liberty, and Liberty of Conscience", "slug": "of-christian-liberty",
     "order": 20, "start": 100, "end": 103,
     "description": "The liberty purchased by Christ for believers"},
    {"name": "Of Religious Worship and the Sabbath-day", "slug": "of-religious-worship",
     "order": 21, "start": 104, "end": 111,
     "description": "The regulation of worship and the Christian Sabbath"},
    {"name": "Of Lawful Oaths and Vows", "slug": "of-lawful-oaths-and-vows",
     "order": 22, "start": 112, "end": 118,
     "description": "The lawfulness and right taking of oaths and vows"},
    {"name": "Of the Civil Magistrate", "slug": "of-the-civil-magistrate",
     "order": 23, "start": 119, "end": 122,
     "description": "The authority and duties of the civil magistrate"},
    {"name": "Of Marriage and Divorce", "slug": "of-marriage-and-divorce",
     "order": 24, "start": 123, "end": 128,
     "description": "The institution, purposes, and regulation of marriage"},
    {"name": "Of the Church", "slug": "of-the-church",
     "order": 25, "start": 129, "end": 134,
     "description": "The visible and invisible Church and its Head"},
    {"name": "Of the Communion of the Saints", "slug": "of-the-communion-of-the-saints",
     "order": 26, "start": 135, "end": 137,
     "description": "The fellowship of believers united to Christ"},
    {"name": "Of the Sacraments", "slug": "of-the-sacraments",
     "order": 27, "start": 138, "end": 142,
     "description": "The nature and efficacy of the sacraments"},
    {"name": "Of Baptism", "slug": "of-baptism",
     "order": 28, "start": 143, "end": 149,
     "description": "The sacrament of baptism and its administration"},
    {"name": "Of the Lord's Supper", "slug": "of-the-lords-supper",
     "order": 29, "start": 150, "end": 157,
     "description": "The sacrament of the Lord's Supper and its right use"},
    {"name": "Of Church Censures", "slug": "of-church-censures",
     "order": 30, "start": 158, "end": 161,
     "description": "The necessity and purposes of church discipline"},
    {"name": "Of Synods and Councils", "slug": "of-synods-and-councils",
     "order": 31, "start": 162, "end": 166,
     "description": "The calling and authority of synods and councils"},
    {"name": "Of the State of Man After Death, and of the Resurrection of the Dead",
     "slug": "of-the-state-of-man-after-death",
     "order": 32, "start": 167, "end": 169,
     "description": "The state of the soul after death and the resurrection of the body"},
    {"name": "Of the Last Judgment", "slug": "of-the-last-judgment",
     "order": 33, "start": 170, "end": 172,
     "description": "The appointed day of the last judgment"},
]


class Command(BaseCommand):
    help = "Load Westminster Confession of Faith chapters and sections into the database"

    def handle(self, *args, **options):
        data_path = settings.BASE_DIR / "data" / "westminster_confession_of_faith.json"
        if data_is_current("catechism-wcf", data_path):
            self.stdout.write("WCF data unchanged, skipping.")
            return

        catechism, _ = Catechism.objects.update_or_create(
            slug='wcf',
            defaults={
                'name': 'Westminster Confession of Faith',
                'abbreviation': 'WCF',
                'description': (
                    'The Westminster Confession of Faith, composed in 1646, is a '
                    'comprehensive statement of Reformed doctrine in 33 chapters '
                    'covering the full range of Christian theology.'
                ),
                'year': 1646,
                'total_questions': 172,
                'document_type': Catechism.CONFESSION,
                'tradition': Catechism.WESTMINSTER,
            }
        )

        topic_map = {}
        for t in WCF_CHAPTERS:
            topic, created = Topic.objects.update_or_create(
                catechism=catechism,
                slug=t["slug"],
                defaults={
                    "name": t["name"],
                    "order": t["order"],
                    "question_start": t["start"],
                    "question_end": t["end"],
                    "description": t["description"],
                }
            )
            topic_map[(t["start"], t["end"])] = topic
            self.stdout.write(f"{'Created' if created else 'Updated'} chapter: {topic.name}")

        data_path = settings.BASE_DIR / "data" / "westminster_confession_of_faith.json"
        with open(data_path) as f:
            data = json.load(f)

        for entry in data["Data"]:
            num = entry["Number"]
            topic = None
            for (start, end), t in topic_map.items():
                if start <= num <= end:
                    topic = t
                    break

            Question.objects.update_or_create(
                catechism=catechism,
                number=num,
                defaults={
                    "question_text": entry["ChapterTitle"],
                    "answer_text": entry["Text"],
                    "topic": topic,
                    "proof_texts": entry.get("ProofTexts", ""),
                }
            )

        mark_data_current("catechism-wcf", data_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(data['Data'])} WCF sections"))
