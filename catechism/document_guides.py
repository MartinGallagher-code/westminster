DOCUMENT_GUIDES = {
    'wsc': {
        'summary': (
            'A concise question-and-answer summary of Reformed doctrine designed for memorization, '
            'family worship, and first steps in theological study.'
        ),
        'date': '1647',
        'authorship': (
            'Prepared by the Westminster Assembly and approved for use in the churches of Scotland and England.'
        ),
        'history': (
            'The Shorter Catechism distills the Assembly’s theology into brief answers that move from humanity’s '
            'chief end through Scripture, God, Christ, salvation, the law, sacraments, prayer, and the Lord’s Prayer.'
        ),
        'context': (
            'It has served for centuries as a teaching text for children, new believers, households, churches, '
            'and schools in the English-speaking Reformed tradition.'
        ),
        'how_to_study': [
            'Read one question slowly, then compare its proof texts before moving on.',
            'Use the topic groupings to trace a doctrine from first principles to practice.',
            'Pair shorter answers with Larger Catechism parallels when a topic needs more depth.',
        ],
        'key_features': ['Compact answers', 'Memorization-friendly', 'Strong first catechism'],
    },
    'wlc': {
        'summary': (
            'A fuller catechetical treatment of Reformed doctrine, expanding the same theological system with more '
            'detailed pastoral and ethical instruction.'
        ),
        'date': '1647',
        'authorship': 'Prepared by the Westminster Assembly as the companion catechism for more mature instruction.',
        'history': (
            'The Larger Catechism develops the Assembly’s teaching at greater length, especially on Christ, '
            'the covenant of grace, the Ten Commandments, the sacraments, and prayer.'
        ),
        'context': (
            'It is especially useful for adult classes, officers, teachers, and readers who want more precision '
            'than the Shorter Catechism can provide.'
        ),
        'how_to_study': [
            'Use the sidebar to stay inside a doctrinal section and read several related answers together.',
            'Compare answers with the Shorter Catechism to see what the Larger Catechism expands.',
            'Pay special attention to the commandments and Lord’s Prayer sections for practical theology.',
        ],
        'key_features': ['Detailed exposition', 'Pastoral ethics', 'Rich Westminster companion'],
    },
    'wcf': {
        'summary': (
            'The central doctrinal confession of the Westminster Standards, arranged as a chapter-by-chapter '
            'statement of Reformed theology.'
        ),
        'date': '1646',
        'authorship': (
            'Composed by the Westminster Assembly, a gathering of theologians and ministers meeting during the '
            'English Civil War period.'
        ),
        'history': (
            'The Confession presents a systematic account of Scripture, God, decree, creation, providence, covenant, '
            'Christ, salvation, worship, church, sacraments, civil authority, and last things.'
        ),
        'context': (
            'It became a defining confession for Presbyterian churches and remains one of the most influential '
            'Protestant confessions in English.'
        ),
        'how_to_study': [
            'Read a chapter end-to-end before opening individual sections for proof texts and commentary.',
            'Use comparison links to see how the catechisms state the same doctrine devotionally.',
            'Move through the chapters in order when studying the structure of Reformed systematic theology.',
        ],
        'key_features': ['Systematic confession', 'Chapter structure', 'Presbyterian standard'],
    },
    'heidelberg': {
        'summary': 'A warm and pastoral catechism organized around guilt, grace, and gratitude.',
        'date': '1563',
        'authorship': (
            'Produced in the Palatinate under Elector Frederick III, traditionally associated with Zacharias Ursinus '
            'and Caspar Olevianus.'
        ),
        'history': (
            'The Heidelberg Catechism was written to provide clear church instruction and unite Reformed teaching '
            'with devotional comfort.'
        ),
        'context': (
            'It is one of the Three Forms of Unity and remains beloved for its personal, consoling opening and '
            'practical shape.'
        ),
        'how_to_study': [
            'Follow the Lord’s Day structure as a weekly devotional rhythm.',
            'Notice how doctrine is framed through comfort, gratitude, and Christian living.',
            'Compare its sacramental language with Westminster and Belgic treatments.',
        ],
        'key_features': ['Pastoral tone', 'Lord’s Day rhythm', 'Three Forms of Unity'],
    },
    'belgic': {
        'summary': (
            'A Reformed confession written to explain and defend the faith of the churches in the Low Countries.'
        ),
        'date': '1561',
        'authorship': 'Written chiefly by Guido de Brès and received by the Reformed churches of the Netherlands.',
        'history': (
            'The Belgic Confession sets out Reformed teaching on Scripture, God, Christ, salvation, church, '
            'sacraments, civil government, and final judgment.'
        ),
        'context': (
            'It is one of the Three Forms of Unity and carries a strong apologetic and ecclesial character.'
        ),
        'how_to_study': [
            'Read articles in clusters to follow its confession of God, salvation, and the church.',
            'Use Scripture proofs to see how the confession argues from biblical texts.',
            'Compare ecclesiology and sacraments with Heidelberg and Dort.',
        ],
        'key_features': ['Confessional articles', 'Apologetic purpose', 'Ecclesial focus'],
    },
    'dort': {
        'summary': (
            'A synodical statement clarifying Reformed teaching on divine grace, election, atonement, conversion, '
            'and perseverance.'
        ),
        'date': '1618–1619',
        'authorship': 'Adopted by the Synod of Dort in response to the Remonstrant controversy.',
        'history': (
            'The Canons of Dort address disputed points of salvation with positive doctrinal statements and '
            'rejections of errors.'
        ),
        'context': (
            'They complete the Three Forms of Unity and are essential for understanding classic Reformed soteriology.'
        ),
        'how_to_study': [
            'Read each head of doctrine as a complete argument before comparing individual articles.',
            'Notice the pastoral purpose behind its careful distinctions.',
            'Pair the canons with Scripture references and related catechism questions on salvation.',
        ],
        'key_features': ['Doctrines of grace', 'Synodical canons', 'Soteriology focus'],
    },
}


def get_document_guide(slug):
    return DOCUMENT_GUIDES.get(slug)
