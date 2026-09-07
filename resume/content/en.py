import resume.content.hyprlinks as links
from resume.models import ContactInfo, MiscItem, PersonalProject, Post, Profile, Resume, Study

## Jobs
namr_en = Post(
    title="Data Scientist",
    company="nam.R",
    company_link=links.namr,
    start_month="March 2026",
    end_month="July 2026",
    desc=[
        "Worked on a wide variety of tasks until the company's liquidation, without a single major project",
        "Rewrote internal libraries to reduce technical debt",
        "Scraped geographic data",
        "Deployed model training workflows on GCP"
    ],
    skills=["Deployment", "ML/DL Training", "Web Scraping", "Geospatial Data"],
    tools=["GCP", "DBeaver", "QGIS"],
    region="Paris, France"
)

trickstr_en = Post(
    title="AI Consultant / Data Scientist",
    company="Trickstr (Vectors Startup)",
    company_link=links.trickstr,
    start_month="January 2026",
    end_month="March 2026",
    desc=[
        ("Internal reporting automation", [
            "Gathered requirements with Vectors consultants",
            "Developed a Streamlit application",
            "Securely deployed the application internally"
        ]),
        ("Study of political biases in AI models", [
            "Designed a scientific methodology to assess LLM 'opinions' as neutrally as possible",
            "Created metrics and indices to compare AI 'opinions' with those of the French population",
            "Conducted large-scale surveys across numerous language models using different settings (personas, geolocation, language, ...)",
            links.ai_bias_article
        ]),
        ("'AI Reputation' study", [
            "Extended the previous study to brands, products, public figures, and other entities",
            "Created detailed reports, benchmarks, and visualizations",
            links.benchmark_airep_cac40,
        ]),
    ],
    skills=[
        "Data Science",
        "API Integration",
        "R&D",
        "GEO (Generative Engine Optimization)",
        "Prompt Engineering"
    ],
    tools=["Google Cloud Platform", "Docker", "Streamlit"],
    region="Paris, France"
)

vectors_en = Post(
    title="AI Consultant / Data Scientist",
    company="Vectors",
    company_link=links.vectors,
    start_month="May 2023",
    end_month="December 2025",
    desc=[
        "Optimized internal processes using AI",
        "Performed large-scale web scraping for various projects (e.g. postal codes for CAC 40 company websites)",
        "Conducted data analyses on clients' social media performance",
        ("Developed a platform to detect social media posts related to the Paris 2024 Olympic Games", [
            "The goal was to detect posts from Carrefour's competitors",
            "Built a dataset containing the physical addresses of Carrefour stores and their competitors",
            "Linked physical addresses to Facebook, Instagram, X, and TikTok pages",
            "Trained AI models to detect Olympic merchandise in images",
            "Deployed a Streamlit platform to browse suspicious posts"
        ])
    ],
    tools=["Neo4j", "Elasticsearch", "Streamlit", "Midjourney", "ElevenLabs"],
    skills=[
        "R&D",
        "Consulting",
        "Problem Analysis",
        "Feasibility Studies",
        "State-of-the-Art Research",
        "Web Scraping",
        "Data Visualization",
        "Prompt Engineering"
    ],
    region="Paris, France"
)

kitware_en = Post(
    title="Machine Learning R&D Intern",
    company="Kitware",
    company_link=links.kitware,
    start_month="July 2022",
    end_month="December 2022",
    desc=[
        ("X-ray image segmentation", [
            "Used the Mask R-CNN model",
            "Modified internal model metrics to account for X-ray image-specific constraints such as overlapping objects",
            "Benchmarked models and developed a training loop for sensitive data",
        ]),
        ("DICOM file classification", [
            "Worked with large medical DICOM files structured as key-value pairs",
            "Tokenized textual fields",
            "Used Random Forest models to identify relevant fields",
            "Developed a small model for 3D image classification"
        ]),
        "Implemented a GPU-compatible 3D filter in PyTorch",
    ],
    tools=["PyTorch", "Mask R-CNN", "Random Forest"],
    skills=["Classification", "Model Modification", "Vector Computation", "Computer Vision"],
    region="Lyon, France"
)

## Studies
master_sherbrooke_en = Study(
    "Master's Degree - Université de Sherbrooke",
    "Engineering Management",
    "Montreal, Canada",
    [
        "Law",
        "Finance",
        "Team Management",
        "Leadership",
        "Project Management",
        "Creativity",
        "Communication",
        "Negotiation"
    ]
)

enseeiht_en = Study(
    "Engineering Degree - ENSEEIHT",
    "Digital Sciences",
    "Toulouse, France",
    [
        "Deep Learning",
        "Optimization",
        "Operations Research",
        "Imperative Programming",
        "Object-Oriented Programming",
        "Concurrent Programming",
        "Graph Theory",
        "Scrum"
    ]
)

## Projects
homelab_en = PersonalProject(
    title="Proxmox Homelab",
    desc=[
        "Deployed and maintained a fleet of around thirty Linux virtual machines",
        "Developed and deployed custom tools"
    ],
    modality="Solo",
    year="2024 - Present",
    tools=[
        "Proxmox",
        "Meilisearch",
        "PostgreSQL",
        "Minio",
        "Caddy",
        "CrowdSec",
        "Pi-hole",
        "Vector",
        "Grafana",
        "UptimeKuma",
        links.pipechecker,
        links.filekeeper
    ],
    skills=[
        "DNS",
        "Reverse Proxy",
        "Virtual Machines",
        "Deployment",
        "Notifications",
        "Maintenance",
        "Networking"
    ]
)

frataga_en = PersonalProject(
    title="Frataga - DnD Archetype Search Engine",
    desc=[
        "Created archetype collections, including a DnD collection and a Greek deity collection",
        "Vectorized archetypes and user queries, then performed vector search",
        "Deployed a Streamlit interface"
    ],
    modality="Duo",
    year=2025,
    links=[links.frataga],
    skills=["Vector Search", "Self-Hosting", "Vector Databases"],
    tools=["Midjourney", "Streamlit", "CamemBERT"]
)

deepfakes_en = PersonalProject(
    title="Synthetic Face Generation with GANs",
    desc=[
        "Built a first version in 2022 with limited results",
        "Built a second version in 2025 with full training on a dedicated GPU and significantly improved results",
    ],
    tools=["Generative Adversarial Network", "Weights & Biases"],
    skills=["AI Model Training", "Training Evaluation"],
    modality="Solo",
    year="2022 and 2025",
)

prez_7fault_en = PersonalProject(
    "President of 7Fault, ENSEEIHT Game Development Club",
    desc=[
        ("Games I worked on during game jams:", [
            links.jump_slime_jump,
            links.loading,
            links.bricobot
        ])
    ],
    modality="Team of 3 to 5",
    year="2020 - 2021",
    skills=["Game Development", "Design Patterns", "Pixel Art", "Music"],
    tools=["Unity", "Bosca Ceoil", "FLStudio"]
)

league_ai_en = PersonalProject(
    "Strategic AI for League of Legends",
    year=2020,
    modality="Duo",
    desc=[
        "The goal was to optimize champion selection in League of Legends",
        "Tested various methods to vectorize champions in order to compare them"
    ],
    skills=["Vectorization", "Statistical Analysis", "Game Theory"],
    tools=["VAE (Variational Auto-Encoder)"]
)
hypnose_en = MiscItem(
    "Street Hypnosis", "I'm a street hypnotist since about 12 years now, I post the videos people send me on Instagram !",
    links=[links.hypnose_insta, links.blog_hypnose],
)

resume_en = Resume(
    profile=Profile(
        name="Alexandre DANG",
        title="Data Scientist / Machine Learning Engineer",
        region="Paris, France",
        ascii_art="""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⢿⠙⠛⠿⣿⡿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⢀⠠⠈⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠠⠈⠀⠀⠀⠀⠀⠂⠀⡀⠈⠻⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⣸⣿⡀⠀⠐⠀⠈⠀⠠⠀⠀⠀⠂⠈⠻⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠐⢸⣿⣿⣿⣿⣿⣷⣄⠐⠀⠀⠈⠀⠠⠐⠈⢹⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢐⣿⠿⠛⠉⢻⣿⣿⣿⣿⣶⣆⡁⠀⡀⠀⠠⣈⣹⣿
⣿⣿⣿⣿⣿⣿⣿⣿⢟⡠⢸⡃⢠⠀⡂⠨⣿⣿⣿⠟⠋⠉⠘⢶⣶⡄⣲⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡇⣞⢋⢺⣇⣀⠉⠁⢀⢧⣿⠁⠠⠊⢙⠄⠸⣿⣂⡙⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣧⡛⠪⢸⣿⣿⣿⣿⣿⣾⣿⣿⣴⣤⣤⣠⣸⡋⢝⣳⢸⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠻⣿⣿⣿⣭⣿⣿⣿⣿⣿⣿⡿⠏⣛⣚⣡⣾⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣜⡛⠿⣿⣿⣿⣿⡿⠟⣫⣴⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣖⢀⡀⣀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠡⣼⣿⣿⡄⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⢻⣿⣿⠁⠀⢀⠈⢿⣿⣿⣿⣿⣿⣿
        """,
        highlights=[
            "Highly proficient in Python",
            "Street hypnotist",
            "Passionate about computer science"
        ],
        current="Looking for an R&D position in AI",
        contact=[
            ContactInfo("@ Email", "alex@auragan.fr", url="mailto:alex@auragan.fr"),
            ContactInfo("✆ Tel", "06 33 02 82 75", url="tel:+33633038357"),
            ContactInfo("⛴ Github", "AlexAuragan", url="https://github.com/AlexAuragan"),
            ContactInfo("♠ Website", "auragan.fr", url="https://auragan.fr")
        ]
    ),
    work_experience=[
        namr_en,
        trickstr_en,
        vectors_en,
        kitware_en,
    ],
    personal_projects=[
        homelab_en,
        frataga_en,
        deepfakes_en,
        prez_7fault_en,
        league_ai_en,
    ],
    studies=[
        master_sherbrooke_en,
        enseeiht_en,
    ],
    misc=[hypnose_en],
)
