from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import CategoryForm
from core.services import category_service


@login_required
def category_list(request):
    categories = category_service.get_categories(request.user.id)
    return render(request, 'categories/list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            category_service.create_category(
                request.user.id, d['name'], d['category_type'], d['color']
            )
            messages.success(request, 'Category created.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_update(request, pk):
    category = category_service.get_category(pk, request.user.id)
    if not category:
        messages.error(request, 'Category not found.')
        return redirect('category_list')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            category_service.update_category(
                pk, request.user.id, d['name'], d['category_type'], d['color']
            )
            messages.success(request, 'Category updated.')
            return redirect('category_list')
    else:
        form = CategoryForm(initial={
            'name': category['name'],
            'category_type': category['category_type'],
            'color': category['color'],
        })
    return render(request, 'categories/form.html', {
        'form': form, 'title': 'Edit Category', 'category': category
    })


@login_required
def category_delete(request, pk):
    category = category_service.get_category(pk, request.user.id)
    if not category:
        messages.error(request, 'Category not found.')
        return redirect('category_list')

    if request.method == 'POST':
        category_service.delete_category(pk, request.user.id)
        messages.success(request, 'Category deleted.')
        return redirect('category_list')

    return render(request, 'categories/confirm_delete.html', {'category': category})
