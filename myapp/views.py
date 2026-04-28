from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMessage
from .models import *

from .models import Comment,Post
# Create your views here.

def _post_queryset():
    return Post.objects.select_related("category", "user")

def index(request):
    return render(request,"index.html",{
        'posts':_post_queryset().filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else Post.objects.none(),
        'top_posts':_post_queryset().order_by("-likes"),
        'recent_posts':_post_queryset().order_by("-id"),
        'user':request.user,
        'media_url':settings.MEDIA_URL
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username,email=email,password=password).save()
                return redirect('signin')
        else:
            messages.info(request,"Password should match")
            return redirect('signup')
            
    return render(request,"signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("index")
        else:
            messages.info(request,'Username or Password is incorrect')
            return redirect("signin")
            
    return render(request,"signin.html")

def logout(request):
    auth.logout(request)
    return redirect('index')

def blog(request):
    return render(request,"blog.html",{
            'posts':_post_queryset().filter(user_id=request.user.id).order_by("-id") if request.user.is_authenticated else Post.objects.none(),
            'top_posts':_post_queryset().order_by("-likes"),
            'recent_posts':_post_queryset().order_by("-id"),
            'user':request.user,
            'media_url':settings.MEDIA_URL
        })
    
def create(request):
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)
            image = request.FILES.get('image')
            Post(postname=postname, content=content, category=category, image=image, user=request.user).save()
        except Exception as e:
            print(f"Error: {e}")
        return redirect('index')
    else:
        categories = Category.objects.all()
        return render(request, "create.html", {"categories": categories})
    
def profile(request,id):
    
    return render(request,'profile.html',{
        'user':User.objects.get(id=id),
        'posts':Post.objects.all(),
        'media_url':settings.MEDIA_URL,
    })
    
    
def profileedit(request,id):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
    
        user = User.objects.get(id=id)
        user.first_name = firstname
        user.email = email
        user.last_name = lastname
        user.save()
        return profile(request,id)
    return render(request,"profileedit.html",{
        'user':User.objects.get(id=id),
    })
    
def increaselikes(request,id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save() 
    return redirect(request.META.get("HTTP_REFERER", "index"))


def post(request,id):
    post = _post_queryset().get(id=id)
    
    return render(request,"post-details.html",{
        "user":request.user,
        'post':post,
        'recent_posts':_post_queryset().exclude(id=id).order_by("-id"),
        'media_url':settings.MEDIA_URL,
        'comments':Comment.objects.select_related("user").filter(post_id = post.id),
        'total_comments': Comment.objects.filter(post_id = post.id).count()
    })
    
def savecomment(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id = post.id,user_id = request.user.id, content = content).save()
        return redirect("index")
    
def deletecomment(request,id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()
    return post(request,postid)
    
def editpost(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)  # Fetch the Category object
            
            post.postname = postname
            post.content = content
            post.category = category  # Assign the Category object
            post.save()
        except Exception as e:
            print(f"Error: {e}")
        return profile(request, request.user.id)
    
    categories = Category.objects.all()  # Fetch all categories for the dropdown
    return render(request, "postedit.html", {
        'post': post,
        'categories': categories
    })
    
def deletepost(request,id):
    Post.objects.get(id=id).delete()
    return profile(request,request.user.id)


def contact_us(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        messenger = request.POST.get('messenger', '').strip()
        message = request.POST.get('message', '').strip()
        answer_files = request.FILES.getlist("answer_files")

        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".heic", ".doc", ".docx"}
        total_size = sum(upload.size for upload in answer_files)
        errors = []

        if not answer_files:
            errors.append("Додайте файл з відповідями: фото, скріншот, PDF або документ.")

        for upload in answer_files:
            file_name = upload.name.lower()
            if not any(file_name.endswith(extension) for extension in allowed_extensions):
                errors.append(f"Файл {upload.name} має непідтримуваний формат.")
            if upload.size > settings.CONTACT_UPLOAD_MAX_SIZE:
                errors.append(f"Файл {upload.name} більший за дозволений розмір.")

        if total_size > settings.CONTACT_UPLOAD_MAX_TOTAL_SIZE:
            errors.append("Загальний розмір файлів завеликий. Спробуйте надіслати менше файлів або стиснути фото.")

        if errors:
            context["errors"] = errors
            context["form_data"] = request.POST
        else:
            subject = "Запит на навчання: діагностичний тест"
            file_names = ", ".join(upload.name for upload in answer_files)
            saved_message = (
                f"Instagram або Telegram: {messenger or 'не вказано'}\n\n"
                f"Повідомлення:\n{message or 'не вказано'}\n\n"
                f"Файли з відповідями: {file_names}"
            )

            Contact(name=name, email=email, subject=subject, message=saved_message).save()

            email_message = EmailMessage(
                subject=f"[Olena Khandii] {subject}",
                body=(
                    "Новий запит на навчання після діагностичного тесту.\n\n"
                    f"Ім'я: {name}\n"
                    f"Email: {email}\n"
                    f"Instagram або Telegram: {messenger or 'не вказано'}\n\n"
                    f"Повідомлення:\n{message or 'не вказано'}\n\n"
                    f"Файли: {file_names}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.TEACHER_EMAIL],
                reply_to=[email] if email else None,
            )

            for upload in answer_files:
                email_message.attach(upload.name, upload.read(), upload.content_type)

            try:
                email_message.send(fail_silently=False)
                context["success_message"] = (
                    "Дякую! Відповіді надіслано. Я перегляну тест і напишу вам щодо наступного кроку."
                )
            except Exception:
                context["errors"] = [
                    "Заявку збережено, але лист не вдалося надіслати. Будь ласка, напишіть напряму на email викладача."
                ]

    return render(request,"contact.html", context)

def booking(request):
    return render(request,"calendar_integration.html",{})

def services(request):
    return render(request,"services.html",{})

def prices(request):
    return render(request,"prices.html",{})

def rules(request):
    return render(request,"rules.html",{})

def aboutme(request):
    return render(request,"about.html",{})

def reviews(request):
    return redirect(settings.INSTAGRAM_REVIEWS_URL)
