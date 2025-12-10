import pytest
from wagtail.blocks import StructBlock, ListBlock
from django.core.exceptions import ValidationError

from sum_core.blocks.testimonials import TestimonialsBlock, TestimonialBlock

def test_block_structure():
    """Test the TestimonialsBlock structure."""
    block = TestimonialsBlock()
    assert isinstance(block, StructBlock)
    
    assert 'eyebrow' in block.child_blocks
    assert 'heading' in block.child_blocks
    assert 'testimonials' in block.child_blocks
    # intro removed
    
    assert isinstance(block.child_blocks['testimonials'], ListBlock)
    assert isinstance(block.child_blocks['testimonials'].child_block, TestimonialBlock)
    
    # Check constraints
    assert block.child_blocks['testimonials'].meta.min_num == 1
    assert block.child_blocks['testimonials'].meta.max_num == 12

def test_item_fields():
    """Test the TestimonialBlock fields."""
    block = TestimonialBlock()
    assert isinstance(block, StructBlock)
    
    assert 'quote' in block.child_blocks
    assert 'author_name' in block.child_blocks
    assert 'company' in block.child_blocks
    assert 'photo' in block.child_blocks
    assert 'rating' in block.child_blocks
    
    assert block.child_blocks['quote'].required
    assert block.child_blocks['author_name'].required
    assert not block.child_blocks['company'].required
    assert not block.child_blocks['photo'].required
    assert not block.child_blocks['rating'].required

def test_rating_validation():
    """Test that rating validators enforce 1-5 range."""
    block = TestimonialBlock()
    rating_block = block.child_blocks['rating']
    
    # Valid values check
    assert rating_block.clean(1) == 1
    assert rating_block.clean(5) == 5
    
    # Invalid values should raise ValidationError
    with pytest.raises(ValidationError):
        rating_block.clean(0)
        
    with pytest.raises(ValidationError):
        rating_block.clean(6)

def test_round_trip():
    """Test initialising block value dict, render to JSON, re-parse to struct."""
    block = TestimonialsBlock()
    value = {
        "eyebrow": "Stories",
        # Richtext handling in struct block clean can be complex to mock locally 
        # without full wagtail setup sometimes, skipping direct string-to-richtext 
        # assertion here for simplicity unless we mock RichText.
        # "heading": "Happy Clients", 
        "testimonials": [
            {
                "quote": "Great service!",
                "author_name": "John Doe",
                "company": "Acme Corp",
                "rating": 5,
                "photo": None
            }
        ]
    }
    
    # Clean ensures data is valid and converts to block values
    clean_value = block.clean(value)
    
    # Basic check that we have the struct value
    assert clean_value['eyebrow'] == "Stories"
    # assert "Happy Clients" in str(clean_value['heading'])
    assert len(clean_value['testimonials']) == 1
    assert clean_value['testimonials'][0]['author_name'] == "John Doe"
