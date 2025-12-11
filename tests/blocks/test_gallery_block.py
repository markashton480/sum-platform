"""
Name: Gallery Block Tests
Path: tests/blocks/test_gallery_block.py
Purpose: Unit tests for GalleryBlock and GalleryImageBlock structure and constraints.
Family: Part of the blocks-level test suite.
Dependencies: sum_core.blocks module, Wagtail blocks, pytest.
"""

from wagtail.blocks import StructBlock, ListBlock
from wagtail.images.blocks import ImageChooserBlock

from sum_core.blocks.gallery import GalleryBlock, GalleryImageBlock


class TestGalleryBlockStructure:
    """Test the GalleryBlock structure and child blocks."""

    def test_gallery_block_is_struct_block(self) -> None:
        """Test that GalleryBlock is a StructBlock."""
        block = GalleryBlock()
        assert isinstance(block, StructBlock)

    def test_gallery_block_has_required_child_blocks(self) -> None:
        """Test that GalleryBlock has eyebrow, heading, intro, and images."""
        block = GalleryBlock()

        assert "eyebrow" in block.child_blocks
        assert "heading" in block.child_blocks
        assert "intro" in block.child_blocks
        assert "images" in block.child_blocks

    def test_images_is_list_block_of_gallery_image_block(self) -> None:
        """Test that images is a ListBlock containing GalleryImageBlock."""
        block = GalleryBlock()
        images_block = block.child_blocks["images"]

        assert isinstance(images_block, ListBlock)
        assert isinstance(images_block.child_block, GalleryImageBlock)

    def test_images_list_constraints(self) -> None:
        """Test that images ListBlock has min_num=1 and max_num=24."""
        block = GalleryBlock()
        images_block = block.child_blocks["images"]

        assert images_block.meta.min_num == 1
        assert images_block.meta.max_num == 24

    def test_heading_is_richtext_block(self) -> None:
        """Test that heading is a RichTextBlock with bold/italic features."""
        from wagtail.blocks import RichTextBlock
        block = GalleryBlock()
        heading_block = block.child_blocks["heading"]
        assert isinstance(heading_block, RichTextBlock)
        assert "bold" in heading_block.features
        assert "italic" in heading_block.features

    def test_optional_fields(self) -> None:
        """Test that eyebrow, heading, and intro are optional."""
        block = GalleryBlock()
        assert not block.child_blocks["eyebrow"].required
        assert not block.child_blocks["heading"].required
        assert not block.child_blocks["intro"].required

    def test_block_meta_attributes(self) -> None:
        """Test that GalleryBlock has correct Meta attributes."""
        block = GalleryBlock()

        assert block.meta.icon == "image"
        assert block.meta.label == "Gallery"
        assert block.meta.template == "sum_core/blocks/gallery.html"


class TestGalleryImageBlockStructure:
    """Test the GalleryImageBlock structure."""

    def test_gallery_image_block_is_struct_block(self) -> None:
        """Test that GalleryImageBlock is a StructBlock."""
        block = GalleryImageBlock()
        assert isinstance(block, StructBlock)

    def test_gallery_image_block_has_required_fields(self) -> None:
        """Test that GalleryImageBlock has image, alt_text, caption."""
        block = GalleryImageBlock()

        assert "image" in block.child_blocks
        assert "alt_text" in block.child_blocks
        assert "caption" in block.child_blocks

    def test_image_field_is_required(self) -> None:
        """Test that image field is required."""
        block = GalleryImageBlock()
        assert block.child_blocks["image"].required

    def test_image_field_is_image_chooser_block(self) -> None:
        """Test that image field is an ImageChooserBlock."""
        block = GalleryImageBlock()
        assert isinstance(block.child_blocks["image"], ImageChooserBlock)

    def test_alt_text_is_optional(self) -> None:
        """Test that alt_text field is optional."""
        block = GalleryImageBlock()
        assert not block.child_blocks["alt_text"].required

    def test_caption_is_optional(self) -> None:
        """Test that caption field is optional."""
        block = GalleryImageBlock()
        assert not block.child_blocks["caption"].required

    def test_alt_text_max_length(self) -> None:
        """Test that alt_text has max_length of 255."""
        block = GalleryImageBlock()
        alt_text_block = block.child_blocks["alt_text"]
        # max_length is stored in field.max_length for CharBlock
        assert alt_text_block.field.max_length == 255

    def test_caption_max_length(self) -> None:
        """Test that caption has max_length of 255."""
        block = GalleryImageBlock()
        caption_block = block.child_blocks["caption"]
        # max_length is stored in field.max_length for CharBlock
        assert caption_block.field.max_length == 255
