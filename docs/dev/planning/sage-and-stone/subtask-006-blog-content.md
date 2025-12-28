# Subtask 006: Blog Content

## Overview

Create BlogIndexPage, Category snippets, and 7 BlogPostPage entries with full article content.

## Deliverables

1. BlogIndexPage configured
2. 3 Category snippets
3. 7 BlogPostPage entries with full content
4. Featured images and body content

## Content Plan

### Categories

| Name | Slug | Description |
|------|------|-------------|
| Commission Stories | commission-stories | Behind the scenes of our kitchen commissions |
| Material Science | material-science | Deep dives into timber, joinery, and craft |
| The Workshop | the-workshop | News and updates from Herefordshire |

### Blog Posts

| # | Title | Category | Date | Featured Image |
|---|-------|----------|------|----------------|
| 1 | The Art of Seasoning Timber | Material Science | 2025-11-15 | BLOG_TIMBER_IMAGE |
| 2 | Inside the Kensington Commission | Commission Stories | 2025-10-28 | BLOG_KENSINGTON |
| 3 | Hand-Cut vs Machine Dovetails | Material Science | 2025-10-15 | BLOG_DOVETAILS |
| 4 | Workshop Update: New Finishing Room | The Workshop | 2025-09-30 | BLOG_WORKSHOP |
| 5 | The Georgian Restoration: A 12-Month Journey | Commission Stories | 2025-09-15 | BLOG_GEORGIAN |
| 6 | Why We Don't Use MDF | Material Science | 2025-08-20 | BLOG_MDF |
| 7 | Meet Marcus: Our New Project Director | The Workshop | 2025-08-01 | BLOG_MARCUS |

## Implementation

### 1. Create Categories

```python
from sum_core.pages.blog import Category

CATEGORIES = [
    {
        "name": "Commission Stories",
        "slug": "commission-stories",
        "description": "Behind the scenes of our kitchen commissions"
    },
    {
        "name": "Material Science",
        "slug": "material-science",
        "description": "Deep dives into timber, joinery, and craft"
    },
    {
        "name": "The Workshop",
        "slug": "the-workshop",
        "description": "News and updates from Herefordshire"
    },
]

def create_categories(self):
    """Create blog categories."""

    categories = {}
    for cat_data in CATEGORIES:
        category, _ = Category.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "description": cat_data["description"],
            }
        )
        categories[cat_data["slug"]] = category
        self.stdout.write(f"  Category: {category.name}")

    return categories
```

### 2. Create Blog Index

```python
from sum_core.pages.blog import BlogIndexPage

def create_blog_index(self, home_page):
    """Create the blog index page."""

    try:
        page = BlogIndexPage.objects.get(slug="journal")
        return page
    except BlogIndexPage.DoesNotExist:
        pass

    page = BlogIndexPage(
        title="The Ledger",
        slug="journal",
        seo_title="The Ledger | Notes from the Workshop | Sage & Stone",
        search_description="Stories of timber, craft, and the kitchens we build. Insights from 28 years of bespoke joinery.",
        show_in_menus=True,
        intro="Notes from the workshop. Stories of timber, craft, and the kitchens we build.",
        posts_per_page=9,
    )

    home_page.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write("  Created Blog Index: The Ledger")
    return page
```

### 3. Create Blog Posts

```python
from sum_core.pages.blog import BlogPostPage
from datetime import datetime

BLOG_POSTS = [
    {
        "title": "The Art of Seasoning Timber",
        "slug": "art-of-seasoning-timber",
        "category_slug": "material-science",
        "published_date": "2025-11-15",
        "image_key": "BLOG_TIMBER_IMAGE",
        "excerpt": "Why we wait years before a single plank touches our workshop. The ancient practice that separates heirloom furniture from firewood.",
        "author_name": "Thomas J. Wright",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">There's a reason antique furniture survives centuries while modern pieces warp within years. The secret isn't in the joinery or the finish—it's in the waiting.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>When a tree is felled, its wood contains up to 80% moisture. Use it immediately, and you're building with a ticking time bomb. As that moisture escapes over months and years, the wood shrinks, twists, and cracks. Every joint loosens. Every surface cups.</p><p>This is why we season every piece of timber that enters our workshop. It's also why we turn away clients who can't wait.</p>"
                }
            },
            {
                "type": "editorial_header",
                "value": {
                    "align": "left",
                    "eyebrow": "",
                    "heading": "Understanding Moisture Content"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>Freshly cut timber has a moisture content (MC) of 60-80%. For furniture making, we need to bring this down to 8-12%—equilibrium with a typical heated home. Get this wrong, and disaster follows.</p><blockquote>Wood remembers. Every stress, every rush, every shortcut—it will express them eventually.</blockquote><p>Traditional air drying takes approximately one year per inch of thickness. A 2-inch oak board needs two full years before it's ready. Modern kiln drying can accelerate this, but at a cost to the wood's character and stability.</p>"
                }
            },
            {
                "type": "image_block",
                "value": {
                    "image": None,  # Will be populated with BLOG_TIMBER_STACK
                    "alt_text": "Oak boards stacked for air drying",
                    "caption": "Our timber stacks: each board separated by spacers for airflow",
                    "full_width": True
                }
            },
            {
                "type": "editorial_header",
                "value": {
                    "align": "left",
                    "eyebrow": "",
                    "heading": "The Waiting Game"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>At Sage & Stone, we maintain our own timber stocks. When you commission a kitchen, the oak for your cabinetry has likely been seasoning in our yard for three years or more.</p><p>This isn't inefficiency—it's insurance. We're building furniture your grandchildren will use. A few years of patience now prevents decades of problems later.</p><p>We've had clients ask us to rush. We've had competitors promise faster delivery. Both paths lead to the same destination: furniture that fails.</p>"
                }
            },
            {
                "type": "quote",
                "value": {
                    "quote": "Speed is the enemy of legacy.",
                    "author": "Thomas J. Wright",
                    "role": "Founder"
                }
            },
            {
                "type": "editorial_header",
                "value": {
                    "align": "left",
                    "eyebrow": "",
                    "heading": "Our Approach"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>Every board in our workshop has a story. We know where it grew, when it was felled, and how long it's been drying. This provenance isn't just record-keeping—it's quality control.</p><p>When you receive your Sage & Stone kitchen, you're receiving timber that's been cared for as carefully as the finished joinery. The waiting is part of the craft.</p><p>If you're ready to begin your commission—and to embrace the pace that quality demands—<a href=\"/contact/\">we'd love to hear from you</a>.</p>"
                }
            },
        ]
    },
    {
        "title": "Inside the Kensington Commission",
        "slug": "inside-kensington-commission",
        "category_slug": "commission-stories",
        "published_date": "2025-10-28",
        "image_key": "BLOG_KENSINGTON",
        "excerpt": "A behind-the-scenes look at our most ambitious London project. From first survey to final handover.",
        "author_name": "Marcus T.",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">The Kensington Commission began with a phone call and ended with a standing ovation from the installation team. Here's what happened in between.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>When the clients first contacted us, they'd already spoken to three other kitchen companies. Each had promised quick turnarounds and competitive pricing. None had asked about their grandparents' kitchen table.</p><p>We did. Because that's where the real brief lives.</p><p>It turned out their favourite piece of furniture was a simple oak table, handed down through three generations. They wanted their new kitchen to feel like that—permanent, loved, and utterly without pretension.</p>"
                }
            },
            {
                "type": "editorial_header",
                "value": {
                    "align": "left",
                    "eyebrow": "",
                    "heading": "The Design Phase"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>We spent four weeks on design alone. Not because we're slow, but because we're thorough. Every drawer, every handle, every sight line was considered and reconsidered.</p><p>The clients visited our workshop twice during this phase. We believe you should see where your kitchen is born—the sawdust, the offcuts, the half-finished pieces that will eventually become yours.</p>"
                }
            },
            {
                "type": "quote",
                "value": {
                    "quote": "They didn't just show us drawings. They showed us the wood that would become our kitchen. That's when we knew we'd chosen right.",
                    "author": "The Clients",
                    "role": "Kensington"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The installation took eleven days. Our team of four worked in near-silence, communicating in the shorthand that comes from years of collaboration. The clients barely knew we were there—which is exactly how we like it.</p><p>When we handed over the keys, the kitchen had already been cleaned three times. We don't leave fingerprints, literal or metaphorical.</p>"
                }
            },
        ]
    },
    {
        "title": "Hand-Cut vs Machine Dovetails",
        "slug": "hand-cut-vs-machine-dovetails",
        "category_slug": "material-science",
        "published_date": "2025-10-15",
        "image_key": "BLOG_DOVETAILS",
        "excerpt": "The joints that define quality craftsmanship. Why we cut every dovetail by hand, and why it matters.",
        "author_name": "David R.",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">You can spot a hand-cut dovetail from across the room. The subtle irregularities. The confident asymmetry. The unmistakable mark of a human hand.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>Machine-cut dovetails are perfect. That's the problem.</p><p>When every joint is identical, when every angle is exactly 1:8, something essential is lost. The furniture becomes a product, not a piece. It could have been made anywhere, by anyone, at any time.</p><p>Hand-cut dovetails are different. Each one carries the signature of its maker—the angle they prefer, the saw marks they leave, the tiny variations that accumulate into character.</p>"
                }
            },
            {
                "type": "editorial_header",
                "value": {
                    "align": "left",
                    "eyebrow": "",
                    "heading": "The Technical Argument"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>Beyond aesthetics, hand-cut dovetails offer practical advantages:</p><ul><li><strong>Custom fit:</strong> Each joint is cut to match the specific piece of wood, accounting for grain direction and density variations.</li><li><strong>Tighter tolerances:</strong> A skilled craftsman can achieve fits that machines cannot, because they can feel when the joint is right.</li><li><strong>Repair potential:</strong> Hand-cut joints can be disassembled and repaired. Machine-cut joints often cannot.</li></ul>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>At Sage & Stone, every drawer box, every carcass joint, every corner is hand-cut. It takes longer. It costs more. But sixty years from now, when your grandchildren are cooking in your kitchen, the dovetails will still be tight.</p><p>That's the only metric that matters.</p>"
                }
            },
        ]
    },
    {
        "title": "Workshop Update: New Finishing Room",
        "slug": "workshop-update-finishing-room",
        "category_slug": "the-workshop",
        "published_date": "2025-09-30",
        "image_key": "BLOG_WORKSHOP",
        "excerpt": "A major upgrade to our Herefordshire facility. Controlled environment finishing for even better results.",
        "author_name": "Thomas J. Wright",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">After eighteen months of planning and three months of construction, our new finishing room is complete. Here's why it matters.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>Finishing is where good furniture becomes great furniture. The final coats of oil or lacquer seal in all the work that came before—and any dust, debris, or moisture that happens to land during application.</p><p>Our new room eliminates those risks. Temperature-controlled to within 2°C, humidity-regulated, and positively pressured to keep dust out. It's overkill for most workshops. For us, it's essential.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The investment was significant. But when you're building furniture to last generations, the finish needs to match. Our clients deserve nothing less.</p><p>If you'd like to see the new facility, <a href=\"/contact/\">book a workshop visit</a>. We're proud to show it off.</p>"
                }
            },
        ]
    },
    {
        "title": "The Georgian Restoration: A 12-Month Journey",
        "slug": "georgian-restoration-journey",
        "category_slug": "commission-stories",
        "published_date": "2025-09-15",
        "image_key": "BLOG_GEORGIAN",
        "excerpt": "Restoring a 1780s kitchen required patience, research, and a willingness to learn from the past.",
        "author_name": "Sarah M.",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">When we first saw the Georgian townhouse kitchen, we knew this would be different. The original cabinetry—what remained of it—dated to 1783.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The brief was clear: restore what could be saved, replace what couldn't, and make the joins invisible. No one looking at the finished kitchen should be able to tell where the 18th century ends and the 21st begins.</p><p>This required research. We spent weeks studying Georgian joinery techniques, visiting museum collections, and consulting with conservation specialists. The dovetails of 1783 are subtly different from those we cut today. The moulding profiles have changed. Even the way the wood was prepared—its texture, its finish—carries period signatures.</p>"
                }
            },
            {
                "type": "quote",
                "value": {
                    "quote": "We weren't just matching the old work. We were learning from craftsmen who died two centuries ago.",
                    "author": "Sarah M.",
                    "role": "Finishing Specialist"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The project took twelve months from first survey to final handover. Expensive by any measure. But the kitchen is now better than it was in 1783—more functional, better preserved, and ready for another two centuries of service.</p><p>That's the kind of work we live for.</p>"
                }
            },
        ]
    },
    {
        "title": "Why We Don't Use MDF",
        "slug": "why-we-dont-use-mdf",
        "category_slug": "material-science",
        "published_date": "2025-08-20",
        "image_key": "BLOG_MDF",
        "excerpt": "The material that dominates modern kitchens has no place in ours. Here's why solid timber wins.",
        "author_name": "Thomas J. Wright",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">MDF—medium-density fibreboard—is everywhere. It's cheap, stable, and easy to work with. It's also the reason most modern kitchens are destined for landfill within twenty years.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The problems with MDF are fundamental:</p><ul><li><strong>Water damage is catastrophic:</strong> Once MDF gets wet, it swells and never recovers. Solid timber can be dried and refinished.</li><li><strong>It cannot be repaired:</strong> Damaged MDF must be replaced. Damaged timber can be patched, filled, or refinished.</li><li><strong>It has no character:</strong> MDF is manufactured uniformity. Timber has grain, colour variation, and warmth.</li><li><strong>It off-gasses:</strong> MDF contains formaldehyde resins that continue releasing chemicals for years.</li></ul>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>We understand why manufacturers use MDF. It's predictable and profitable. But we're not building for the next fiscal quarter—we're building for the next century.</p><p>Every Sage & Stone kitchen is solid timber throughout. Carcasses, doors, drawers, shelves—not a scrap of MDF anywhere. It costs more. It takes longer. But it lasts forever.</p><p>That's a trade we'll make every time.</p>"
                }
            },
        ]
    },
    {
        "title": "Meet Marcus: Our New Project Director",
        "slug": "meet-marcus-project-director",
        "category_slug": "the-workshop",
        "published_date": "2025-08-01",
        "image_key": "BLOG_MARCUS",
        "excerpt": "After five years as Senior Installer, Marcus takes on a new role. Here's what that means for our clients.",
        "author_name": "Thomas J. Wright",
        "body": [
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p class=\"lead\">Marcus joined Sage & Stone five years ago. Last month, he became our Project Director. For our clients, this is very good news.</p>"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>The Project Director role is new for us. Previously, I handled all client communications personally. As our order book has grown, this became unsustainable. Clients deserve more attention than I could give them.</p><p>Marcus was the obvious choice. He knows our processes inside out—literally, having installed more Sage & Stone kitchens than anyone else. He understands what we promise and how we deliver.</p>"
                }
            },
            {
                "type": "quote",
                "value": {
                    "quote": "I've seen what happens when installation goes wrong. My job is making sure it never does.",
                    "author": "Marcus T.",
                    "role": "Project Director"
                }
            },
            {
                "type": "rich_text",
                "value": {
                    "align": "left",
                    "body": "<p>If you're a current client, Marcus is now your primary contact for project updates and scheduling. If you're considering a commission, he'll be the one guiding you through the process.</p><p>He's very good. You're in safe hands.</p>"
                }
            },
        ]
    },
]


def create_blog_content(self, home_page, categories):
    """Create blog index and all posts."""

    # Create blog index
    blog_index = self.create_blog_index(home_page)

    # Create each post
    for post_data in BLOG_POSTS:
        self._create_blog_post(blog_index, post_data, categories)

    return blog_index


def _create_blog_post(self, blog_index, post_data, categories):
    """Create a single blog post."""

    try:
        page = BlogPostPage.objects.get(slug=post_data["slug"])
        return page
    except BlogPostPage.DoesNotExist:
        pass

    # Get category
    category = categories[post_data["category_slug"]]

    # Process body to add image references
    body = post_data["body"].copy()
    for block in body:
        if block["type"] == "image_block" and block["value"]["image"] is None:
            # Default to main blog image
            image_key = post_data.get("image_key", "BLOG_TIMBER_IMAGE")
            if "STACK" in block["value"].get("alt_text", "").upper():
                image_key = "BLOG_TIMBER_STACK"
            if image_key in self.images:
                block["value"]["image"] = self.images[image_key].pk

    page = BlogPostPage(
        title=post_data["title"],
        slug=post_data["slug"],
        category=category,
        published_date=datetime.strptime(post_data["published_date"], "%Y-%m-%d"),
        featured_image=self.images.get(post_data["image_key"]),
        excerpt=post_data["excerpt"],
        author_name=post_data["author_name"],
        seo_title=f"{post_data['title']} | The Ledger | Sage & Stone",
        search_description=post_data["excerpt"][:160],
        body=body,
    )

    blog_index.add_child(instance=page)
    page.save_revision().publish()
    self.stdout.write(f"  Blog post: {page.title}")
    return page
```

## Acceptance Criteria

- [ ] BlogIndexPage created with correct settings
- [ ] 3 Category snippets created
- [ ] 7 BlogPostPage entries created
- [ ] All posts have featured images
- [ ] All posts have body content
- [ ] Posts ordered by published_date
- [ ] Posts correctly assigned to categories
- [ ] Excerpts populated
- [ ] Reading time calculated
- [ ] Idempotent: no duplicate posts

## Dependencies

- Subtask 001 (Site exists)
- Subtask 002 (Images generated)
- Subtask 005 (Home page exists as parent)

## Testing

```python
def test_categories_created():
    call_command("seed_sage_stone")

    assert Category.objects.count() == 3
    assert Category.objects.filter(slug="material-science").exists()

def test_blog_index_created():
    call_command("seed_sage_stone")

    index = BlogIndexPage.objects.get(slug="journal")
    assert index.title == "The Ledger"
    assert index.posts_per_page == 9

def test_blog_posts_created():
    call_command("seed_sage_stone")

    posts = BlogPostPage.objects.all()
    assert posts.count() == 7

def test_posts_have_categories():
    call_command("seed_sage_stone")

    post = BlogPostPage.objects.get(slug="art-of-seasoning-timber")
    assert post.category.slug == "material-science"

def test_posts_ordered_by_date():
    call_command("seed_sage_stone")

    posts = list(BlogPostPage.objects.live().order_by("-published_date"))
    assert posts[0].slug == "art-of-seasoning-timber"  # Most recent
```

## Notes

- Blog posts use realistic copy style matching brand voice
- Articles vary in length (some short, some long)
- Author names match team member names
- Published dates spread across several months for realistic feel
- Reading time auto-calculated by BlogPostPage model
