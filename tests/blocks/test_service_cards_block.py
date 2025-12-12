from django.test import TestCase
from wagtail.blocks import StructBlock, ListBlock
from wagtail.images.tests.utils import get_test_image_file
from wagtail.images.models import Image

from sum_core.blocks.services import ServiceCardsBlock, ServiceCardItemBlock

class ServiceCardsBlockTest(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test Image",
            file=get_test_image_file(),
        )

    def test_block_count_validation(self):
        """Test that the block enforces min and max card counts."""
        block = ServiceCardsBlock()

        # Test 0 cards (should fail min_num=1)
        with self.assertRaises(Exception):
            block.clean({"heading": "Test", "cards": []})

        # Verify the ListBlock constraints directly on the class definition
        # (constructing full valid data for 13 cards is complex due to StructBlock validation)
        self.assertEqual(block.child_blocks['cards'].meta.min_num, 1)
        self.assertEqual(block.child_blocks['cards'].meta.max_num, 12)

    def test_item_fields(self):
        """Test the ServiceCardItemBlock fields."""
        block = ServiceCardItemBlock()
        self.assertIsInstance(block, StructBlock)

        # Check field existence
        self.assertIn('icon', block.child_blocks)
        self.assertIn('image', block.child_blocks)
        self.assertIn('title', block.child_blocks)
        self.assertIn('description', block.child_blocks)
        self.assertIn('link_url', block.child_blocks)
        self.assertIn('link_label', block.child_blocks)

        # Check required fields
        self.assertTrue(block.child_blocks['title'].required)
        self.assertFalse(block.child_blocks['icon'].required)
        self.assertFalse(block.child_blocks['image'].required)

    def test_block_structure(self):
        """Test the ServiceCardsBlock structure."""
        block = ServiceCardsBlock()
        self.assertIsInstance(block, StructBlock)

        self.assertIn('eyebrow', block.child_blocks)
        self.assertIn('heading', block.child_blocks)
        self.assertIn('intro', block.child_blocks)
        self.assertIn('cards', block.child_blocks)
        self.assertIn('layout_style', block.child_blocks)

        self.assertIsInstance(block.child_blocks['cards'], ListBlock)
        self.assertIsInstance(block.child_blocks['cards'].child_block, ServiceCardItemBlock)
