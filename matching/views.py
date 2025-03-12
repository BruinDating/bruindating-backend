from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


from .models import Match, Swipe
from .serializers import MatchSerializer, PotentialMatchSerializer, UserSerializer
from auth_app.models import UCLAUser



class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]#permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:  
            return Match.objects.none() 
        return Match.objects.filter(user=user)

    def get_object(self):
        user = self.request.user
        match, created = Match.objects.get_or_create(user=user)
        return match


    @action(detail=False, methods=["get"])
    def matches(self, request):
        match = self.get_object()
        matched_users = match.matched.all()
        serializer = UserSerializer(matched_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def approved(self, request):
        match = self.get_object()
        approved_users = match.approved.all()
        serializer = UserSerializer(approved_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def rejected(self, request):
        match = self.get_object()
        rejected_users = match.rejected.all()
        serializer = UserSerializer(rejected_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def super_liked(self, request):
        match = self.get_object()
        super_liked_users = match.super_liked.all()
        serializer = UserSerializer(super_liked_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def approved_by(self, request):
        user = request.user
        approved_by_users = UCLAUser.objects.filter(match_profile__approved=user)
        serializer = UserSerializer(approved_by_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def super_liked_by(self, request):
        user = request.user
        super_liked_by_users = UCLAUser.objects.filter(match_profile__super_liked=user)
        serializer = UserSerializer(super_liked_by_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        try:
            target_user = UCLAUser.objects.get(pk=pk)
        except UCLAUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            return Response({"error": "You cannot approve yourself"}, status=status.HTTP_400_BAD_REQUEST)

        user_match, _ = Match.objects.get_or_create(user=request.user)
        target_match, _ = Match.objects.get_or_create(user=target_user)

        user_match.approved.add(target_user)

        if target_user in user_match.rejected.all():
            user_match.rejected.remove(target_user)

        is_match = request.user in target_match.approved.all()

        if is_match:
            user_match.matched.add(target_user)
            target_match.matched.add(request.user)

            return Response({"status": "approved", "is_match": True, "message": f"You matched with {target_user.name}!"}, status=status.HTTP_200_OK)

        return Response({"status": "approved", "is_match": False, "message": f"You approved {target_user.name}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        try:
            target_user = UCLAUser.objects.get(pk=pk)
        except UCLAUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            return Response({"error": "You cannot reject yourself"}, status=status.HTTP_400_BAD_REQUEST)

        user_match, _ = Match.objects.get_or_create(user=request.user)

        user_match.rejected.add(target_user)

        if target_user in user_match.approved.all():
            user_match.approved.remove(target_user)

        if target_user in user_match.matched.all():
            user_match.matched.remove(target_user)

            target_match, _ = Match.objects.get_or_create(user=target_user)
            target_match.matched.remove(request.user)

        return Response({"status": "rejected", "message": f"You rejected {target_user.name}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def super_like(self, request, pk=None):
        try:
            target_user = UCLAUser.objects.get(pk=pk)
        except UCLAUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            return Response({"error": "You cannot super like yourself"}, status=status.HTTP_400_BAD_REQUEST)

        user_match, _ = Match.objects.get_or_create(user=request.user)
        target_match, _ = Match.objects.get_or_create(user=target_user)

        user_match.super_liked.add(target_user)
        user_match.approved.add(target_user)

        if target_user in user_match.rejected.all():
            user_match.rejected.remove(target_user)

        is_match = request.user in target_match.approved.all()

        if is_match:
            user_match.matched.add(target_user)
            target_match.matched.add(request.user)

            return Response(
                {"status": "super_liked", "is_match": True, "message": f"You matched with {target_user.name}!"}, status=status.HTTP_200_OK
            )

        return Response({"status": "super_liked", "is_match": False, "message": f"You super liked {target_user.name}"}, status=status.HTTP_200_OK)


class PotentialMatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PotentialMatchSerializer
    permission_classes = [AllowAny]  # Allows anyone to access this endpoint

    def get_queryset(self):
        return UCLAUser.objects.all()  # Return all users for testing

def handle_match_creation(swiper, swiped_user):
    """
    Handle match creation between two users.
    Returns True if a match was created, False otherwise.
    """
    print(f"\n=== Handling match creation between {swiper.email} and {swiped_user.email} ===")
    
    # Get or create match profiles
    swiper_match, _ = Match.objects.get_or_create(user=swiper)
    swiped_match, _ = Match.objects.get_or_create(user=swiped_user)
    
    # Check if there's a mutual like
    mutual_like = Swipe.objects.filter(
        swiper=swiped_user,
        swiped=swiper,
        action='like'
    ).exists() and Swipe.objects.filter(
        swiper=swiper,
        swiped=swiped_user,
        action='like'
    ).exists()
    
    print(f"Mutual like exists: {mutual_like}")
    
    if mutual_like:
        print("Creating match...")
        # Add mutual approvals
        swiper_match.approved.add(swiped_user)
        swiped_match.approved.add(swiper)
        
        # Add mutual matches
        swiper_match.matched.add(swiped_user)
        swiped_match.matched.add(swiper)
        
        print("\nVerifying match creation:")
        print(f"{swiper.email}'s matches:", [u.email for u in swiper_match.matched.all()])
        print(f"{swiped_user.email}'s matches:", [u.email for u in swiped_match.matched.all()])
        return True
    else:
        # Just add to approved list
        swiper_match.approved.add(swiped_user)
        print(f"Added {swiped_user.email} to {swiper.email}'s approved list")
        return False

@api_view(['POST'])
@permission_classes([AllowAny])
def handle_swipe(request):
    """
    Handles swipe actions and match creation between users.
    
    Expected POST request data:
    - user_id (int): ID of the person being swiped on
    - action (str): Either 'like' or 'dislike'
    - swiper_email (str): Email of person doing the swipe
    
    Returns:
    - For matches: {'success': True, 'is_match': True, 'message': '...'}
    - For likes without match: {'success': True, 'is_match': False, 'message': '...'}
    - For dislikes: {'success': True, 'message': '...'}
    - For errors: {'error': 'error message'}
    """
    print("\n=== INCOMING SWIPE REQUEST ===")
    print("Request data:", request.data)
    
    # Parse incoming request data
    swiped_id = request.data.get('user_id')
    action = request.data.get('action')
    swiper_email = request.data.get('swiper_email')
    
    print(f"\nParsed data:")
    print(f"swiped_id: {swiped_id}")
    print(f"action: {action}")
    print(f"swiper_email: {swiper_email}")
    
    # Validate required fields
    if not swiped_id or action not in ['like', 'dislike']:
        print("Invalid data received!")
        return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get both users involved in the swipe
        swiped_user = UCLAUser.objects.get(id=swiped_id)
        swiper = UCLAUser.objects.get(email=swiper_email)
        
        print(f"\nFound users:")
        print(f"Swiper: {swiper.email} (ID: {swiper.id})")
        print(f"Swiped: {swiped_user.email} (ID: {swiped_user.id})")
        
        # Prevent self-swiping
        if swiper.id == swiped_user.id:
            return Response({'error': 'Cannot swipe on yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create swipe record in database
        swipe = Swipe.objects.create(
            swiper=swiper,
            swiped=swiped_user,
            action=action
        )
        print(f"\nCreated swipe record (ID: {swipe.id}):")
        print(f"{swiper.email} -> {swiped_user.email} ({action})")
        
        if action == 'like':
            print("\nHandling like action...")
            # Use handle_match_creation to check for match and handle all match logic
            is_match = handle_match_creation(swiper, swiped_user)
            
            if is_match:
                print("Match created successfully!")
                # TODO: Add your match handling logic here
                # - Initialize chat functionality
                # - Send match notifications
                # - Update UI for both users
                # - Store match metadata (timestamp, etc.)
                return Response({
                    'success': True,
                    'is_match': True,
                    'message': f'You matched with {swiped_user.email}!'
                })
            else:
                print("No match yet - waiting for reciprocal like")
                return Response({
                    'success': True,
                    'is_match': False,
                    'message': 'Like recorded'
                })
        else:  # dislike
            # Get or create match profiles for both users
            user_match, _ = Match.objects.get_or_create(user=swiper)
            target_match, _ = Match.objects.get_or_create(user=swiped_user)
            
            # Remove from approved and matched if they exist
            user_match.approved.remove(swiped_user)
            user_match.matched.remove(swiped_user)
            target_match.matched.remove(swiper)
            print(f"Removed {swiped_user.email} from {swiper.email}'s lists (dislike)")
            
            return Response({
                'success': True,
                'message': 'Dislike recorded'
            })
            
    except UCLAUser.DoesNotExist as e:
        print(f"User not found error: {str(e)}")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
