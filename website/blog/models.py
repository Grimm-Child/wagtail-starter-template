from django import forms
from django.db import models
from django.shortcuts import redirect, render

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField

from taggit.models import Tag, TaggedItemBase

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search.index import SearchField
from wagtail.snippets.models import register_snippet


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=255)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)

    search_fields = Page.search_fields + [
        SearchField('intro'),
        SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading='Blog information'),
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname='full'),
        InlinePanel('gallery_images', label='Gallery images'),
    ]

    def main_image(self):
        gallery_item = self.gallery_images.first()
        return gallery_item.image if gallery_item else None


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage,
        related_name='gallery_images',
        on_delete=models.CASCADE
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.CASCADE
    )
    caption = models.CharField(blank=True, max_length=255)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


# class BlogTagIndexPage(Page):
#     def get_context(self, request):
#         tag = request.GET.get('tag')
#         tagged_pages = BlogPage.objects.filter(tags__name=tag)
#         context = super().get_context(request)
#         context['tag'] = tag
#         context['tagged_pages'] = tagged_pages
#         return context


@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class BlogIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    def get_context(self, request, *args, **kwargs):
        posts = self.get_posts().order_by('-first_published_at')
        context = super().get_context(request)
        context['posts'] = posts
        return context

    @route(r'^tags/$', name='post_by_tag')
    @route(r'^tags/([\w-]+)/$', name='post_by_tag')
    def post_by_tag(self, request, tag=None):
        if tag:
            tag = Tag.objects.filter(slug=tag).first()
            posts = self.get_posts(tag=tag)
            context = super().get_context(request)
            context = {**context, 'tag': tag, 'posts': posts}
            return render(request, 'blog/blog_index_page.html', context)
        else:
            return redirect(self.url)

    def get_posts(self, tag=None):
        posts = BlogPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts
