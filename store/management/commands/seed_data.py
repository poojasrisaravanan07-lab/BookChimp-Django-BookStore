from django.core.management.base import BaseCommand
from store.models import Category, Book, FeaturedSection


CATEGORIES = [
    ("Fiction", "bi-emoji-smile", "Stories that stay with you"),
    ("Non-fiction", "bi-lightbulb", "Real stories, real ideas"),
    ("Education", "bi-mortarboard", "Learn something new"),
    ("Technology", "bi-cpu", "Code, gadgets & the future"),
    ("Self-Help", "bi-heart", "Grow a little every day"),
    ("Biography", "bi-person-badge", "Lives worth reading about"),
    ("Fantasy", "bi-stars", "Escape to another world"),
    ("Business", "bi-graph-up-arrow", "Ideas that build empires"),
]

# (title, author, category, price, discount_price, rating, pages, description, flags)
BOOKS = [
    ("The Silent Orchard", "Meera Kapoor", "Fiction", 499, 349, 4.6, 312,
     "A quiet family drama set across three generations of an orchard family in the Nilgiris, "
     "exploring memory, inheritance and the things we never say out loud.",
     dict(is_bestseller=True, is_new_arrival=False, is_featured=True)),
    ("Atlas of Small Griefs", "Rohan Verma", "Fiction", 399, None, 4.3, 280,
     "A collection of interconnected short stories about loss, healing, and the strange comfort "
     "of ordinary days.",
     dict(is_bestseller=True)),
    ("The Last Lighthouse Keeper", "Alina Ford", "Fiction", 549, 429, 4.7, 356,
     "On a remote coastal island, the last lighthouse keeper uncovers a decades-old secret that "
     "will change everything she believes about her family.",
     dict(is_new_arrival=True, is_featured=True)),
    ("Deep Work Revisited", "Cal Whitmore", "Non-fiction", 599, None, 4.5, 240,
     "An updated, practical guide to focused success in a distracted world, with new research "
     "on attention and productivity.",
     dict(is_bestseller=True)),
    ("The Honest Economy", "Devika Rao", "Non-fiction", 449, 379, 4.2, 298,
     "A clear-eyed look at how everyday economic decisions shape society, told through real "
     "stories from around the world.",
     dict(is_new_arrival=True)),
    ("Learning Python the Practical Way", "Aditya Sharma", "Technology", 699, 549, 4.8, 420,
     "A hands-on, project-based introduction to Python programming for absolute beginners and "
     "career switchers alike.",
     dict(is_bestseller=True, is_featured=True)),
    ("Django for Builders", "Sarah Collins", "Technology", 749, None, 4.6, 380,
     "Build production-ready web applications with Django, covering everything from models to "
     "deployment.",
     dict(is_new_arrival=True)),
    ("The Machine Learning Field Guide", "Wei Zhang", "Technology", 899, 699, 4.4, 456,
     "A practical, jargon-free companion to modern machine learning concepts and applications.",
     dict(is_bestseller=True)),
    ("Atomic Focus", "Naina Iyer", "Self-Help", 349, 279, 4.5, 210,
     "Small, science-backed habits to help you concentrate, create, and finish what you start.",
     dict(is_bestseller=True)),
    ("The Quiet Confidence", "James Okafor", "Self-Help", 379, None, 4.3, 232,
     "A gentle, practical guide to building self-assurance without pretending to be someone "
     "you're not.",
     dict(is_new_arrival=True)),
    ("Letters to My Younger Self", "Kavya Menon", "Biography", 429, None, 4.6, 264,
     "A candid, moving memoir about ambition, failure, and finding purpose in an unpredictable "
     "career.",
     dict(is_featured=True)),
    ("The Architect of Silence", "Marcus Bell", "Biography", 499, 399, 4.4, 310,
     "The untold story of a reclusive architect whose buildings quietly reshaped modern cities.",
     dict(is_new_arrival=True)),
    ("The Glass Kingdom", "Priya Nair", "Fantasy", 549, None, 4.7, 402,
     "In a kingdom built entirely of enchanted glass, a young apprentice must choose between "
     "loyalty and the truth.",
     dict(is_bestseller=True, is_audiobook=True)),
    ("Shadow of the Ember Throne", "Liam Carter", "Fantasy", 599, 479, 4.5, 448,
     "An exiled prince and a rogue mapmaker race across a war-torn continent to stop an ancient "
     "power from awakening.",
     dict(is_new_arrival=True, is_audiobook=True)),
    ("The Founder's Dilemma", "Ritu Sen", "Business", 649, None, 4.3, 288,
     "Real decisions from real startups — a field guide to the hardest choices founders face.",
     dict(is_bestseller=True)),
    ("Negotiate Like You Mean It", "Tom Bradley", "Business", 399, 329, 4.2, 220,
     "A no-nonsense playbook for negotiating salary, deals, and everyday conflicts with confidence.",
     dict(is_new_arrival=True)),
    ("The Curriculum of Curiosity", "Dr. Anjali Rao", "Education", 349, None, 4.4, 198,
     "Rethinking how we teach children to ask better questions instead of memorising answers.",
     dict(is_featured=True)),
    ("Mathematics Without Fear", "Peter Nguyen", "Education", 429, 349, 4.6, 256,
     "An approachable guide that turns mathematical anxiety into genuine curiosity, for students "
     "and adults alike.",
     dict(is_bestseller=True)),
    ("Whispers of the Deep Forest", "Elena Marsh", "Fantasy", 459, None, 4.5, 320,
     "A lyrical audiobook adventure following a forest spirit guarding the last of the old magic.",
     dict(is_audiobook=True, is_new_arrival=True)),
    ("The Productivity Myth", "Grace Lin", "Non-fiction", 379, 299, 4.1, 214,
     "Why chasing productivity often backfires — and what actually helps people do meaningful work.",
     dict(is_audiobook=True)),
]

SECTIONS = [
    ("bestseller", "Best Sellers", "Reader favourites, chosen by thousands"),
    ("new_arrival", "New Arrivals", "Fresh off the press this month"),
    ("audiobook", "Audiobooks", "Listen to your next favourite story"),
    ("editor_pick", "Editor's Picks", "Hand-picked by our team"),
]


class Command(BaseCommand):
    help = "Seed the database with sample categories, books and featured sections."

    def handle(self, *args, **options):
        cat_map = {}
        for name, icon, desc in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"icon": icon, "description": desc}
            )
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f"✔ {len(CATEGORIES)} categories ready"))

        created_count = 0
        for title, author, cat_name, price, discount, rating, pages, desc, flags in BOOKS:
            book, created = Book.objects.get_or_create(
                title=title,
                author=author,
                defaults=dict(
                    category=cat_map[cat_name],
                    price=price,
                    discount_price=discount,
                    rating=rating,
                    pages=pages,
                    description=desc,
                    stock=30,
                    **flags,
                ),
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"✔ {created_count} books created"))

        for section_type, title, subtitle in SECTIONS:
            FeaturedSection.objects.get_or_create(
                section_type=section_type,
                defaults={"title": title, "subtitle": subtitle, "is_active": True},
            )
        self.stdout.write(self.style.SUCCESS("✔ Featured sections ready"))
        self.stdout.write(self.style.SUCCESS("\nSeed complete! Run the server and visit the homepage."))
