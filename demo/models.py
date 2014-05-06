from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.management import call_command
from django.dispatch import receiver
from django.shortcuts import render
from django.http import HttpResponse

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from south.signals import post_migrate

from demo.utils import export_event


EVENT_AUDIENCE_CHOICES = (
    ('public', "Public"),
    ('private', "Private"),
)


COMMON_PANELS = (
    FieldPanel('slug'),
    FieldPanel('seo_title'),
    FieldPanel('show_in_menus'),
    FieldPanel('search_description'),
)


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class ContactFields(models.Model):
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    panels = [
        FieldPanel('telephone'),
        FieldPanel('email'),
        FieldPanel('address_1'),
        FieldPanel('address_2'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('post_code'),
    ]

    class Meta:
        abstract = True


# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Advert Snippet

class AdvertPlacement(models.Model):
    page = ParentalKey('wagtailcore.Page', related_name='advert_placements')
    advert = models.ForeignKey('demo.Advert', related_name='+')


class Advert(models.Model):
    page = models.ForeignKey(
        'wagtailcore.Page',
        related_name='adverts',
        null=True,
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    text = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('page'),
        FieldPanel('url'),
        FieldPanel('text'),
    ]

    def __unicode__(self):
        return self.text

register_snippet(Advert)


# Home Page


class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.HomePage', related_name='carousel_items')


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.HomePage', related_name='related_links')


class HomePage(Page):
    body = RichTextField(blank=True)
    headline = models.CharField(max_length=255, blank=True)
    features = RichTextField(blank=True)

    indexed_fields = ('body', )
    search_name = "Homepage"

    class Meta:
        verbose_name = "Homepage"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('headline'),
    FieldPanel('features'),
    FieldPanel('body', classname="full"),
    InlinePanel(HomePage, 'carousel_items', label="Carousel items"),
    InlinePanel(HomePage, 'related_links', label="Related links"),
]

HomePage.promote_panels     = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


# Standard index page

class StandardIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.StandardIndexPage', related_name='related_links')


class StandardIndexPage(Page):
    intro = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('intro', )
    search_name = None

StandardIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(StandardIndexPage, 'related_links', label="Related links"),
]

StandardIndexPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
    ImageChooserPanel('feed_image'),
]


# Standard page

class StandardPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.StandardPage', related_name='carousel_items')


class StandardPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.StandardPage', related_name='related_links')


class StandardPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('intro', 'body', )
    search_name = None

StandardPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(StandardPage, 'carousel_items', label="Carousel items"),
    FieldPanel('body', classname="full"),
    InlinePanel(StandardPage, 'related_links', label="Related links"),
]

StandardPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
    ImageChooserPanel('feed_image'),
]


# Blog index page

class BlogIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.BlogIndexPage', related_name='related_links')


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    indexed_fields = ('intro', )
    search_name = "Blog"

    @property
    def blogs(self):
        # Get list of blog pages that are descendants of this page
        blogs = BlogPage.objects.filter(
            live=True,
            path__startswith=self.path
        )

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    def serve(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        return render(request, self.template, {
            'self': self,
            'blogs': blogs,
        })

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(BlogIndexPage, 'related_links', label="Related links"),
]

BlogIndexPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


# Blog page

class BlogPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('demo.BlogPage', related_name='carousel_items')


class BlogPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('demo.BlogPage', related_name='related_links')


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('demo.BlogPage', related_name='tagged_items')


class BlogPage(Page):
    body = RichTextField()
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('body', )
    search_name = "Blog Entry"

    @property
    def blog_index(self):
        # Find blog index in ancestors
        for ancestor in reversed(self.get_ancestors()):
            if isinstance(ancestor.specific, BlogIndexPage):
                return ancestor

        # No ancestors are blog indexes,
        # just return first blog index in database
        return BlogIndexPage.objects.first()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('body', classname="full"),
    InlinePanel(BlogPage, 'carousel_items', label="Carousel items"),
    InlinePanel(BlogPage, 'related_links', label="Related links"),
]

BlogPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]



# Signal handler to load demo data from fixtures after migrations have completed
@receiver(post_migrate)
def import_demo_data(sender, **kwargs):
    # post_migrate will be fired after every app is migrated; we only want to do the import
    # after demo has been migrated
    if kwargs['app'] != 'demo':
        return

    # Check that there isn't already meaningful data in the db that would be clobbered.
    # A freshly created databases should contain no images, tags or snippets
    # and just two page records: root and homepage.
    if Image.objects.count() or Tag.objects.count() or Advert.objects.count() or Page.objects.count() > 2:
        return

    # furthermore, if any page has a more specific type than Page, that suggests that meaningful
    # data has been added
    for page in Page.objects.all():
        if page.specific_class != Page:
            return

    import os, shutil
    from django.conf import settings

    fixtures_dir = os.path.join(settings.PROJECT_ROOT, 'demo', 'fixtures')
    fixture_file = os.path.join(fixtures_dir, 'demo.json')
    image_src_dir = os.path.join(fixtures_dir, 'images')
    image_dest_dir = os.path.join(settings.MEDIA_ROOT, 'original_images')

    call_command('loaddata', fixture_file, verbosity=0)

    if not os.path.isdir(image_dest_dir):
        os.makedirs(image_dest_dir)

    for filename in os.listdir(image_src_dir):
        shutil.copy(os.path.join(image_src_dir, filename), image_dest_dir)
