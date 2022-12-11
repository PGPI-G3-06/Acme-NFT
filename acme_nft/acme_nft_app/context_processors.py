from .models import ProductEntry, User, ProfilePicture

def global_context(request):
    
    # Load user product entries and profile picture
    
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user)
        user_entries = ProductEntry.objects.filter(user=user)
        profile_picture, _ = ProfilePicture.objects.get_or_create(user=user)
        return {
            'products_in_cart': user_entries.filter(entry_type='CART'),
            'profile_pic': str(profile_picture.image)
        }
    else:
        user_entries = ProductEntry.objects.filter(user=None)
        return {
            'products_in_cart': user_entries.filter(entry_type='CART')
        }
    