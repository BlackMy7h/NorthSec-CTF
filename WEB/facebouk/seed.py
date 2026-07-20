from __future__ import annotations

import random
from datetime import datetime, timedelta, date

from app import app, db
from app.models import User, Post, Comment, Friendship


def _dt_days_ago(days: int, *, base: datetime | None = None) -> datetime:
    base = base or datetime.utcnow()
    return base - timedelta(days=days, hours=random.randint(0, 23), minutes=random.randint(0, 59))


def seed_users() -> list[User]:
    # Admin user is inserted first — gets ID 1.
    users_data = [
        {
            "first_name": "Mark",
            "last_name": "Zuk",
            "email": "admin@facebouk.internal",
            "gender": "Unknown",
            "birthday": date(1980, 1, 1),
            "profile_pic_url": "https://i.pravatar.cc/200?img=1",
            "cover_quote": "Building the future of social networking.",
            "is_admin": True,
            "password": "Adm1nFac3b0uk!2010",
        },
        {
            "first_name": "Mark",
            "last_name": "Z.",
            "email": "mark@example.com",
            "gender": "Male",
            "birthday": date(1984, 5, 14),
            "profile_pic_url": "https://i.pravatar.cc/200?img=12",
            "cover_quote": "Move fast. Stay connected.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Dustin",
            "last_name": "M.",
            "email": "dustin@example.com",
            "gender": "Male",
            "birthday": date(1984, 5, 22),
            "profile_pic_url": "https://i.pravatar.cc/200?img=15",
            "cover_quote": "Shipping beats debating.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Eduardo",
            "last_name": "S.",
            "email": "eduardo@example.com",
            "gender": "Male",
            "birthday": date(1982, 3, 19),
            "profile_pic_url": "https://i.pravatar.cc/200?img=47",
            "cover_quote": "Coffee, code, and late nights.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Chris",
            "last_name": "H.",
            "email": "chris@example.com",
            "gender": "Male",
            "birthday": date(1983, 6, 27),
            "profile_pic_url": "https://i.pravatar.cc/200?img=32",
            "cover_quote": "Keep it simple.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Sarah",
            "last_name": "Jenkins",
            "email": "sarah@example.com",
            "gender": "Female",
            "birthday": date(1988, 9, 2),
            "profile_pic_url": "https://i.pravatar.cc/200?img=5",
            "cover_quote": "Weekend brunch mode: ON.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Alex",
            "last_name": "Nguyen",
            "email": "alex@example.com",
            "gender": "Male",
            "birthday": date(1990, 1, 9),
            "profile_pic_url": "https://i.pravatar.cc/200?img=18",
            "cover_quote": "New playlist every week.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Priya",
            "last_name": "Kumar",
            "email": "priya@example.com",
            "gender": "Female",
            "birthday": date(1989, 11, 20),
            "profile_pic_url": "https://i.pravatar.cc/200?img=45",
            "cover_quote": "Trying to take more photos.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Jason",
            "last_name": "Baker",
            "email": "jason@example.com",
            "gender": "Male",
            "birthday": date(1987, 4, 1),
            "profile_pic_url": "https://i.pravatar.cc/200?img=22",
            "cover_quote": "Road trips > everything.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Maya",
            "last_name": "Torres",
            "email": "maya@example.com",
            "gender": "Female",
            "birthday": date(1991, 7, 7),
            "profile_pic_url": "https://i.pravatar.cc/200?img=29",
            "cover_quote": "If it's sunny, I'm outside.",
            "is_admin": False,
            "password": "password",
        },
        {
            "first_name": "Ben",
            "last_name": "Carter",
            "email": "ben@example.com",
            "gender": "Male",
            "birthday": date(1986, 12, 12),
            "profile_pic_url": "https://i.pravatar.cc/200?img=67",
            "cover_quote": "Working on something cool.",
            "is_admin": False,
            "password": "password",
        },
    ]

    users: list[User] = []
    for u in users_data:
        user = User(
            first_name=u["first_name"],
            last_name=u["last_name"],
            email=u["email"],
            gender=u["gender"],
            birthday=u["birthday"],
            profile_pic_url=u["profile_pic_url"],
            cover_quote=u["cover_quote"],
            is_admin=u["is_admin"],
        )
        user.set_password(u["password"])
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return users


def seed_friendships(users: list[User]) -> None:
    ids = [u.id for u in users]
    accepted_pairs: set[tuple[int, int]] = set()
    pending_pairs: set[tuple[int, int]] = set()

    def add_pair(a: int, b: int, status: str) -> None:
        if a == b:
            return
        key = tuple(sorted((a, b)))  # type: ignore[assignment]
        if status == 'accepted':
            accepted_pairs.add(key)  # type: ignore[arg-type]
        else:
            pending_pairs.add(key)  # type: ignore[arg-type]

    for _ in range(18):
        a, b = random.sample(ids, 2)
        add_pair(a, b, 'accepted')
    for _ in range(6):
        a, b = random.sample(ids, 2)
        add_pair(a, b, 'pending')

    for a, b in sorted(accepted_pairs):
        db.session.add(Friendship(user_id_1=a, user_id_2=b, status='accepted'))
    for a, b in sorted(pending_pairs - accepted_pairs):
        db.session.add(Friendship(user_id_1=a, user_id_2=b, status='pending'))

    db.session.commit()


def seed_posts_comments(users: list[User]) -> None:
    sample_statuses = [
        "Just got back from a long walk. The weather is perfect.",
        "Anyone else remember when profiles had found a way to be simple and clean?",
        "Working late again. Coffee is a feature, not a bug.",
        "New headphones. Same old playlist.",
        "If you need me, I'll be reorganizing my photo albums.",
        "Trying out a new recipe tonight.",
        "Can't believe it's already Friday.",
        "Laptop battery is giving up. Time to find an outlet.",
        "Quick question: best movie of the year so far?",
        "Going offline for a bit — see you later!",
    ]

    sample_wall = [
        "Hey! Long time no see — how have you been?",
        "Happy birthday! Hope it's a good one.",
        "That photo from last weekend is amazing.",
        "Congrats on the new job!",
        "We should catch up soon.",
    ]

    posts: list[Post] = []
    now = datetime.utcnow()

    # Exclude admin user (index 0) from being a random post author
    regular_users = users[1:]

    for _ in range(26):
        author = random.choice(regular_users)
        if random.random() < 0.45:
            target = random.choice(regular_users)
            content = random.choice(sample_wall)
            if author.id == target.id:
                content = random.choice(sample_statuses)
                target = None
        else:
            target = None
            content = random.choice(sample_statuses)

        p = Post(
            author_id=author.id,
            target_user_id=(target.id if target else None),
            content=content,
            timestamp=_dt_days_ago(random.randint(0, 4), base=now),
            likes_count=random.randint(0, 12),
        )
        posts.append(p)

    # Add deterministic "photo" posts that reference local static images
    photo_filenames = [
        "670787490_17940808152188367_5759919604156780066_n.jpeg",
        "670848644_17940808092188367_4455578767293241986_n.jpeg",
        "670897693_17940808104188367_21804959405545027_n.jpeg",
        "670955404_17940808170188367_3371117144704931633_n.jpeg",
        "670959785_17940808143188367_6453427502577120675_n.jpeg",
        "671201789_17940808065188367_8419842473753200730_n.jpeg",
    ]

    photo_captions = [
        "Photo dump.",
        "Throwback.",
        "Found this in my camera roll.",
        "Classic.",
        "No filter.",
        "Mood.",
    ]

    # Use a couple different authors so they show up naturally in feeds.
    for i, fn in enumerate(photo_filenames):
        author = regular_users[i % len(regular_users)]
        posts.append(
            Post(
                author_id=author.id,
                target_user_id=None,
                content=photo_captions[i % len(photo_captions)],
                image_url=f"/static/images/{fn}",
                timestamp=_dt_days_ago(random.randint(0, 2), base=now),
                likes_count=random.randint(1, 25),
            )
        )

    db.session.add_all(posts)
    db.session.commit()

    comment_lines = [
        "lol", "So true.", "Nice!", "Send pics.", "I'm in.",
        "Congrats!!", "Miss those days.", "Call me later.", "What time?", "Agreed.",
    ]

    comments: list[Comment] = []
    for p in posts:
        if random.random() < 0.65:
            for _ in range(random.randint(1, 4)):
                author = random.choice(regular_users)
                c = Comment(
                    post_id=p.id,
                    author_id=author.id,
                    content=random.choice(comment_lines),
                    timestamp=p.timestamp + timedelta(minutes=random.randint(2, 240)),
                )
                comments.append(c)

    db.session.add_all(comments)
    db.session.commit()


def seed_all() -> None:
    with app.app_context():
        # Don't wipe the DB on each container start.
        # Create missing tables/columns via SQLAlchemy metadata (simple schema init for this challenge).
        db.create_all()

        # If we've already seeded (at least one user exists), do nothing.
        if User.query.first() is not None:
            print("[seed] Existing data detected; skipping reseed.")
            return

        users = seed_users()
        seed_friendships(users)
        seed_posts_comments(users)
        print(f"[seed] Admin user ID: {users[0].id} ({users[0].email})")
        print(f"[seed] Seeded {len(users)} users, ready.")


if __name__ == '__main__':
    seed_all()
