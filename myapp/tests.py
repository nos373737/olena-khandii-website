from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Post, Category, Comment, Contact

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", description="Test Description")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.description, "Test Description")
        self.assertEqual(str(self.category), "Test Category")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            postname="Test Post",
            category=self.category,
            content="Test Content",
            user=self.user,
        )

    def test_post_creation(self):
        self.assertEqual(self.post.postname, "Test Post")
        self.assertEqual(self.post.content, "Test Content")
        self.assertEqual(self.post.category.name, "Test Category")
        self.assertEqual(str(self.post), "Test Post")


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            postname="Test Post",
            category=self.category,
            content="Test Content",
            user=self.user,
        )
        self.comment = Comment.objects.create(
            content="Test Comment", post=self.post, user=self.user
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, "Test Comment")
        self.assertEqual(self.comment.post.postname, "Test Post")
        self.assertEqual(str(self.comment), f"{self.comment.id}.Test Comment...")


class ContactModelTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test Message",
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, "Test User")
        self.assertEqual(self.contact.email, "test@example.com")
        self.assertEqual(self.contact.subject, "Test Subject")
        self.assertEqual(self.contact.message, "Test Message")


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            postname="Test Post",
            category=self.category,
            content="Test Content",
            user=self.user,
        )

    def test_index_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_blog_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get("/blog")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog.html")

    def test_create_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get("/create")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create.html")

    def test_post_creation(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            "/create",
            {
                "postname": "New Post",
                "content": "New Content",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Post.objects.filter(postname="New Post").exists())