import resume.content.hyprlinks as links
from resume.models import PersonalProject, Post, Profile, Resume, Study

## Jobs
trickstr_fr = Post(
    title="Consultant IA / Data scientist",
    company="Trickstr (Startup de Vectors)",
    company_link=links.trickstr,
    start_month="Janvier 2025",
    end_month="Mars 2025",
    desc=[
        ("Automatisation en interne de reporting", [
            "Étude du besoin avec les consultants Vectors",
            "Développement d'une app Streamlit",
            "Déploiement sécurisé en interne"
        ]),
        ("Étude des biais politques des IA", [
            "Mise en place d'une méthode scientifique pour évaluer de façon la plus neutre possible les 'opinions' des LLMs.",
            "Création de métriques et d'indice pour comparer les 'opinions' des IA avec celles de la population française",
            "Sondage de masse de nombreux modèles de langages avec différentes modalités (personnas, géo-localisation, langue, ...)",
            links.ai_bias_article
        ])
        ,
        ("Étude 'IA Réputation'", [
            "Généralisation de l'étude précédente aux marques, produits, personnes, etc",
            "Création de rapport détaillés, benchmark et graphiques",
            links.benchmark_airep_cac40,

        ]),
    ],
    skills=["Data Science", "API manipulation", "R&D", "GEO (Generative Engine Optimization)", "Prompt Engineering"],
    tools=["Google Cloud Platform", "Docker", "Streamlit"],
    region="Paris, France"
)

vectors_fr = Post(
    title="Consultant IA / Data scientist",
    company="Vectors",
    company_link=links.vectors,
    start_month="Mai 2023",
    end_month="Décembre 2024",
    desc=[
        "Optimization de processus interne grace à l'IA",
        "Scrapping de masse de données pour divers projets (ex: les CP des sites du CAC40)",
        "Études data sur les performances réseaux sociaux de nos clients",
        ("Mise en place d'une platforme pour détecter les posts parlant des JO de Paris 2024", [
            "Le but est de détecter les posts des concurrents de Carrefour",
            "Mise en place de la liste des adresses des toutes les enseignes de Carrefour et de ses concurrents",
            "Lien entre les adresses physiques et des pages Facebook / Instagram / X / Tiktok",
            "Entrainement d'IA pour détecter le merch JO sur les photos",
            "Déploiement d'une plateforme streamlit pour browser les posts suspects"
        ])
    ],
    tools=["Neo4j", "elasticsearch", "streamlit", "Midjourney", "Elevenlabs"],
    skills=["R&D", "Conseil", "Étude de problèmes", "Étude de faisabilité", "Suivis de l'état de l'art", "Web scraping", "Visualization de données",
            "Prompt Engineering"],
    region="Paris, France"
)

kitware_fr = Post(
    title="Stage R&D en Machine-learning",
    company="Kitware",
    company_link=links.kitware,
    start_month="Juillet 2022",
    end_month="Décembre 2022",
    desc=[
        ("Segmentation d'images rayon-X", [
            "Utilisation du modèle Mask-RCNN",
            "Modification de métriques interne au modèle pour répondre aux spécificité des images rayon-X (chevauchement)",
            "Benchmark et création d'une boucle d'entrainement pour des données sensibles",
        ]),
        ("Classification de fichier DICOM", [
            "Les DICOM sont de très gros fichiers médicaux sous forme key-value pair",
            "Tokenization de champs textuels",
            "Utilisation de random forest pour trouver les champs d'intérêts",
            "Petit modèle pour la classification d'images 3D"
        ]),
        "Implementation d'un filtre 3D en Pytorch (Compatible GPU)",
    ],
    tools=["Pytorch", "Mask-RCNN", "Random Forest"],
    skills=["Classification", "Modification de modèles","Calcul Vectoriel", "Vision par ordinateur"],
    region="Lyon, France"
)

## Studies
master_sherbrooke_fr = Study(
    "Maîtrise - Université de Sherbrook",
    "Gesion de l'ingénierie",
    "Montréal, Canada",
    ["Droit", "Finance", "Gestion d'équipe", "Leadership", "Gestion de projet", "créativité", "Communication", "Négociation"]
)

enseeiht_fr = Study(
    "Diplôme d'Ingénieur - ENSEEIHT",
    "sciences du numérique",
    "Toulouse, France",
    ["Apprentissage profond", "Optimisation", "Recherche opérationnelle", "Programmation impérative", "Programmation orientée objet",
     "Programmation concurrente", "Théorie des graphes", "Scrum"]
)

## Projects
homelab_fr = PersonalProject(
    title="Homelab Proxmox",
    desc=[
        "Déploiement et maintien d'une flotte d'une trentaine de VM linux",
        "Développement et déloiement d'outils custom"
     ],
    modality="Solo",
    year="2024 - Aujourd'hui",
    tools=["Proxmox", "Meillisearch", "PostgreSQL",
           "Minio", "Caddy", "Crowdec", "Pihole", "Vector", "Grafana", "UptimeKuma",
           links.pipechecker, links.filekeeper],
    skills=["DNS", "Reverse Proxy", "Virtual Machine", "Déploiement", "Notifications", "Maintenance", "Network"]
)

frataga_fr = PersonalProject(
    title="Frataga - Moteur de recherche d'archetypes DnD",
    desc=[
        "Création d'archetypes (une collection DnD et une collection divinitées grecques)",
        "Vectorisation des archetypes et d'une requête utilisateur + vecteur search",
        "Déploiement d'une interface Streamlit"
    ],
    modality="Duo",
    year=2025,
    links=[links.frataga],
    skills=["Vector search", "Self-hosting", "Vector Database"],
    tools=["Midjourney", "Streamlit", "CamemBert"]
)

deepfakes_fr = PersonalProject(
    title="Génération de faux visages par GAN",
    desc=[
        "Première version en 2022 avec des résultats peut concluants",
        "Deuxième version en 2025 avec un vrai entrainement sur GPU dédié avec de bien meilleurs résultats",
    ],
    tools=["Generative Adversarial Network", "Weights and biasses"],
    skills=["Entrainement de model d'IA", "Évaluation d'entrainement"],
    modality="Solo",
    year="2022 et 2025",
)

prez_7fault_fr = PersonalProject(
    "Président de 7Fault, club de Game Dev de l'ENSEEIHT",
    desc=[
        ("Jeux sur lesquels j'ai travaillé disponnibles lors de Game jams:", [
            links.jump_slime_jump, links.loading, links.bricobot
        ])
    ],
    modality="Équipe de 3 à 5",
    year="2020 - 2021",
    skills=["Game Dev", "Design Patern", "Pixel art", "Musique"],
    tools=["Unity", "Bosca Ceoil",  "FLStudio"]
)

league_ai_fr = PersonalProject(
    "IA stratégique sur League of Legends",
    year=2020,
    modality="Duo",
    desc=["Le but était d'optimiser la sélection de personnage dans League of Legends",
          "Nous avons tester diverses méthodes pour vectoriser les personnage pour pouvoir les comparer"],
    skills=["Vectorisation", "Analyse statistique", "Théorie des jeux"],
    tools=["VAE (Variational Auto-Encoder)"]
)


resume_fr = Resume(
    profile=Profile(
        name="Alexandre  DANG",
        title="Data Scientist / Ingénieur en ML",
        region="Paris, France",
        ascii_art="""

$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$@@@Bp&@$$$$$@$$$$$$$$$$$
$$$$$$$$$$$$$$$$%!?j.'>|Qq)QB$$$$$$$$$$$
$$$$$$$$$$$$$$@0_        .  lY&@$$$$$$$$
$$$$$$$$$$$$$@J.              .{w@$$$$$$
$$$$$$$$$$$$@#: "f}              ~O@$$$$
$$$$$$$$$$$$@j IZB&n~~+'           ]*$$$
$$$$$$$$$$$$W].0BBBBBBB#r:          f@$$
$$$$$$$$$$$@{ x%MQf|mBBBB8wv1'     ",}8$
$$$$$$$$$$$M:^q/`'!.:&BBBB8pX/(+-: +W8@$
$$$$$$$$$BXjv+M,^[_l.0pBd|:`-:^dBm+M$$$$
$$$$$$$$$qfm)~%u_I"^Itw8i.-^,r }%v?[a$$$
$$$$$$$$$M|Ut-#BBB%%%a%BWu|[<:,jLxCQ+@$$
$$$$$$$$$$@hJt|&BBB#Oq#BBBBBBB%dYnq|r@$$
$$$$$$$$$$$$$@Q(bBBB%M&BBBB%%bf|LYLa@$$$
$$$$$$$$$$$$$$$8Ljx0hM&8WoZvrJM@$$$$$$$$
$$$$$$$$$$$$$$$$$@Bam:,^''L8$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$@bn,pdp/n&@$$$$$$$$$$$
$$$$$$$$$$$$$$$$%Y! .z8BBh^`?J%@$$$$$$$$
$$$$$$$$$$$$$$@p>    _%BB|    !w$$$$$$$$

        """,
        highlights=[
            "Trop fort en python",
            "Hypnotiseur de rue",
        ],
        current="Cherche à travailler dans la R&D en IA",
    ),
    work_experience=[
        trickstr_fr,
        vectors_fr,
        kitware_fr,
    ],
    personal_projects=[
        homelab_fr,
        frataga_fr,
        deepfakes_fr,
        prez_7fault_fr,
        league_ai_fr,
    ],
    studies=[
        master_sherbrooke_fr,
        enseeiht_fr,
    ],
    misc=[],
    contacts=[],
)
