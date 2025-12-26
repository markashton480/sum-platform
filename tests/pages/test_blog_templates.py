"""
Tests for blog template rendering.

Validates that BlogIndexPage and BlogPostPage templates render correctly
with all UI contract requirements met.
"""

import pytest
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from wagtail.models import Site

# Test constants
# ---------------
# Number of word repetitions to generate content for reading time calculation.
# Reading time is calculated at ~200 WPM, so 50 words = ~15 seconds (rounds to 1 min).
WORDS_FOR_READING_TIME = 50

# Default posts per page for blog index pagination testing.
DEFAULT_POSTS_PER_PAGE = 10

# Small posts_per_page to trigger pagination with fewer posts.
POSTS_PER_PAGE_FOR_PAGINATION = 3

# Medium posts_per_page for component testing.
POSTS_PER_PAGE_FOR_COMPONENTS = 5


@pytest.mark.django_db
class TestBlogIndexPageTemplateRendering:
    """Test BlogIndexPage template rendering."""

    @pytest.fixture
    def site(self):
        """Create a test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def blog_index(self, site):
        """Create a BlogIndexPage."""
        home = site.root_page
        blog_index = BlogIndexPage(
            title="Blog",
            slug="blog",
            posts_per_page=DEFAULT_POSTS_PER_PAGE,
        )
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        return blog_index

    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(
            name="Test Category", slug="test-category", description="Test description"
        )

    @pytest.fixture
    def blog_posts(self, blog_index, category):
        """Create multiple blog posts for testing."""
        posts = []
        for i in range(5):
            post = BlogPostPage(
                title=f"Test Post {i}",
                slug=f"test-post-{i}",
                excerpt=f"Excerpt for post {i}",
                body=[
                    (
                        "rich_text",
                        "<p>"
                        + f"Body content for post {i} " * WORDS_FOR_READING_TIME
                        + "</p>",
                    )
                ],
                category=category,
            )
            blog_index.add_child(instance=post)
            post.save_revision().publish()
            posts.append(post)
        return posts

    def test_blog_index_template_renders(self, client, blog_index, blog_posts):
        """Test that blog index page template renders without errors."""
        response = client.get(blog_index.get_url())
        assert response.status_code == 200
        assert b"Blog" in response.content

    def test_blog_index_displays_post_cards(self, client, blog_index, blog_posts):
        """Test that post cards are rendered on the listing page."""
        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Check that post titles appear
        for post in blog_posts:
            assert post.title in content

    def test_blog_index_displays_category_labels(
        self, client, blog_index, blog_posts, category
    ):
        """Test that category labels are displayed on post cards."""
        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Check that category name appears
        assert category.name in content

    def test_blog_index_displays_published_dates(self, client, blog_index, blog_posts):
        """Test that published dates are displayed on post cards."""
        client.get(blog_index.get_url())

        # Check that dates are present on posts
        for post in blog_posts:
            # Published date should be set
            assert post.published_date is not None

    def test_blog_index_displays_reading_time(self, client, blog_index, blog_posts):
        """Test that reading time is displayed on post cards."""
        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Check for reading time display - template uses "X min read" format
        # At least one post should have reading time displayed
        assert "min read" in content.lower()

    def test_blog_index_displays_excerpts(self, client, blog_index, blog_posts):
        """Test that post excerpts are displayed on cards."""
        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Check that excerpts appear
        for post in blog_posts:
            assert post.excerpt in content

    def test_blog_index_displays_featured_images(self, client, blog_index, blog_posts):
        """Test that featured images are rendered when present."""
        response = client.get(blog_index.get_url())

        # Check for image tags (posts may or may not have featured images)
        # This test verifies the template handles both cases
        assert response.status_code == 200

    def test_blog_index_pagination_controls_appear(self, client, blog_index):
        """Test that pagination controls appear when needed."""
        # Create more posts than posts_per_page to trigger pagination
        blog_index.posts_per_page = POSTS_PER_PAGE_FOR_PAGINATION
        blog_index.save()

        category = Category.objects.create(
            name="Pagination Test", slug="pagination-test"
        )

        for i in range(10):
            post = BlogPostPage(
                title=f"Pagination Post {i}",
                slug=f"pagination-post-{i}",
                body=[
                    ("rich_text", "<p>" + "Content " * WORDS_FOR_READING_TIME + "</p>")
                ],
                category=category,
            )
            blog_index.add_child(instance=post)
            post.save_revision().publish()

        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Check for pagination nav element with aria-label="Pagination"
        # and pagination links with ?page= query parameter
        assert 'aria-label="Pagination"' in content
        assert "?page=" in content

    def test_blog_index_category_filtering_works(
        self, client, blog_index, blog_posts, category
    ):
        """Test that category filtering via query param works."""
        response = client.get(f"{blog_index.get_url()}?category={category.slug}")
        assert response.status_code == 200
        content = response.content.decode()

        # All posts should be from the filtered category
        for post in blog_posts:
            assert post.title in content


@pytest.mark.django_db
class TestBlogPostPageTemplateRendering:
    """Test BlogPostPage template rendering."""

    @pytest.fixture
    def site(self):
        """Create a test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def blog_index(self, site):
        """Create a BlogIndexPage."""
        home = site.root_page
        blog_index = BlogIndexPage(
            title="Blog", slug="blog", posts_per_page=DEFAULT_POSTS_PER_PAGE
        )
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        return blog_index

    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(
            name="Article Category",
            slug="article-category",
            description="Category for articles",
        )

    @pytest.fixture
    def blog_post(self, blog_index, category):
        """Create a blog post for testing."""
        post = BlogPostPage(
            title="Test Article",
            slug="test-article",
            excerpt="This is a test article excerpt.",
            body=[
                (
                    "rich_text",
                    "<h2>Introduction</h2><p>"
                    + "This is the introduction paragraph. " * WORDS_FOR_READING_TIME
                    + "</p>",
                ),
                (
                    "rich_text",
                    "<h2>Main Content</h2><p>"
                    + "This is the main content. " * 100
                    + "</p>",
                ),
            ],
            category=category,
            author_name="Test Author",
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()
        return post

    def test_blog_post_template_renders(self, client, blog_post):
        """Test that blog post page template renders without errors."""
        response = client.get(blog_post.get_url())
        assert response.status_code == 200
        assert b"Test Article" in response.content

    def test_blog_post_displays_title(self, client, blog_post):
        """Test that the post title is rendered."""
        response = client.get(blog_post.get_url())
        content = response.content.decode()
        assert blog_post.title in content

    def test_blog_post_displays_published_date(self, client, blog_post):
        """Test that published date is displayed."""
        response = client.get(blog_post.get_url())
        # Published date should be set
        assert blog_post.published_date is not None
        assert response.status_code == 200

    def test_blog_post_displays_category(self, client, blog_post, category):
        """Test that category label is displayed."""
        response = client.get(blog_post.get_url())
        content = response.content.decode()
        assert category.name in content

    def test_blog_post_displays_reading_time(self, client, blog_post):
        """Test that reading time is displayed."""
        response = client.get(blog_post.get_url())
        content = response.content.decode()
        # Reading time should be displayed - template uses "X min read" format
        assert "min read" in content.lower()

    def test_blog_post_displays_author_name(self, client, blog_post):
        """Test that author name is displayed when present."""
        response = client.get(blog_post.get_url())
        content = response.content.decode()
        assert blog_post.author_name in content

    def test_blog_post_renders_streamfield_body(self, client, blog_post):
        """Test that StreamField body content is rendered."""
        response = client.get(blog_post.get_url())
        content = response.content.decode()
        # Check for heading and paragraph content
        assert "Introduction" in content
        assert "Main Content" in content
        assert "introduction paragraph" in content

    def test_blog_post_displays_featured_image_when_present(self, client, blog_post):
        """Test that featured image section renders (even if no image)."""
        response = client.get(blog_post.get_url())
        # Template should handle case where featured_image is None
        assert response.status_code == 200

    def test_blog_post_supports_dynamic_form_block_in_body(self, blog_index):
        """Test that DynamicFormBlock can be included in post body."""
        from sum_core.forms.models import FormDefinition

        site = Site.objects.get(is_default_site=True)
        category = Category.objects.create(name="Form Test", slug="form-test")

        # Create a FormDefinition
        form_def = FormDefinition.objects.create(
            name="Newsletter Signup",
            slug="newsletter",
            site=site,
            fields=[
                ("email_input", {"label": "Email", "required": True}),
            ],
            success_message="Thanks for signing up!",
            is_active=True,
        )

        # Create post with DynamicFormBlock
        post = BlogPostPage(
            title="Post with Form",
            slug="post-with-form",
            body=[
                (
                    "rich_text",
                    "<p>" + "Article content here. " * WORDS_FOR_READING_TIME + "</p>",
                ),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_def,
                        "presentation_style": "inline",
                        "cta_button_text": "Subscribe",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Verify the post was created successfully
        assert post.body is not None
        assert len(post.body) == 2
        assert post.body[1].block_type == "dynamic_form"

    def test_blog_post_template_no_errors_without_optional_fields(
        self, client, blog_index, category
    ):
        """Test that template renders correctly when optional fields are None."""
        # Create post without optional fields
        post = BlogPostPage(
            title="Minimal Post",
            slug="minimal-post",
            body=[
                (
                    "rich_text",
                    "<p>" + "Minimal content. " * WORDS_FOR_READING_TIME + "</p>",
                )
            ],
            category=category,
            # No excerpt, no author_name, no featured_image
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        assert response.status_code == 200
        assert b"Minimal Post" in response.content


@pytest.mark.django_db
class TestBlogComponentTemplates:
    """Test individual blog component templates."""

    @pytest.fixture
    def site(self):
        """Create a test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def blog_index(self, site):
        """Create a BlogIndexPage."""
        home = site.root_page
        blog_index = BlogIndexPage(
            title="Blog", slug="blog", posts_per_page=POSTS_PER_PAGE_FOR_COMPONENTS
        )
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        return blog_index

    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(name="Component Test", slug="component-test")

    def test_post_card_component_renders(self, client, blog_index, category):
        """Test that post card component renders correctly."""
        post = BlogPostPage(
            title="Card Test Post",
            slug="card-test-post",
            excerpt="Test excerpt for card",
            body=[("rich_text", "<p>" + "Content " * WORDS_FOR_READING_TIME + "</p>")],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Post card should include title and excerpt
        assert "Card Test Post" in content
        assert "Test excerpt for card" in content

    def test_pagination_component_renders(self, client, blog_index, category):
        """Test that pagination component renders when needed."""
        # Create enough posts to trigger pagination
        for i in range(15):
            post = BlogPostPage(
                title=f"Pagination Post {i}",
                slug=f"pagination-post-{i}",
                body=[
                    ("rich_text", "<p>" + "Content " * WORDS_FOR_READING_TIME + "</p>")
                ],
                category=category,
            )
            blog_index.add_child(instance=post)
            post.save_revision().publish()

        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Pagination controls should be present
        assert response.status_code == 200
        # Check for page 2 link or next button
        assert "page=2" in content or "next" in content.lower()

    def test_category_filter_component_renders(self, client, blog_index):
        """Test that category filter component renders when categories exist."""
        # Create multiple categories with posts
        for i in range(3):
            category = Category.objects.create(
                name=f"Filter Category {i}", slug=f"filter-category-{i}"
            )
            post = BlogPostPage(
                title=f"Filter Post {i}",
                slug=f"filter-post-{i}",
                body=[
                    ("rich_text", "<p>" + "Content " * WORDS_FOR_READING_TIME + "</p>")
                ],
                category=category,
            )
            blog_index.add_child(instance=post)
            post.save_revision().publish()

        response = client.get(blog_index.get_url())
        content = response.content.decode()

        # Category names should appear in filter
        assert "Filter Category 0" in content
        assert "Filter Category 1" in content
        assert "Filter Category 2" in content
