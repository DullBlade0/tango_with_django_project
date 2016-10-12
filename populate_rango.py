import os
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
import django
django.setup()
from rango.models import Category, Page


def populate():
    # First create lists of dictionaries containing pages
    # Create dictionary of dictionaries for categories

    python_pages = [
        {'title': 'Official Python Tutorial',
         'url': 'http://docs.python.org/3/tutorial'},
        {'title': 'How to think like a Computer Scientist',
         'url': 'http://www.greenteapress.com/thinkpython/'},
        {'title': 'Learn Python in 10 Minutes',
         'url': 'http://korokithakis.net/tutorials/python/'}]

    django_pages = [
        {'title': 'Official Django Tutorial',
         'url': 'https://docs.djangoproject.com/en/dev/tutorial01/'},
        {'title': 'Django Rocks',
         'url': 'http://www.djangorocks.com'},
        {'title': 'How to Tango with Django',
         'url': 'http://www.tangowithdjango.com/'},
    ]

    other_pages = [
        {'title': 'Bottle',
         'url': 'http://bottlepy.com/docs/dev'},
        {'title': 'Flask',
         'url': 'http://flask.pocoo.org'},
    ]

    cats = {
        "Python": {"pages": python_pages},
        "Django": {"pages": django_pages},
        "Other Frameworks": {"pages": other_pages}}

    # To add more categories add above

    for cat, cat_data in cats.items():
        cat_views = 0
        cat_likes = 0
        if cat == "Python":
            cat_views = 128
            cat_likes = 64
        elif cat == "Django":
            cat_views = 64
            cat_likes = 32
        elif cat == "Other Frameworks":
            cat_views = 32
            cat_likes = 16
        c = add_cat(cat, cat_views, cat_likes)
        for p in cat_data["pages"]:
            add_page(c, p['title'], p['url'])

    # Print out the categories we have added
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print('- {0} - {1}'. format(str(c), str(p)))


def add_page(cat, title, url):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = random.randint(1,5000)
    p.save()
    return p


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c


# Start execution here!
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
