from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import Category, Comment, Contact, Post


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ("id", "name", "description")


class PostResource(resources.ModelResource):
    class Meta:
        model = Post
        fields = (
            "id",
            "postname",
            "category__name",
            "user__username",
            "content",
            "image",
            "time",
            "likes",
        )


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = ("id", "post__postname", "user__username", "content", "time")


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact
        fields = ("id", "name", "email", "subject", "message")


class EditorialAdminMixin(ImportExportModelAdmin, ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm


@admin.register(Category)
class CategoryAdmin(EditorialAdminMixin):
    resource_class = CategoryResource
    list_display = ("name", "post_count", "description_preview")
    search_fields = ("name", "description")
    ordering = ("name",)

    @admin.display(description="Posts")
    def post_count(self, obj):
        return obj.posts.count()

    @admin.display(description="Description")
    def description_preview(self, obj):
        if not obj.description:
            return "No description"
        return obj.description[:100]


class CommentInline(TabularInline):
    model = Comment
    extra = 0
    fields = ("user", "content", "time")
    readonly_fields = ("time",)
    autocomplete_fields = ("user",)
    show_change_link = True


@admin.register(Post)
class PostAdmin(EditorialAdminMixin):
    resource_class = PostResource
    list_display = (
        "thumbnail",
        "postname",
        "category",
        "user",
        "likes",
        "comment_count",
        "time",
    )
    list_display_links = ("thumbnail", "postname")
    list_filter = ("category", "user", "time")
    search_fields = ("postname", "content", "category__name", "user__username")
    autocomplete_fields = ("category", "user")
    readonly_fields = ("image_preview", "comment_count")
    inlines = (CommentInline,)
    ordering = ("-id",)
    list_per_page = 25
    actions = ("reset_likes",)
    fieldsets = (
        ("Publication", {"fields": ("postname", "category", "user")}),
        ("Content", {"fields": ("content", "image", "image_preview")}),
        ("Engagement", {"fields": ("likes", "comment_count", "time")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category", "user")
            .prefetch_related("comment_set")
        )

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "content":
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 20})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if not obj.image:
            return "No image"
        return format_html(
            '<img class="admin-thumb" src="{}" alt="" loading="lazy">',
            obj.image.url,
        )

    @admin.display(description="Image preview")
    def image_preview(self, obj):
        if not obj.image:
            return "No image uploaded"
        return format_html(
            '<img class="admin-preview" src="{}" alt="">',
            obj.image.url,
        )

    @admin.display(description="Comments")
    def comment_count(self, obj):
        return obj.comment_set.count()

    @admin.action(description="Reset likes to zero")
    def reset_likes(self, request, queryset):
        updated = queryset.update(likes=0)
        self.message_user(request, f"Reset likes for {updated} post(s).")


@admin.register(Comment)
class CommentAdmin(EditorialAdminMixin):
    resource_class = CommentResource
    list_display = ("content_preview", "post_link", "user", "time")
    list_filter = ("time", "user")
    search_fields = ("content", "post__postname", "user__username")
    autocomplete_fields = ("post", "user")
    ordering = ("-id",)
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("post", "user")

    @admin.display(description="Comment")
    def content_preview(self, obj):
        return obj.content[:120]

    @admin.display(description="Post")
    def post_link(self, obj):
        url = reverse("admin:myapp_post_change", args=(obj.post_id,))
        return format_html('<a href="{}">{}</a>', url, obj.post.postname)


@admin.register(Contact)
class ContactAdmin(EditorialAdminMixin):
    resource_class = ContactResource
    list_display = ("name", "email_link", "subject_preview", "message_preview")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message")
    ordering = ("name",)
    list_per_page = 30
    actions = ("export_as_text",)
    fieldsets = (
        ("Sender", {"fields": ("name", "email")}),
        ("Message", {"fields": ("subject", "message")}),
    )

    @admin.display(description="Email")
    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    @admin.display(description="Subject")
    def subject_preview(self, obj):
        return obj.subject[:90]

    @admin.display(description="Message")
    def message_preview(self, obj):
        return obj.message[:120]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Show selected messages in the admin log")
    def export_as_text(self, request, queryset):
        for contact in queryset:
            self.message_user(
                request,
                f"{contact.name} <{contact.email}> | {contact.subject}: {contact.message}",
            )
