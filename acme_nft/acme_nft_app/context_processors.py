from .models import ProductEntry

def global_context(request):

    user = request.user
    
    # Load user product entries
    
    if user.is_authenticated:
        user_entries = ProductEntry.objects.filter(user=request.user)
    else:
        user_entries = ProductEntry.objects.filter(user=None)
        
    return {
        'products_in_cart': user_entries.filter(entry_type='CART'),
    }