"""P4 presentation copy and non-medical tip cards.

Tips are human-readable paraphrases of the cited evidence in data/curated_evidence.json,
not personalized prescriptions and not model-generated medical advice.
"""

COPY = {
    "fr": {
        "home": "Accueil", "history": "Mes conversations", "saved": "Conseils enregistrés",
        "new": "Nouvelle conversation", "language": "Langue", "science": "Les coulisses du RAG",
        "mode": "Méthode de recherche", "k": "Passages retenus", "provider": "Génération",
        "hero_badge": "VOTRE COACH DOCUMENTAIRE", "hero_title": "Bien manger. Mieux bouger.",
        "hero_subtitle": "Des réponses claires sur la nutrition sportive et la gestion du poids, fondées sur des sources scientifiques.",
        "ask": "Que souhaitez-vous savoir aujourd'hui ?",
        "ask_placeholder": "Ex. : Que manger après la musculation ?",
        "ideas": "Quelques idées pour commencer", "goals": "Votre objectif",
        "goals_intro": "Choisissez ce qui vous intéresse : les réponses s'appuieront sur les documents liés à ce thème.",
        "muscle": "Prise de muscle", "muscle_detail": "Protéines, récupération, entraînement",
        "weight": "Gestion du poids", "weight_detail": "Équilibre alimentaire et activité physique",
        "general": "Manger équilibré", "general_detail": "Nutrition et bonnes habitudes",
        "choose": "Choisir", "selected": "Sélectionné", "answer": "Vos réponses",
        "empty_title": "Votre espace nutrition commence ici", "empty_body": "Choisissez un objectif ou posez votre question. NutriSport recherche les informations dans ses sources pour vous répondre.",
        "tips": "Le conseil du moment", "next_tip": "Autre conseil →",
        "sources": "Voir les sources", "source_link": "Ouvrir la source", "save": "Enregistrer ce conseil", "saved_ok": "Conseil enregistré",
        "save_empty": "Aucun conseil enregistré pour le moment.", "history_empty": "Aucune conversation pour le moment.",
        "history_intro": "Retrouvez vos questions de cette session.", "back": "Retour à l'accueil", "question": "Question",
        "offline": "Les extraits ci-dessous sont affichés en mode démonstration : configurez Grok pour obtenir une réponse générée.",
        "loading": "Je consulte les sources nutritionnelles…",
        "no_key": "Clé Grok absente : les réponses seront des extraits du corpus.",
        "disclaimer": "Information éducative uniquement. NutriSport ne fournit ni diagnostic ni programme médical personnalisé.",
        "based_on": "Réponse issue de documents sélectionnés", "saved_notes": "Vos réponses enregistrées pendant cette session.",
        "question_examples": [
            "💪 Que manger pour prendre du muscle ?", "🥣 Que manger après l'entraînement ?",
            "⚡ Quel rôle jouent les calories ?", "🥬 Quels aliments pour gérer son poids ?"
        ],
    },
    "en": {
        "home": "Home", "history": "My conversations", "saved": "Saved advice",
        "new": "New conversation", "language": "Language", "science": "How the RAG works",
        "mode": "Search method", "k": "Retrieved passages", "provider": "Generation",
        "hero_badge": "YOUR EVIDENCE-BASED NUTRITION GUIDE", "hero_title": "Eat well. Move better.",
        "hero_subtitle": "Clear answers about sports nutrition and healthy weight management, grounded in scientific sources.",
        "ask": "What would you like to know today?", "ask_placeholder": "E.g. What should I eat after strength training?",
        "ideas": "Try one of these questions", "goals": "Your goal",
        "goals_intro": "Choose your interest to prioritize relevant nutrition sources.",
        "muscle": "Build muscle", "muscle_detail": "Protein, recovery, training",
        "weight": "Manage weight", "weight_detail": "Balanced eating and physical activity",
        "general": "Eat balanced", "general_detail": "Nutrition and healthy habits",
        "choose": "Choose", "selected": "Selected", "answer": "Your answers",
        "empty_title": "Your nutrition journey starts here", "empty_body": "Choose a goal or ask a question. NutriSport checks its sources before answering.",
        "tips": "Nutrition tip", "next_tip": "Another tip →",
        "sources": "View sources", "source_link": "Open source", "save": "Save this advice", "saved_ok": "Advice saved",
        "save_empty": "No saved advice in this session yet.", "history_empty": "No conversations yet.",
        "history_intro": "Your questions in this session.", "back": "Back to home", "question": "Question",
        "offline": "The text below is from offline source extracts. Configure Grok to enable generated answers.",
        "loading": "Checking nutrition sources…", "no_key": "No Grok key configured: responses will show source extracts.",
        "disclaimer": "Educational information only. No diagnosis or individualized medical meal plans.",
        "based_on": "Grounded in selected source documents", "saved_notes": "Responses saved during this session.",
        "question_examples": [
            "💪 What should I eat to build muscle?", "🥣 What should I eat after training?",
            "⚡ What role do calories play?", "🥬 Which foods support weight management?"
        ],
    },
    "ar": {
        "home": "الرئيسية", "history": "محادثاتي", "saved": "نصائح محفوظة",
        "new": "محادثة جديدة", "language": "اللغة", "science": "خيارات البحث المتقدمة",
        "mode": "طريقة البحث", "k": "عدد المقاطع", "provider": "توليد الإجابة",
        "hero_badge": "دليلك للمعلومات الغذائية الموثوقة", "hero_title": "غذاء أفضل. نشاط أفضل.",
        "hero_subtitle": "إجابات مبنية على مصادر علمية حول تغذية الرياضيين وإدارة الوزن بشكل صحي.",
        "ask": "ما الذي تود معرفته اليوم؟", "ask_placeholder": "مثال: ماذا آكل بعد تمارين المقاومة؟",
        "ideas": "أسئلة مقترحة", "goals": "هدفك",
        "goals_intro": "اختر مجال اهتمامك للعثور على المصادر الغذائية الملائمة.",
        "muscle": "بناء العضلات", "muscle_detail": "البروتين والتعافي والتمارين",
        "weight": "إدارة الوزن", "weight_detail": "الغذاء المتوازن والنشاط البدني",
        "general": "غذاء متوازن", "general_detail": "التغذية والعادات الصحية",
        "choose": "اختيار", "selected": "محدد", "answer": "إجاباتك",
        "empty_title": "ابدأ رحلتك الغذائية هنا", "empty_body": "اختر هدفاً أو اطرح سؤالاً. يبحث المساعد في مصادره قبل تقديم الإجابة.",
        "tips": "نصيحة غذائية", "next_tip": "نصيحة أخرى →",
        "sources": "عرض المصادر", "source_link": "فتح المصدر", "save": "حفظ النصيحة", "saved_ok": "تم حفظ النصيحة",
        "save_empty": "لم تحفظ أي نصيحة في هذه الجلسة.", "history_empty": "لا توجد محادثات بعد.",
        "history_intro": "أسئلتك خلال هذه الجلسة.", "back": "العودة للرئيسية", "question": "السؤال",
        "offline": "هذه مقتطفات من المصادر في وضع العرض دون نموذج لغوي. قم بإعداد Grok للحصول على إجابات مولدة.",
        "loading": "أبحث في المصادر الغذائية…", "no_key": "لم يتم إعداد مفتاح Grok: سيتم عرض مقتطفات من المصادر.",
        "disclaimer": "معلومات تثقيفية فقط، وليست تشخيصاً أو برنامجاً علاجياً فردياً.",
        "based_on": "معلومات من مصادر علمية مختارة", "saved_notes": "إجابات محفوظة خلال هذه الجلسة.",
        "question_examples": [
            "💪 ماذا آكل لبناء العضلات؟", "🥣 ماذا آكل بعد التمرين؟",
            "⚡ ما دور السعرات الحرارية؟", "🥬 ما الأطعمة المناسبة لإدارة الوزن؟"
        ],
    },
}

TIPS = {
    "fr": [
        ("Une routine riche en protéines", "L'apport protéique total de la journée compte dans l'adaptation musculaire à l'entraînement.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("La récupération ne se joue pas à la minute", "Les protéines peuvent être consommées avant ou après l'effort : le total quotidien demeure important.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("Équilibre sur la durée", "Pour la gestion du poids, les habitudes alimentaires durables comptent davantage que les solutions rapides.", "CDC — Steps for Losing Weight", "https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html"),
        ("Bouger et bien manger", "L'entraînement de résistance et un apport protéique suffisant contribuent à préserver la masse maigre.", "ISSN — Diets and Body Composition", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/"),
    ],
    "en": [
        ("Protein across the day", "Total daily protein intake matters for muscle adaptation to resistance training.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("Recovery is not a one-minute window", "Protein can be consumed before or after exercise; total daily intake still matters.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("Long-term balance", "For weight management, sustainable habits matter more than quick fixes.", "CDC — Steps for Losing Weight", "https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html"),
        ("Strength and nutrition", "Resistance training and adequate protein can support lean mass retention.", "ISSN — Diets and Body Composition", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/"),
    ],
    "ar": [
        ("البروتين خلال اليوم", "إجمالي البروتين اليومي مهم للتكيف العضلي مع تمارين المقاومة.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("التعافي ليس مسألة دقائق", "يمكن تناول البروتين قبل التمرين أو بعده، مع أهمية الكمية الإجمالية اليومية.", "ISSN — Protein and Exercise", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/"),
        ("توازن مستمر", "العادات المستدامة لإدارة الوزن أفضل من الحلول السريعة.", "CDC — Steps for Losing Weight", "https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html"),
        ("النشاط والتغذية", "تمارين المقاومة والبروتين الكافي قد يساعدان في الحفاظ على الكتلة العضلية.", "ISSN — Diets and Body Composition", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/"),
    ],
}

def ui_text(language):
    return COPY.get(language, COPY['fr'])


def tips_for(language):
    return TIPS.get(language, TIPS['fr'])
