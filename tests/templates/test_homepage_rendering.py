import pytest
from django.test import Client
from wagtail.models import Site
from home.models import HomePage

pytestmark = pytest.mark.django_db

def test_homepage_renders_testimonials_block():
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    
    # Create homepage
    home = HomePage(title="Home Test", slug="home-test-testimonials")
    root.add_child(instance=home)
    home.save()
    
    # Assign testimonials block data
    home.body = [
        ('testimonials', {
            'eyebrow': 'Testimonials',
            'heading': '<p>Client Vibes</p>', 
            'testimonials': [
                {
                    'quote': 'Amazing work!',
                    'author_name': 'Alice Smith',
                    'rating': 5
                },
                {
                    'quote': 'Pretty good.',
                    'author_name': 'Bob Jones',
                    'rating': 4
                }
            ]
        })
    ]
    home.save()
    
    # Function based rendering check via client
    client = Client()
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()
    
    # Check layout classes
    assert 'class="section section--dark testimonials"' in content
    assert 'testimonials__grid' in content
    assert 'testimonial-card' in content
    
    # Check content
    assert 'Testimonials' in content
    assert 'Client Vibes' in content
    assert 'Amazing work!' in content
    assert 'Alice Smith' in content
    
    # Check ratings render
    # There are 2 testimonials, each has 5 star spans. Total 10 star spans.
    assert content.count('aria-hidden="true">★</span>') + content.count('aria-hidden="true">☆</span>') == 10
    
    # First one is 5 stars (5 filled)
    # Second one is 4 stars (4 filled)
    # Total filled stars = 9
    assert content.count('aria-hidden="true">★</span>') == 9
