from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page, UserProfile


def index(request):
    # request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    # Call function to handle the cookies
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']

    # Obtain our Response object early so we can add cookie info.
    response = render(request, 'rango/index.html', context_dict)

    # Return response back to the user and updating cookies
    return response


def about(request):
    context_dict = {'about_site': 'This tutorial has been put together by Jose'}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    context_dict['last_visit'] = request.session['last_visit']
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    # Create a context dictionary to pass to template
    # Engine
    context_dict = {}
    try:
        # Can we find a category name slug with that name?
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve associated pages
        # Filter will return a list
        pages = Page.objects.filter(category=category)

        # Adds our results to the template page
        context_dict['pages'] = pages
        # We also add the category object from
        # The database to the context dictionary
        # We'll use this in the template to verify that category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if there's no category
        # Don't do anything
        context_dict['category'] = None
        context_dict['pages'] = None
    if request.method == 'POST':
        query = request.POST['query']
        results = Page.objects.filter(title__icontains=query)
        context_dict['result_list'] = results
    return render(request, 'rango/category.html', context=context_dict)


def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # Then we can direct the user back to the index page.
            return index(request)
        else:
            # The supplied form contains errors
            # Just print them to terminal
            print(form.errors)
        # Will handle the bad form, new form or no form supplied cases.
        # Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

'''
def register(request):
    # A boolean field for telling the template
    # Whether the registration was successful
    # Set to False initially. Code changes value to
    # True when registration is successful
    registered = False

    # If it's a HTTP POST, we're registering data
    if request.method == 'POST':
        # Attempt to grab information from the raw form information
        # Note that the we use both forms.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save data to db
            user = user_form.save()
            # Hash the password
            # Once hashed we can update the user object
            user.set_password(user.password)
            user.save()

            # Now sorting the UserProfile
            # Since we need to set the user attribute ourselves
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            # put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile
            profile.save()

            # Update our variable to indicate the template registration was successful
            registered = True
        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
        # Not an HTTP POST, so render the two ModelForm instances
        # Blank forms
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context
    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })

def user_login(request):
    # If the request is POST, pull info
    fail_auth = False
    if request.method == 'POST':
        # Gather userrname and password
        # This information is obtained from the form
        # We use request.POST.get(variable) as opposed
        # to request.POST[variable] because
        # request.POST.get returns None
        # if it does not exist
        # while request.POST[]
        # raises a keyError
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct
        # If None, no user with matching credentials
        if user:
            # Is the account active? It could be disabled/banned
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse('Your rango account is disabled')
        else:
            # Bad login details were provided. So we can't log the user in
            print("Invalid login details: {0},{1}".format(username, password))
            fail_auth = True
            return render(request, 'rango/login.html', {'fail_auth': fail_auth})

    # The request method is not HTTP POST so display the login form.
    # This scenario would most likely be HTTP GET
    else:
        # No context variable to pass to the template system, hence the
        # blank directory object...
        return render(request, 'rango/login.html', {})

# Use login required decorator to ensure only logged in users can log out
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
'''

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


# def visitor_cookie_handler(request, response):
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the vale returned is casted to int.
    # If the cookie doesn't exist it defaults to 1
    visits = int(request.COOKIES.get('visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    # last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now())) Old version
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        # update the last visit cookie now that the count is updated
        # response.set_cookie('last_visit', str(datetime.now())) Old Version
        request.session['last_visit'] = str(datetime.now())
    else:
        # set the last visit cookie
        # response.set_cookie('last_visit', last_visit_cookie)
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    if request.method == 'GET':
        page_id = request.GET['page_id']
        page = Page.objects.get(id=page_id)
        page.views += 1
        page.save()
        return redirect(page.url)
    else:
        return redirect(reverse('rango:index'))

@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('rango:index')
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'registration/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website': userprofile.website, 'picture': userprofile.picture})
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', username=user.username)
        else:
            print(form.errors)
    return render(request, 'registration/profile.html', {
        'userprofile': userprofile,
        'selecteduser': user,
        'form': form})

@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'registration/list_profiles.html', {'userprofile_list': userprofile_list})

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)
    return render(request, 'rango/cats.html', {'cats': cat_list})
