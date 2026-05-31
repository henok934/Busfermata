from drf_spectacular.utils import extend_schema
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import CustomUser
from .models import Feedback
from .models import Bus
from .models import Route
from django.db import IntegrityError
from .models import City
from .models import Buschange
from .models import Ticket
from rest_framework import generics, status
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render
from .models import Buschange, City  # Ensure you import your models
from drf_spectacular.utils import extend_schema
from .serializers import UserProfileSerializer, TicketSerializer
# top of users/views.py
from .serializers import (
    UserProfileSerializer,
    TicketSerializer
)
def custom_csrf_failure_view(request, reason=""):
    return render(request, 'users/csrf_failure.html', {'reason': reason})

from rest_framework.views import APIView
from django.shortcuts import render, redirect
from .models import CustomUser, Buschange # Import your custom user and stats models
from drf_spectacular.utils import extend_schema
from .serializers import UserProfileSerializer # Add this import
class ProfileView(APIView):
    @extend_schema(responses=UserProfileSerializer)
    def get(self, request):
        # 1. Retrieve the user ID from the session
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        # 2. SECURITY CHECK: If no session exists, redirect to login
        if not user_id:
            return render(request, 'users/login.html', {
                'error': 'Please login to access your Toward Country profile.',
                'buschanges_count': buschanges_count
            })

        try:
            # 3. Fetch the specific user
            user = CustomUser.objects.get(id=user_id)

            # 4. Render the profile page with the user data
            return render(request, 'users/profile.html', {
                'user': user,
                'buschanges_count': buschanges_count
            })

        except CustomUser.DoesNotExist:
            # 5. Handle case where session has an ID but user was deleted
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'User account not found.',
                'buschanges_count': buschanges_count
            })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import PaymentRequestSerializer
@extend_schema(tags=['Payment Auth'])
class ProcessPaymentView(APIView):
    serializer_class = PaymentRequestSerializer
    @extend_schema(
        summary="Process payment method selection",
        description="Redirects web users to bank pages or returns JSON instructions for API clients.",
        request=PaymentRequestSerializer
    )
    def post(self, request, *args, **kwargs):
        payment_method = request.data.get('payment_method')
        price = request.data.get('price')
        templates = {
            'cbe': 'users/cbe.html',
            'boa': 'users/boa.html',
            'telebirr': 'users/tele.html',
            'safaricom': 'users/safaricom.html',
            'awash': 'users/awash.html'
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            template_name = templates.get(payment_method, 'users/payment.html')
            return render(request, template_name, {'price': price})
        if payment_method in templates:
            return Response({
                'payment_method': payment_method,
                'price': price,
                'status': 'redirect_to_gateway',
                'message': f'Please proceed with {payment_method.upper()} payment.'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid payment method selected'}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Buschange
from .serializers import AboutSerializer # Import the new serializer

class About(APIView):
    @extend_schema(
        tags=['Routes & Cities'],
        summary="Get about page information",
        description="Returns the count of all bus changes for both API and HTML views.",
        responses={200: AboutSerializer}
    )
    @extend_schema(responses=AboutSerializer)
    def get(self, request):
        buschanges_count = Buschange.objects.count()

        context = {
            'buschanges_count': buschanges_count
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/about.html', context)
        serializer = AboutSerializer(context)
        return Response(serializer.data, status=status.HTTP_200_OK)



from .serializers import (UserSerializer,ChangePasswordSerializer, TotalBalanceResponseSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import City, Buschange  # Adjust based on your actual model imports
#@extend_schema(tags=['Routes & Cities'])
class HomeViews(APIView):
    @extend_schema(responses=UserSerializer)
    def get(self, request):
        buschanges = Buschange.objects.all()
        buschanges_count = buschanges.count()
        des = City.objects.all()

        context = {
            'des': des,
            'buschanges_count': buschanges_count if buschanges_count > 0 else None
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/index.html', context)

        response_data = {
            'cities': [city.depcity for city in des],
            'buschanges_count': buschanges_count
        }
        return Response(response_data, status=status.HTTP_200_OK)


from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render
from .models import Feedback, Buschange
from .serializers import FeedbackSerializer
class CommentsView(generics.GenericAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    def get(self, request, *args, **kwargs):
        buschanges_count = Buschange.objects.count()
        return render(request, 'users/comment.html', {'buschanges_count': buschanges_count})

    def post(self, request, *args, **kwargs):
        buschanges_count = Buschange.objects.count()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            message = serializer.validated_data['message']
            phone = serializer.validated_data['phone']
            email = serializer.validated_data['email']
            if Feedback.objects.filter(name=name, message=message, phone=phone, email=email).exists():
                return render(request, 'users/comment.html', {'buschanges_count': buschanges_count, 'error': 'This Comment already exists.'})
                return Response(
                    {'error': 'This Comment already exists.', 'buschanges_count': buschanges_count},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return render(request, 'users/comment.html', {'buschanges_count': buschanges_count, 'success': 'Comment submitted successfully.'})
            return Response(
                {'success': 'Comment submitted successfully.', 'buschanges_count': buschanges_count},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'error': serializer.errors, 'buschanges_count': buschanges_count},
            status=status.HTTP_400_BAD_REQUEST
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Bus
@extend_schema(tags=['Bus & Driver Management'])
class BusInsertViews(APIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'users/Businsert.html')
    def post(self, request, *args, **kwargs):
        print(request.data)
        plate_no = request.data.get('plate_no')
        sideno = request.data.get('sideno')
        no_seats = request.data.get('no_seats')
        level = request.data.get('level', 'unknown')  # Default to 'unknown' if not provided
        if not plate_no or not sideno or not no_seats:
            error_message = 'Plate number, Side number, and Number of seats are required.'
            return self.render_response(request, error=error_message)
        if Bus.objects.filter(plate_no=plate_no).exists():
            return self.render_response(request, error='Plate number already exists.')

        if Bus.objects.filter(sideno=sideno).exists():
            return self.render_response(request, error='Side number already exists.')
        Bus.objects.create(
            plate_no=plate_no,
            sideno=sideno,
            no_seats=no_seats,
            level=level
        )
        return self.render_response(request, success='Bus registered successfully.')

    def render_response(self, request, success=None, error=None):
        context = {}
        if success:
            context['success'] = success
        if error:
            context['error'] = error
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/Businsert.html', context)
        else:
            response_data = {'success': success} if success else {'error': error}
            return Response(response_data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)





from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
from drf_spectacular.utils import extend_schema
# Import your models and serializers
from .models import Route, City, Bus, Service_fee, Buschange  # Added Service_fee and Buschange
from .serializers import RouteSerializer
@extend_schema(tags=['Routes & Cities'])
class RoutesInsertView(LoginRequiredMixin, generics.GenericAPIView):
    login_url = '/'
    redirect_field_name = 'next'
    permission_classes = [IsAuthenticated]

    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_route_context(self, extra_context=None):
        # Added buschanges_count to maintain notification sync
        context = {
            'dep': City.objects.all(),
            'des': City.objects.all(),
            'bus': Bus.objects.all(),
            'buschanges_count': Buschange.objects.count(),
            'username': self.request.session.get('username')
        }
        if extra_context:
            context.update(extra_context)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, 'users/route.html', self.get_route_context())

    def post(self, request, *args, **kwargs):
        context = self.get_route_context()
        
        # 1. TARIFF REGISTRY GATE (Security & Financial Integrity)
        # Check if the service fee is set in the system
        fee_record = Service_fee.objects.first()
        if not fee_record or not fee_record.service_fee:
            context['error'] = "Tariff Protocol Error: Global Service Fee is not configured in the Registry."
            return render(request, 'users/route.html', context)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            depcity = data.get('depcity')
            descity = data.get('descity')
            route_date = data.get('date')
            plate_no = data.get('plate_no')
            side_no = data.get('side_no')
            price = data.get('price')
            kilometer = data.get('kilometer')

            # 2. VALIDATION: Identity Check (Source vs Destination)
            if str(depcity).strip().lower() == str(descity).strip().lower():
                context['error'] = 'Route Conflict: Departure and Destination cannot be identical.'
                return render(request, 'users/route.html', context)

            # 3. VALIDATION: Fleet Availability
            if Route.objects.filter(side_no=side_no, date=route_date, plate_no=plate_no).exists():
                context['error'] = f'Fleet Conflict: Bus {plate_no} is already assigned for this date.'
                return render(request, 'users/route.html', context)

            # 4. SAVE PRIMARY ROUTE
            serializer.save()

            # 5. AUTOMATIC RETURN TRIP LOGIC
            if str(depcity).strip() == "Addisababa":
                try:
                    if isinstance(route_date, str):
                        route_date = datetime.strptime(route_date, '%Y-%m-%d').date()

                    next_date = route_date + timedelta(days=1)

                    Route.objects.create(
                        depcity=descity,
                        descity=depcity,
                        kilometer=kilometer,
                        plate_no=plate_no,
                        side_no=side_no,
                        price=price,
                        date=next_date
                    )
                except Exception as e:
                    context['error'] = f'Registry Warning: Primary route saved, but return log failed: {str(e)}'
                    return render(request, 'users/route.html', context)

            context['success'] = 'Route Registry: Journey successfully logged.'
            return render(request, 'users/route.html', context)
        # 6. HANDLE VALIDATION ERRORS
        context['error'] = serializer.errors
        return render(request, 'users/route.html', context)


from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import City, Buschange, CustomUser  # Added CustomUser
from .serializers import CitySerializer
@extend_schema(tags=['Routes & Cities'])
class CityInsertView(generics.GenericAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to manage cities.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to modify the Route Registry
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required to update Route Registry.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED: Render the city template
        return render(request, 'users/city.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION & LOGIC
        serializer = self.get_serializer(data=request.data)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if serializer.is_valid():
            depcity = serializer.validated_data['depcity']

            # Business Logic: Case-insensitive uniqueness check
            if City.objects.filter(depcity__iexact=depcity).exists():
                context['error'] = 'Registry Conflict: This city is already registered in the system.'
                if is_html:
                    return render(request, 'users/city.html', context)
                return Response({'error': context['error']}, status=status.HTTP_400_BAD_REQUEST)

            # Save valid city
            serializer.save()
            context['success'] = 'Route Registry: New destination initialized successfully.'

            if is_html:
                return render(request, 'users/city.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)

        # 4. HANDLE VALIDATION ERRORS
        context['error'] = serializer.errors
        if is_html:
            return render(request, 'users/city.html', context)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import CustomUser, Buschange  # Added Buschange for the count
from .serializers import USerializer
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['User Management'])
class Use(APIView):
    serializer_class = USerializer

    def get(self, request):
        # 1. THE SECURITY GATE: Check session first
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            # Clear any stale session data and redirect to login
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage users.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch users
        users = CustomUser.objects.all()

        # 3. HANDLE HTML REQUESTS (Template Rendering)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/users.html', {
                'users': users,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 4. HANDLE API REQUESTS (JSON)
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Sc, Worker, CustomUser, Buschange  # Added Buschange
from .serializers import ScSerializer

@extend_schema(tags=['SC Management'])
class Sce(APIView):

    @extend_schema(
        summary="List all SC users",
        responses={200: ScSerializer(many=True)}
    )
    def get(self, request):
        # 1. THE SECURITY GATE: Retrieve session data
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        # 2. REDIRECT UNAUTHORIZED: Clear session and show login
        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage SC users.',
                'buschanges_count': buschanges_count
            })

        # 3. AUTHORIZED: Fetch data
        users = Sc.objects.all()

        # 4. HANDLE HTML RESPONSE
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/sce.html', {
                'users': users,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 5. HANDLE API RESPONSE
        serializer = ScSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
# Ensure Buschange is imported for the count logic
from .models import Bus, Buschange 
from .serializers import BusesSerializer
@extend_schema(tags=['Bus & Driver Management'])
class Buse(APIView):
    serializer_class = BusesSerializer

    @extend_schema(
        summary="List all buses",
        responses={200: BusesSerializer(many=True)}
    )
    def get(self, request):
        # 1. THE SECURITY GATE: Block unauthorized access
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage buses.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch data
        buses = Bus.objects.all()
        
        # 3. HANDLE HTML REQUESTS (Template Rendering)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buses.html', {
                'buses': buses,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 4. HANDLE API REQUESTS (JSON)
        serializer = self.serializer_class(buses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema

# Ensure Buschange is imported for the stats count
from .models import Worker, Buschange
from .serializers import WorkSerializer

@extend_schema(tags=['Bus & Driver Management'])
class Drivers(APIView):
    serializer_class = WorkSerializer

    @extend_schema(
        summary="List all Drivers (Workers)",
        responses={200: WorkSerializer(many=True)}
    )
    def get(self, request):
        # 1. THE SECURITY GATE: Verify session and get stats
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage drivers.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch data
        drivers = Worker.objects.all()

        # 3. HANDLE HTML REQUESTS (Template Rendering)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/drivers.html', {
                'driver': drivers, # Keeping your variable name 'driver' for the template
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 4. HANDLE API REQUESTS (JSON)
        serializer = self.serializer_class(drivers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema

# Ensure Buschange is imported for the dashboard count
from .models import Feedback, Buschange 
from .serializers import CommentteSerializer

@extend_schema(tags=['Feedback & Support'])
class Com(APIView):
    serializer_class = CommentteSerializer

    @extend_schema(
        summary="List all user feedback/comments",
        responses={200: CommentteSerializer(many=True)}
    )
    def get(self, request):
        # 1. THE SECURITY GATE: Block unauthorized session access
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to view feedback.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch comments
        comments = Feedback.objects.all()

        # 3. HANDLE HTML REQUESTS (Template Rendering)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/comments.html', {
                'comments': comments,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 4. HANDLE API REQUESTS (JSON)
        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
# Added Buschange to models import
from .models import Route, Buschange
from .serializers import RouteSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Routes Management'])
class Rout(APIView):
    serializer_class = RouteSerializer

    def get(self, request):
        # 1. THE SECURITY GATE: Verify session and get system stats
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            # Clear invalid session and redirect
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage routes.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch route data
        routes = Route.objects.all()

        # 3. HANDLE HTML REQUESTS
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/routes.html', {
                'routes': routes,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        # 4. HANDLE API REQUESTS
        serializer = self.serializer_class(routes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.shortcuts import render  # Import render
from .models import Ticket, Route
from .serializers import RouteSerializer, TickSerializer, RoutSerializer
@extend_schema(tags=['Booking & Tickets'])
@extend_schema(tags=['Bus & Driver Management'])
class SelectBusView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    def post(self, request):
        date = request.data.get('date')
        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        route = Ticket.objects.filter(plate_no=plate_no, date=date, depcity=depcity, descity=descity)
        routes = Route.objects.filter(date=date, depcity=depcity, descity=descity)
        if route.exists():
            serialized_route = TickSerializer(route, many=True)
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/ticketoch.html', {'route': serialized_route.data})
            else:
                return Response({'route': serialized_route.data})
        else:
            serialized_routes = RoutSerializer(routes, many=True)
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/rootee.html', {'error': 'No booked tickets for this travel', 'routes': serialized_routes.data})
            return Response({'error': 'No booked tickets for this travel', 'routes': serialized_routes.data})
        return Response({'error': 'Invalid request method'}, status=400)











from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema

from .models import Ticket, City, Bus
from .serializers import TSerializer, ChangePassengerRequestSerializer

@extend_schema(tags=['Booking & Tickets'])
class Changepassenger(APIView):
    serializer_class = ChangePassengerRequestSerializer

    @extend_schema(summary="Get passenger change page")
    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/changepassenger.html', {'des': des})
        return Response({'cities': [city.depcity for city in des]}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update passenger details on a ticket",
        request=ChangePassengerRequestSerializer,
        responses={200: TSerializer, 400: dict}
    )
    def post(self, request):
        # 1. Initialize variables to avoid NameErrors
        error_message = None
        level = None
        bus_name = None
        
        # Get request data
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        new_firstname = request.data.get('new_firstname')
        new_lastname = request.data.get('new_lastname')
        new_phone = request.data.get('new_phone')
        new_gender = request.data.get('new_gender')


        # 2. Find the ticket
        current_ticket = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            depcity=depcity,
            descity=descity,
            date=date
        ).first()

        if not current_ticket:
            return self._handle_response(request, None, "Original ticket not found", status.HTTP_404_NOT_FOUND)

        # 3. Pre-fetch Bus info so it's available for both success and error paths
        bus_info = Bus.objects.filter(plate_no=current_ticket.plate_no).first()
        if bus_info:
            level = bus_info.level
            bus_name = bus_info.name

        # 4. Validation logic
        if not all([new_firstname, new_lastname, new_phone]):
            error_message = 'All fields are required!'
        elif new_firstname.strip().lower() == new_lastname.strip().lower():
            error_message = 'Firstname and Lastname cannot be the same!'
        else:
            duplicate_exists = Ticket.objects.filter(
                firstname=new_firstname,
                lastname=new_lastname,
                phone=new_phone,
                depcity=depcity,
                descity=descity,
                date=date
            ).exclude(id=current_ticket.id).exists()

            if duplicate_exists:
                error_message = 'A ticket with these details already exists for this trip!'
            else:
                # Update and Save
                current_ticket.firstname = new_firstname
                current_ticket.lastname = new_lastname
                current_ticket.phone = new_phone
                current_ticket.gender = new_gender
                current_ticket.save()
                return self._handle_response(
                    request, current_ticket, "Updated successfully!", 
                    status.HTTP_200_OK, level=level, bus_name=bus_name
                )

        # Handle errors
        return self._handle_response(
            request, current_ticket, error_message, 
            status.HTTP_400_BAD_REQUEST, level=level, bus_name=bus_name
        )

    # 5. Added bus_name to method signature to match dictionary usage
    def _handle_response(self, request, ticket, message, status_code, qr_path=None, level=None, bus_name=None):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            context = {
                'ticket': ticket,
                'level': level,
                'name': bus_name, # Use the argument passed from post()
                'des': City.objects.all()
            }
            if status_code >= 400:
                context['error'] = message
            else:
                context['success'] = message
            
            # Using your passenger template from the snippet
            return render(request, 'users/passenger.html', context)

        # API response fallback
        if status_code >= 400:
            return Response({'error': message}, status=status_code)
        return Response(TSerializer(ticket).data, status=status_code)












import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket # Ensure Ticket model is imported
class CancelTicketView(APIView):
    def post(self, request):
        # 1. Retrieve data from form
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')
        password = request.data.get('password')
        
        # Hidden ticket identifiers for deletion
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        price = request.data.get('price')
        
        # Find the specific ticket to delete
        ticket_to_delete = Ticket.objects.filter(
        firstname=firstname,
        lastname=lastname,
        plate_no=plate_no,
        side_no=side_no
        ).first()
        if ticket_to_delete:
            ticket_to_delete.delete()
            context = {
                'success': 'Refund processed and ticket cancelled successfully.'
                }
            return render(request, 'users/index.html', context)
        return render(request, 'users/index.html', {'error': 'Ticket not found or already cancelled.'
        })






from rest_framework.views import APIView
from django.shortcuts import render
from .models import Ticket
class Recover_balanceView(APIView):
    def post(self, request):
        # 1. Extract context verification rules from form validation metadata
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden unique ticket identifiers
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        price = request.data.get('price')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')
        # 2. Locate targeted entry allocation matching hidden parameter components

        ticket = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            depcity=depcity,
            descity=descity,
            date=date
        ).first()  # Get the first ticket instance or None

        if ticket:
            plate_no = ticket.plate_no
            level = Bus.objects.filter(plate_no=plate_no).values_list('level', flat=True).first() if plate_no else None
            name = Bus.objects.filter(plate_no=plate_no).values_list('name', flat=True).first() if plate_no else None

            username = ticket.username
            fname = Worker.objects.filter(username=username).values_list('fname', flat=True).first() if username else ""
            lname = Worker.objects.filter(username=username).values_list('lname', flat=True).first() if username else ""
            #fname = Worker.objects.filter(username = username).values_list('fname', flat=True).first() if username else self
            #lname = Worker.objects.filter(username = username).values_list('lname', flat=True).first() if username else self
            #qr_code_path = ticket.generate_qr_code()  # Assuming generate_qr_code is a method of Ticket
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/tickets.html', {
                    'ticket': ticket,
                    'level': level,
                    'name': name,
                    'fname': fname,
                    'lname': lname,
                    #'qr_code_path': qr_code_path
                })
            else:
                serialized_ticket = TSerializer(ticket)
                return Response(serialized_ticket.data, status=status.HTTP_200_OK)

        return render(request, 'users/index.html', {
            'error': 'Ticket not found or already cancelled.'
        })







"""
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket, Bus, Worker  # Ensure all models are imported correctly
class Recover_balanceView(APIView):
    def post(self, request):
        # 1. Retrieve data from HTML form submission
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden ticket identifiers passed by frontend
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        # 2. Find the specific ticket to process and extract details before deletion
        ticket = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            depcity=depcity,
            descity=descity,
            date=date
        ).first()

        if not ticket:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Ticket not found or already processed.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 3. Dynamic Merchant Master Configuration based on selected gateway
        if method == 'telebirr':
            merchant_master_account = "0975143134"
        elif method == 'cbe':
            merchant_master_account = "1000327248549"
        elif method == 'boa':
            merchant_master_account = "48710778"
        else:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Unsupported payment method selected.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 4. Process Refund Balances
        # Get current pool balance from the API wrapper
        merchant_balance = self.get_gateway_balance(merchant_master_account)
        customer_balance = self.get_gateway_balance(account_number)

        # Verify system account balance can back the refund action
        if merchant_balance is None:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Unable to verify gateway master balance configuration.'},
                status.HTTP_502_BAD_GATEWAY
            )

        if merchant_balance < price:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'System balance processing limit reached. Contact customer care.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 5. Core Ledger Calculations
        new_merchant_balance = merchant_balance - price
        new_customer_balance = (customer_balance or 0.0) + price

        # 6. Execute Simulated Core Network Transactions
        transaction_response = self.execute_gateway_transaction(account_number, price)

        if transaction_response.get('success'):
            # Update balances within API gateways
            update_merchant = self.update_gateway_balance(merchant_master_account, new_merchant_balance)
            update_customer = self.update_gateway_balance(account_number, new_customer_balance)

            if update_merchant.get('success') and update_customer.get('success'):

                # Fetch related meta-information required by the dynamic template response prior to deletion
                t_plate_no = ticket.plate_no
                level = Bus.objects.filter(plate_no=t_plate_no).values_list('level', flat=True).first() if t_plate_no else None
                name = Bus.objects.filter(plate_no=t_plate_no).values_list('name', flat=True).first() if t_plate_no else None

                username = ticket.username
                fname = Worker.objects.filter(username=username).values_list('fname', flat=True).first() if username else ""
                lname = Worker.objects.filter(username=username).values_list('lname', flat=True).first() if username else ""

                # Core deletion after confirmed money movement safety block execution completes
                ticket.delete()

                context = {
                    'success': f'Refund of {price} ETB processed back to account {account_number} and ticket completed successfully.',
                    'transaction_id': transaction_response.get('transaction_id'),
                    'ticket': ticket,
                    'level': level,
                    'name': name,
                    'fname': fname,
                    'lname': lname
                }

                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    return render(request, 'users/tickets.html', context)
                else:
                    return Response({
                        'status': 'success',
                        'message': context['success'],
                        'transaction_id': context['transaction_id']
                    }, status=status.HTTP_200_OK)
            else:
                return self.render_response(
                    request,
                    'users/index.html',
                    {'error': 'Failed to adjust system settlement balances.'},
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return self.render_response(
                request,
                'users/index.html',
                {'error': f'{method.upper()} transaction network reversal failed.'},
                status.HTTP_502_BAD_GATEWAY
            )

    # Helper function to serve HTML forms or JSON gracefully based on client request headers
    def render_response(self, request, template_name, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, template_name, context)
        return Response(context, status=status_code)

    # Mock gateway integrations unified to point towards your telebirr API specs mapping
    def get_gateway_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number, 'phone': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception:
            return None

    def execute_gateway_transaction(self, target_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': target_account, 'phone': target_account, 'amount': amount, 'description': 'Ticket Reimbursement Reversal'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}

    def update_gateway_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'phone': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}

"""



"""
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket, Bus, Worker  # Ensure all models are imported correctly
class Recover_balanceView(APIView):
    def post(self, request):
        # 1. Retrieve data from HTML form submission
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden ticket identifiers passed by frontend
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        # 2. Find the specific ticket to process and extract details before deletion
        ticket = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            depcity=depcity,
            descity=descity,
            date=date
        ).first()

        if not ticket:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Ticket not found or already processed.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 3. Dynamic Merchant Master Configuration based on selected gateway
        if method == 'telebirr':
            merchant_master_account = "0975143134"
        elif method == 'cbe':
            merchant_master_account = "1000327248549"
        elif method == 'boa':
            merchant_master_account = "48710778"
        else:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Unsupported payment method selected.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 4. Process Refund Balances
        # Get current pool balance from the API wrapper
        merchant_balance = self.get_gateway_balance(merchant_master_account)
        customer_balance = self.get_gateway_balance(account_number)

        # Verify system account balance can back the refund action
        if merchant_balance is None:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'Unable to verify gateway master balance configuration.'},
                status.HTTP_502_BAD_GATEWAY
            )

        if merchant_balance < price:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'System balance processing limit reached. Contact customer care.'},
                status.HTTP_400_BAD_REQUEST
            )

        # 5. Core Ledger Calculations
        new_merchant_balance = merchant_balance - price
        new_customer_balance = (customer_balance or 0.0) + price

        # 6. Execute Simulated Core Network Transactions
        transaction_response = self.execute_gateway_transaction(account_number, price)

        if transaction_response.get('success'):
            # Update balances within API gateways
            update_merchant = self.update_gateway_balance(merchant_master_account, new_merchant_balance)
            update_customer = self.update_gateway_balance(account_number, new_customer_balance)

            if update_merchant.get('success') and update_customer.get('success'):

                # Fetch related meta-information required by the dynamic template response prior to deletion
                t_plate_no = ticket.plate_no
                level = Bus.objects.filter(plate_no=t_plate_no).values_list('level', flat=True).first() if t_plate_no else None
                name = Bus.objects.filter(plate_no=t_plate_no).values_list('name', flat=True).first() if t_plate_no else None

                username = ticket.username
                fname = Worker.objects.filter(username=username).values_list('fname', flat=True).first() if username else ""
                lname = Worker.objects.filter(username=username).values_list('lname', flat=True).first() if username else ""

                # Core deletion after confirmed money movement safety block execution completes
                ticket.delete()

                context = {
                    'success': f'Refund of {price} ETB processed back to account {account_number} and ticket completed successfully.',
                    'transaction_id': transaction_response.get('transaction_id'),
                    'ticket': ticket,
                    'level': level,
                    'name': name,
                    'fname': fname,
                    'lname': lname
                }

                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    return render(request, 'users/tickets.html', context)
                else:
                    return Response({
                        'status': 'success',
                        'message': context['success'],
                        'transaction_id': context['transaction_id']
                    }, status=status.HTTP_200_OK)
            else:
                return self.render_response(
                    request,
                    'users/index.html',
                    {'error': 'Failed to adjust system settlement balances.'},
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return self.render_response(
                request,
                'users/index.html',
                {'error': f'{method.upper()} transaction network reversal failed.'},
                status.HTTP_502_BAD_GATEWAY
            )

    # Helper function to serve HTML forms or JSON gracefully based on client request headers
    def render_response(self, request, template_name, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, template_name, context)
        return Response(context, status=status_code)

    # Mock gateway integrations unified to point towards your telebirr API specs mapping
    def get_gateway_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number, 'phone': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception:
            return None

    def execute_gateway_transaction(self, target_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': target_account, 'phone': target_account, 'amount': amount, 'description': 'Ticket Reimbursement Reversal'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}

    def update_gateway_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'phone': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}






import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket  # Ensure Ticket model is imported
class Recover_balanceView(APIView):
    def post(self, request):
        # 1. Retrieve data from HTML form submission
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden ticket identifiers passed by frontend
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0
        # 2. Find the specific ticket to delete
        ticket_to_delete = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            plate_no=plate_no,
            side_no=side_no
        ).first()

        if not ticket_to_delete:
            return self.render_response(request, 'users/index.html', {'error': 'Ticket not found or already cancelled.'}, status.HTTP_400_BAD_REQUEST)

        # 3. Dynamic Merchant Master Configuration based on selected gateway
        if method == 'telebirr':
            merchant_master_account = "0975143134"
        elif method == 'cbe':
            merchant_master_account = "1000327248549"
        elif method == 'boa':
            merchant_master_account = "48710778"
        else:
            return self.render_response(request, 'users/index.html', {'error': 'Unsupported payment method selected.'}, status.HTTP_400_BAD_REQUEST)

        # 4. Process Refund Balances
        # Get current pool balance from the API wrapper
        merchant_balance = self.get_gateway_balance(merchant_master_account)
        customer_balance = self.get_gateway_balance(account_number)
        # Verify system account can back the refund action
        if merchant_balance < price:
            return self.render_response(request, 'users/index.html', {'error': 'System balance processing limit reached. Contact customer care.'}, status.HTTP_400_BAD_REQUEST)

        # 5. Core Ledger Calculations
        new_merchant_balance = merchant_balance - price
        new_customer_balance = (customer_balance or 0.0) + price

        # 6. Execute Simulated Core Network Transactions
        transaction_response = self.execute_gateway_transaction(account_number, price)

        if transaction_response.get('success'):
            # Update balances within API gateways
            update_merchant = self.update_gateway_balance(merchant_master_account, new_merchant_balance)
            update_customer = self.update_gateway_balance(account_number, new_customer_balance)

            if update_merchant.get('success') and update_customer.get('success'):
                # Core deletion after confirmed money movement safety block
                ticket_to_delete.delete()

                context = {
                    'success': f'Refund of {price} ETB processed back to account {account_number} and ticket cancelled successfully.',
                    'transaction_id': transaction_response.get('transaction_id')
                }
                return self.render_response(request, 'users/index.html', context, status.HTTP_200_OK)
            else:
                return self.render_response(request, 'users/index.html', {'error': 'Failed to adjust system settlement balances.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return self.render_response(request, 'users/index.html', {'error': f'{method.upper()} transaction network reversal failed.'}, status.HTTP_502_BAD_GATEWAY)
        

    # Helper function to serve HTML forms or JSON gracefully based on client request headers
    def render_response(self, request, template_name, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, template_name, context)
        return Response(context, status=status_code)

    # Mock gateway integrations unified to point towards your telebirr API specs mapping
    def get_gateway_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number, 'phone': account_number} # satisfies both parameter schemes
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception:
            return None

    def execute_gateway_transaction(self, target_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': target_account, 'phone': target_account, 'amount': amount, 'description': 'Ticket Cancellation Reversal'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}


    def update_gateway_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'phone': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}
"""




"""
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket  # Ensure Ticket model is imported
class CancelTicketView(APIView):
    def post(self, request):
        # 1. Retrieve data from HTML form submission
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden ticket identifiers passed by frontend
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        # 2. Find the specific ticket to delete
        ticket_to_delete = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            plate_no=plate_no,
            side_no=side_no
        ).first()

        if not ticket_to_delete:
            return self.render_response(request, 'users/index.html', {'error': 'Ticket not found or already cancelled.'}, status.HTTP_400_BAD_REQUEST)

        # 3. Dynamic Merchant Master Configuration based on selected gateway
        if method == 'telebirr':
            merchant_master_account = "0975143134"
        elif method == 'cbe':
            merchant_master_account = "1000327248549"
        elif method == 'boa':
            merchant_master_account = "48710778"
        else:
            return self.render_response(request, 'users/index.html', {'error': 'Unsupported payment method selected.'}, status.HTTP_400_BAD_REQUEST)

        # 4. Process Refund Balances
        # Get current pool balance from the API wrapper
        merchant_balance = self.get_gateway_balance(merchant_master_account)
        customer_balance = self.get_gateway_balance(account_number)

        if merchant_balance is None:
            return self.render_response(request, 'users/index.html', {'error': f"Failed to connect to {method.upper()} gateway balance checking."}, status.HTTP_502_BAD_GATEWAY)

        # Verify system account can back the refund action
        if merchant_balance < price:
            return self.render_response(request, 'users/index.html', {'error': 'System balance processing limit reached. Contact customer care.'}, status.HTTP_400_BAD_REQUEST)

        # 5. Core Ledger Calculations
        new_merchant_balance = merchant_balance - price
        new_customer_balance = (customer_balance or 0.0) + price

        # 6. Execute Simulated Core Network Transactions
        transaction_response = self.execute_gateway_transaction(account_number, price)

        if transaction_response.get('success'):
            # Update balances within API gateways
            update_merchant = self.update_gateway_balance(merchant_master_account, new_merchant_balance)
            update_customer = self.update_gateway_balance(account_number, new_customer_balance)

            if update_merchant.get('success') and update_customer.get('success'):
                # Core deletion after confirmed money movement safety block
                ticket_to_delete.delete()

                context = {
                    'success': f'Refund of {price} ETB processed back to account {account_number} and ticket cancelled successfully.',
                    'transaction_id': transaction_response.get('transaction_id')
                }
                return self.render_response(request, 'users/index.html', context, status.HTTP_200_OK)
            else:
                return self.render_response(request, 'users/index.html', {'error': 'Failed to adjust system settlement balances.'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return self.render_response(request, 'users/index.html', {'error': f'{method.upper()} transaction network reversal failed.'}, status.HTTP_502_BAD_GATEWAY)

    # Helper function to serve HTML forms or JSON gracefully based on client request headers
    def render_response(self, request, template_name, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, template_name, context)
        return Response(context, status=status_code)

    # Mock gateway integrations unified to point towards your telebirr API specs mapping
    def get_gateway_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number, 'phone': account_number} # satisfies both parameter schemes
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception:
            return None

    def execute_gateway_transaction(self, target_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': target_account, 'phone': target_account, 'amount': amount, 'description': 'Ticket Cancellation Reversal'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}

    def update_gateway_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'phone': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}
"""




"""
import requests
from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Ticket  # Ensure Ticket model is imported
class CancelTicketView(APIView):
    def post(self, request):
        # 1. Retrieve data from HTML form submission
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')

        # Hidden ticket identifiers passed by frontend
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        # 2. Find the specific ticket to process
        ticket_to_delete = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            plate_no=plate_no,
            side_no=side_no
        ).first()

        if not ticket_to_delete:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'ትኬቱ አልተገኘም ወይም አስቀድሞ ተሰርዟል። (Ticket not found or already cancelled.)'},
                status.HTTP_400_BAD_REQUEST
            )

        # 3. Dynamic Merchant Master Configuration based on selected gateway
        if method == 'telebirr':
            merchant_master_account = "0975143134"
        elif method == 'cbe':
            merchant_master_account = "1000327248549"
        elif method == 'boa':
            merchant_master_account = "48710778"
        else:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'ያልተደገፈ የክፍያ መንገድ። (Unsupported payment method.)'},
                status.HTTP_400_BAD_REQUEST
            )

        # 4. Fetch live gateway balances
        merchant_balance = self.get_gateway_balance(merchant_master_account)
        customer_balance = self.get_gateway_balance(account_number)

        if merchant_balance is None:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'ከባንክ መገናኛ መስመር ጋር መገናኘት አልተቻለም። (Failed to connect to payment gateway.)'},
                status.HTTP_502_BAD_GATEWAY
            )

        if merchant_balance < price:
            return self.render_response(
                request,
                'users/index.html',
                {'error': 'የሲስተም ሂሳብ ገደብ ላይ ደርሷል። እባክዎ ድጋፍ ሰጪዎችን ያግኙ። (System balance processing limit reached.)'},
                status.HTTP_400_BAD_REQUEST
            )

        # 5. Core Ledger Calculations
        new_merchant_balance = merchant_balance - price
        new_customer_balance = (customer_balance or 0.0) + price

        # 6. Execute the balance movement using an atomic database lock
        try:
            with transaction.atomic():
                # Call external gateway API to move the funds
                transaction_response = self.execute_gateway_transaction(account_number, price)

                if transaction_response.get('success'):
                    # Synchronize updated balances back to respective systems
                    update_merchant = self.update_gateway_balance(merchant_master_account, new_merchant_balance)
                    update_customer = self.update_gateway_balance(account_number, new_customer_balance)

                    if update_merchant.get('success') and update_customer.get('success'):

                        # --- CRITICAL FIX: DELETE TICKET SECURELY ---
                        ticket_to_delete.delete()

                        context = {
                            'success': f'የትኬት መሰረዙ ተሳክቷል! {price} ብር ወደ መለያ ቁጥር {account_number} ተመልሷል።',
                            'transaction_id': transaction_response.get('transaction_id')
                        }
                        return self.render_response(request, 'users/index.html', context, status.HTTP_200_OK)
                    else:
                        raise Exception("Failed to adjust system settlement balances.")
                else:
                    raise Exception("Gateway transaction network reversal rejected.")

        except Exception as e:
            # If anything fails inside the block, database operations roll back safely
            return self.render_response(
                request,
                'users/index.html',
                {'error': f'ስህተት፡ {str(e)}'},
                status.HTTP_502_BAD_GATEWAY
            )

    def render_response(self, request, template_name, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, template_name, context)
        return Response(context, status=status_code)

    # Gateway API Integrations pointing to your endpoints
    def get_gateway_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number, 'phone': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception:
            return None

    def execute_gateway_transaction(self, target_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': target_account, 'phone': target_account, 'amount': amount, 'description': 'Ticket Cancellation Reversal'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}

    def update_gateway_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'phone': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception:
            return {'success': False}
"""



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Ticket, City, Bus
from .serializers import TSerializer
from drf_spectacular.utils import extend_schema
from .serializers import UserProfileSerializer, TicketSerializer # Add TicketSerializer here
class GetTicketViews(APIView):
    serializer_class = TicketSerializer  # Add this
    #@extend_schema(responses=TicketSerializer(many=True))
    #@extend_schema(responses=TicketSerializer(many=True))
    #@extend_schema(responses=TicketSerializer(many=True))
    @extend_schema(responses=TicketSerializer(many=True))
    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/getticket.html', {'des': des})
        return Response({'des': [city.depcity for city in des]}, status=status.HTTP_200_OK)

    def post(self, request):
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        # Validate input
        if depcity == descity:
            error_message = 'Departure and Destination cannot be the same!'
        elif firstname == lastname:
            error_message = 'Firstname and Lastname cannot be the same!'
        else:
            error_message = None

        if error_message:
            des = City.objects.all()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/getticket.html', {
                    'error': error_message,
                    'des': des
                })
            else:
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the ticket
        ticket = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            depcity=depcity,
            descity=descity,
            date=date
        ).first()  # Get the first ticket instance or None

        if ticket:
            plate_no = ticket.plate_no
            level = Bus.objects.filter(plate_no=plate_no).values_list('level', flat=True).first() if plate_no else None
            name = Bus.objects.filter(plate_no=plate_no).values_list('name', flat=True).first() if plate_no else None

            username = ticket.username
            fname = Worker.objects.filter(username=username).values_list('fname', flat=True).first() if username else ""
            lname = Worker.objects.filter(username=username).values_list('lname', flat=True).first() if username else ""
            #fname = Worker.objects.filter(username = username).values_list('fname', flat=True).first() if username else self
            #lname = Worker.objects.filter(username = username).values_list('lname', flat=True).first() if username else self
            #qr_code_path = ticket.generate_qr_code()  # Assuming generate_qr_code is a method of Ticket
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/tickets.html', {
                    'ticket': ticket,
                    'level': level,
                    'name': name,
                    'fname': fname,
                    'lname': lname,
                    #'qr_code_path': qr_code_path
                })
            else:
                serialized_ticket = TSerializer(ticket)
                return Response(serialized_ticket.data, status=status.HTTP_200_OK)
        else:
            # No ticket found
            des = City.objects.all()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/getticket.html', {
                    'error': 'No booked tickets for this travel',
                    'des': des
                })
            else:
                return Response({'error': 'No booked tickets found for this travel'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from .models import Buschange, Route, Worker, Sc
from .serializers import LoginRequestSerializer
class LoginView(APIView):
    serializer_class = LoginRequestSerializer

    @extend_schema(tags=['Authentication'], summary="Get login page or bus counts")
    def get(self, request):
        buschanges_count = Buschange.objects.count()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/login.html', {'buschanges_count': buschanges_count})
        return Response({'buschanges_count': buschanges_count}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Authentication'],
        summary="Login for Workers, Users, or SCs",
        request=LoginRequestSerializer
    )
    def post(self, request):
        buschanges_count = Buschange.objects.count()
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role')

        if role == 'worker':
            return self.handle_worker_login(username, password, buschanges_count, request)
        elif role == 'user':
            return self.handle_user_login(username, password, buschanges_count, request)
        elif role == 'sc':
            return self.handle_sc_login(username, password, buschanges_count, request)

        #return Response({'error': 'Invalid role specified'}, status=status.HTTP_400_BAD_REQUEST)
        return self.handle_login_error(buschanges_count, request, 'Invalid role specified')

    def handle_worker_login(self, username, password, buschanges_count, request):
        try:
            worker = Worker.objects.get(username=username)
            if not check_password(password, worker.password):
                raise Worker.DoesNotExist

            # 1. Get today's range (start of day to end of day)
            today = timezone.now().date()

            # 2. Filter tickets by this worker's username AND today's date
            # We use Cast if price is CharField, but here we assume it's numeric-friendly
            tickets_today = Ticket.objects.filter(
            username=worker.username,
            booked_time__date=today
        )
            # 3. Calculate Total Price
            # Note: If price is a CharField, we must convert it during the sum
            from django.db.models.functions import Cast
            from django.db.models import FloatField
            total_sum = tickets_today.annotate(
            price_as_float=Cast('price', FloatField())
            ).aggregate(total=Sum('price_as_float'))['total'] or 0

            # Save to session
            request.session['worker_id'] = worker.id
            request.session['username'] = worker.username
            request.session['total_today'] = total_sum

            context = {
            'username': worker.username,
            'lname': worker.lname,
            'fname': worker.fname,
            'phone': worker.phone,
            'total_today': total_sum,  # Pass this to the template
            }
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/rooteee.html', context)

            return Response(context, status=status.HTTP_200_OK)

        except Worker.DoesNotExist:
            return self.handle_login_error(buschanges_count, request, 'Worker credentials not found')
    
    def handle_user_login(self, username, password, buschanges_count, request):
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Save to session
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = 'user'
            request.session.modified = True
            return render(request, 'users/profile.html', {'user': user, 'buschanges_count': buschanges_count})
        return self.handle_login_error(buschanges_count, request, 'Invalid user credentials')
    

    def handle_sc_login(self, username, password, buschanges_count, request):
        try:
            sc_user = Sc.objects.get(username=username)
            if not check_password(password, sc_user.password):
                return self.handle_login_error(buschanges_count, request, 'Invalid password')

            # Set session storage parameters safely
            request.session['sc_id'] = sc_user.id
            request.session['username'] = sc_user.username
            request.session['firstname'] = sc_user.firstname
            request.session['lastname'] = sc_user.lastname

            side_parts = sc_user.side.split('/')
            first_part = side_parts[0].strip()
            second_part = side_parts[1].strip() if len(side_parts) == 2 else None

            if first_part == '3' or second_part == '3':
                routes = Route.objects.filter(side_no__regex=r'^\d{3}$')
            else:
                filters = Q(side_no__startswith=first_part, side_no__regex=r'^\d{4}$')
                if second_part:
                    filters |= Q(side_no__startswith=second_part, side_no__regex=r'^\d{4}$')
                routes = Route.objects.filter(filters)

            serialized_routes = self.serialize_routes(routes)

            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                # FIXED: Corrected template name string from 'users/rooteeess.html' to 'users/rooteees.html'
                return render(request, 'users/rooteeess.html', {
                'routes': serialized_routes,
                'company': sc_user,          # Inlines logo binary link mapping
                'level': sc_user.level,      # Inlines the Station Authority classification marker
                'name': sc_user.name,
                'firstname': sc_user.firstname,
                'lastname': sc_user.lastname,
                'side': sc_user.side
            })
            return Response({'routes': serialized_routes}, status=status.HTTP_200_OK)

        except Sc.DoesNotExist:
            return self.handle_login_error(buschanges_count, request, 'Invalid username')

    """
    def handle_sc_login(self, username, password, buschanges_count, request):
        try:
            sc_user = Sc.objects.get(username=username)
            if not check_password(password, sc_user.password):
                return self.handle_login_error(buschanges_count, request, 'Invalid password')

            request.session['sc_id'] = sc_user.id
            request.session['username'] = sc_user.username
            request.session['firstname'] = sc_user.firstname
            request.session['lastname'] = sc_user.lastname

            side_parts = sc_user.side.split('/')
            first_part = side_parts[0].strip()
            second_part = side_parts[1].strip() if len(side_parts) == 2 else None

            if first_part == '3' or second_part == '3':
                routes = Route.objects.filter(side_no__regex=r'^\d{3}$')
            else:
                filters = Q(side_no__startswith=first_part, side_no__regex=r'^\d{4}$')
                if second_part:
                    filters |= Q(side_no__startswith=second_part, side_no__regex=r'^\d{4}$')
                routes = Route.objects.filter(filters)

            serialized_routes = self.serialize_routes(routes)
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/rooteeess.html', {
                    'routes': serialized_routes,
                     'company': sc_user,
                     'level': sc_user.level,
                    'name': sc_user.name,
                    'firstname': sc_user.firstname,
                    'lastname': sc_user.lastname,
                    'side': sc_user.side
                })
            return Response({'routes': serialized_routes}, status=status.HTTP_200_OK)
        except Sc.DoesNotExist:
            return self.handle_login_error(buschanges_count, request, 'SC user not found')
    """
    def serialize_routes(self, routes):
        return [{'id': r.id, 'depcity': r.depcity, 'plate_no': r.plate_no, 'side_no': r.side_no} for r in routes]
    def handle_login_error(self, buschanges_count, request, error_message):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/login.html', {'error': error_message, 'buschanges_count': buschanges_count})
        return Response({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)



from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Worker, Ticket, City, Buschange, Route, Bus
class Books(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    throttle_classes = []
    serializer_class = TicketSerializer  # Add this
    #@extend_schema(responses=BookSerializer(many=True))
    #@extend_schema(responses=TicketSerializer(many=True))
    @extend_schema(responses=TicketSerializer(many=True))
    @extend_schema(responses=TicketSerializer(many=True))
    def get_user_from_session(self, request):
        user_id = request.session.get('worker_id')
        return Worker.objects.filter(id=user_id).first() if user_id else None

    def get_daily_total(self, username):
        today = timezone.now().date()
        total = Ticket.objects.filter(
            username=username,
            booked_time__date=today
        ).annotate(
            price_as_float=Cast('price', FloatField())
        ).aggregate(total=Sum('price_as_float'))['total'] or 0
        return total

    def get(self, request):
        worker = self.get_user_from_session(request)

        # --- MANDATORY INTERNATIONAL AUTH & DATA CHECK ---
        # If no worker, or no city/username assigned, block access
        if not worker or not worker.username or not worker.city:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access booking.'
            })
        # --------------------------------------------------

        buschanges_count = Buschange.objects.count()
        username = worker.username.strip()
        city = worker.city
        total_today = self.get_daily_total(username)

        # Unified Terminal Logic
        if city in ['Kality', 'Ayertena', 'Lamberet', 'Autobustera']:
            city = 'Addisababa'

        return render(request, 'users/book.html', {
            'des': City.objects.all(),
            'username': username,
            'city': city,
            'buschanges_count': buschanges_count,
            'total_today': total_today
        })

    def post(self, request):
        worker = self.get_user_from_session(request)

        # --- MANDATORY AUTH CHECK FOR POST ---
        if not worker or not worker.username or not worker.city:
            request.session.flush()
            return render(request, 'users/login.html')

        username = worker.username.strip()
        city = worker.city
        total_today = self.get_daily_total(username)

        if city in ['Kality', 'Ayertena', 'Lamberet', 'Autobustera']:
            city = 'Addisababa'

        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        # Date Validation Logic
        try:
            incoming_date = datetime.strptime(date, '%Y-%m-%d')
            today = timezone.now().date()
            if incoming_date.date() < today:
                raise ValueError("Past date")
        except (ValueError, TypeError):
            return render(request, 'users/book.html', {
                'des': City.objects.all(),
                'city': city,
                'username': username,
                'buschanges_count': Buschange.objects.count(),
                'error': "Invalid date or date is in the past.",
                'total_today': total_today
            })

        # --- Route Search Logic ---
        rout = Route.objects.filter(depcity=depcity, descity=descity, date=date)
        buschanges_count = Buschange.objects.count()
        routes = []
        levels = None

        if rout.exists():
            for route in rout:
                buses = Bus.objects.filter(plate_no=route.plate_no)
                levels = buses.first().level if buses.exists() else None
                total_seats = sum(int(bus.no_seats) for bus in buses) if buses.exists() else 0

                booked_tickets = Ticket.objects.filter(
                    depcity=route.depcity, descity=route.descity,
                    date=route.date, plate_no=route.plate_no
                ).count()

                remaining_seats = total_seats - booked_tickets

                if remaining_seats > 0:
                    routes.append({
                        'route': route,
                        'levels': levels,
                        'remaining_seats': remaining_seats
                    })

        if not routes:
            return render(request, 'users/book.html', {
                'des': City.objects.all(),
                'username': username,
                'buschanges_count': buschanges_count,
                'error': "There is no Travel for this information!",
                'city': city,
                'total_today': total_today
            })

        return render(request, 'users/roo.html', {
            'routes': routes,
            'levels': levels,
            'username': username,
            'buschanges_count': buschanges_count,
            'total_today': total_today
        })





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Buschange, Route, Bus, Ticket
from .serializers import RouteSerializer, BusSerializer
class SelView(APIView):
    #@extend_schema(responses=TicketSerializer(many=True))
    #@extend_schema(responses=TicketSerializer(many=True))
    serializer_class = TicketSerializer  # Add this
    @extend_schema(responses=TicketSerializer(many=True))
    def get(self, request):
        buschanges = Buschange.objects.all()
        buschanges_count = buschanges.count()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/rooote.html', {'buschanges_count': buschanges_count})
        return Response({'buschanges_count': buschanges_count}, status=status.HTTP_200_OK)

    def post(self, request):
        plate = request.data.get('plate')
        side = request.data.get('side')
        first = request.data.get('first')
        last = request.data.get('last')
        phone = request.data.get('phone')
        email = request.data.get('email')
        dep = request.data.get('dep')
        pr = request.data.get('pr')
        da = request.data.get('da')
        des = request.data.get('des')
        gender = request.data.get('gender')
        
        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')
        passenger_type = request.data.get('passenger_type')
        routes = Route.objects.filter(depcity=depcity, descity=descity, date=date, plate_no=plate_no)
        route_info = []
        bus_full = False
        buses = Bus.objects.filter(plate_no=plate_no)
        levels = buses.first().level if buses.exists() else None

        # Initialize variables to avoid UnboundLocalError
        unbooked_seats = []
        booked_seats = set()  # Initialize booked_seats as a set
        total_seats = 0

        for route in routes:
            try:
                bus = Bus.objects.get(plate_no=route.plate_no)
                total_seats = int(bus.no_seats)
                booked_tickets = Ticket.objects.filter(
                    depcity=route.depcity,
                    descity=route.descity,
                    date=route.date,
                    plate_no=route.plate_no
                ).values_list('no_seat', flat=True)

                # Convert to set for faster lookups
                booked_seats = set(int(seat) for seat in booked_tickets if seat)
                booked_seat_count = len(booked_seats)
                remaining_seats = total_seats - booked_seat_count
                unbooked_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_seats]

                if route.plate_no == plate_no and remaining_seats <= 0:
                    bus_full = True
                    route_info.append({
                        'route': route,
                        'levels': levels,
                        'remaining_seats': remaining_seats if remaining_seats > 0 else "Full"
                    })
            except Bus.DoesNotExist:
                continue
        if bus_full:
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/rooote.html', {
                    'error': 'This Bus is Full!',
                    'levels': levels,
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'This Bus is Full!'}, status=status.HTTP_400_BAD_REQUEST)
        serialized_routes = RouteSerializer(routes, many=True).data
        all_seats = list(range(1, total_seats + 1) if total_seats > 0 else [])

        response_data = {
            'routes': serialized_routes,
            'levels': levels,
            'remaining_seats': len(unbooked_seats),
            'unbooked_seats': unbooked_seats,
            'booked_seats': booked_seats,
            'all_seats': all_seats
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/updateticket.html', {
                'routes': serialized_routes,
                'levels': levels,
                'remaining_seats': len(unbooked_seats),
                'unbooked_seats': unbooked_seats,
                'booked_seats': booked_seats,
                'first': first,
                'last': last,
                'pr': pr,
                'da': da,
                'email': email,
                'plate': plate,
                'side': side,
                'phone': phone,
                'gender': gender,
                'passenger_type': passenger_type,
                'all_seats': all_seats
            })
        return Response(response_data, status=status.HTTP_200_OK)


"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from .models import Bus, Route, Ticket, Worker, Buschange
from .serializers import (
    RouteSerializer,
    SeatLookupRequestSerializer,
    SeatInfoResponseSerializer
)
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Seat Management'])
class SeeView(APIView):
    serializer_class = SeatLookupRequestSerializer

    def get_user_from_session(self, request):
        
        user_id = request.session.get('worker_id')
        return Worker.objects.filter(id=user_id).first() if user_id else None
    def get_daily_total(self, username):
        
        today = timezone.now().date()
        total = Ticket.objects.filter(
            username=username,
            booked_time__date=today
        ).annotate(
            price_as_float=Cast('price', FloatField())
        ).aggregate(total=Sum('price_as_float'))['total'] or 0
        return total

    @extend_schema(summary="Check current worker session")
    def get(self, request):
        worker = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION & DATA INTEGRITY CHECK
        if not worker or not worker.username:
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html', {
                    'error': 'Authentication required. Please login to access seat management.'
                })
            return Response({'error': 'User session not found'}, status=status.HTTP_401_UNAUTHORIZED)

        buschanges_count = Buschange.objects.count()
        username = worker.username.strip()
        total_today = self.get_daily_total(username)

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/roo.html', {
                'buschanges_count': buschanges_count,
                'username': username,
                'total_today': total_today
            })

        return Response({
            'username': username,
            'buschanges_count': buschanges_count,
            'total_today': total_today
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Lookup available seats",
        request=SeatLookupRequestSerializer,
        responses={200: SeatInfoResponseSerializer}
    )
    def post(self, request):
        worker = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not worker or not worker.username:
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html')
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        buschanges_count = Buschange.objects.count()
        username = worker.username.strip()
        total_today = self.get_daily_total(username)

        # 1. ROUTE EXISTENCE CHECK
        routes = Route.objects.filter(depcity=depcity, descity=descity, date=date, plate_no=plate_no)

        if not routes.exists():
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/roo.html', {
                    'error': 'No Travel found for this bus configuration.',
                    'username': username,
                    'buschanges_count': buschanges_count,
                    'total_today': total_today
                })
            return Response({'error': 'No Travel found'}, status=status.HTTP_404_NOT_FOUND)

        # 2. BUS REGISTRY CHECK
        bus = Bus.objects.filter(plate_no=plate_no).first()
        if not bus:
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/booker.html', {
                    'error': f'Bus registry error: Plate {plate_no} not found.',
                    'username': username,
                    'buschanges_count': buschanges_count,
                    'total_today': total_today
                })
            return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)

        # 3. SEAT CALCULATION LOGIC
        total_seats = int(bus.no_seats)
        levels = bus.level
        booked_tickets = Ticket.objects.filter(
            depcity=depcity, descity=descity, date=date, plate_no=plate_no
        ).values_list('no_seat', flat=True)

        booked_seats = sorted([int(seat) for seat in booked_tickets if str(seat).isdigit()])
        unbooked_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_seats]

        response_data = {
            'routes': RouteSerializer(routes, many=True).data,
            'levels': levels,
            'remaining_seats': len(unbooked_seats),
            'unbooked_seats': unbooked_seats,
            'booked_seats': booked_seats,
            'all_seats': list(range(1, total_seats + 1)),
            'username': username,
            'buschanges_count': buschanges_count,
            'total_today': total_today
        }

        # 4. RESPONSE DISPATCH
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/booker.html', response_data)
        return Response(response_data, status=status.HTTP_200_OK)
"""


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from .models import Bus, Route, Ticket, Worker, Buschange
from .serializers import (
    RouteSerializer,
    SeatLookupRequestSerializer,
    SeatInfoResponseSerializer
)
@extend_schema(tags=['Seat Management'])
class SeeView(APIView):
    serializer_class = SeatLookupRequestSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('worker_id')
        return Worker.objects.filter(id=user_id).first() if user_id else None

    def get_daily_total(self, username):
        today = timezone.now().date()
        total = Ticket.objects.filter(
            username=username,
            booked_time__date=today
        ).annotate(
            price_as_float=Cast('price', FloatField())
        ).aggregate(total=Sum('price_as_float'))['total'] or 0
        return total

    @extend_schema(summary="Check current worker session")
    def get(self, request):
        worker = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION & DATA INTEGRITY CHECK
        if not worker or not worker.username:
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html', {
                    'error': 'Authentication required. Please login to access seat management.'
                })
            return Response({'error': 'User session not found'}, status=status.HTTP_401_UNAUTHORIZED)

        buschanges_count = Buschange.objects.count()
        username = worker.username.strip()
        total_today = self.get_daily_total(username)

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/roo.html', {
                'buschanges_count': buschanges_count,
                'username': username,
                'total_today': str(total_today)  # <-- CHANGED HERE: Wrap with str()
            })

        return Response({
            'username': username,
            'buschanges_count': buschanges_count,
            'total_today': str(total_today)  # <-- CHANGED HERE: Wrap with str()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Lookup available seats",
        request=SeatLookupRequestSerializer,
        responses={200: SeatInfoResponseSerializer}
    )
    def post(self, request):
        worker = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not worker or not worker.username:
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html')
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        buschanges_count = Buschange.objects.count()
        username = worker.username.strip()
        total_today = self.get_daily_total(username)

        # 1. ROUTE EXISTENCE CHECK
        routes = Route.objects.filter(depcity=depcity, descity=descity, date=date, plate_no=plate_no)

        if not routes.exists():
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/roo.html', {
                    'error': 'No Travel found for this bus configuration.',
                    'username': username,
                    'buschanges_count': buschanges_count,
                    'total_today': str(total_today)  # <-- CHANGED HERE: Wrap with str()
                })
            return Response({'error': 'No Travel found'}, status=status.HTTP_404_NOT_FOUND)

        # 2. BUS REGISTRY CHECK
        bus = Bus.objects.filter(plate_no=plate_no).first()
        if not bus:
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/booker.html', {
                    'error': f'Bus registry error: Plate {plate_no} not found.',
                    'username': username,
                    'buschanges_count': buschanges_count,
                    'total_today': str(total_today)  # <-- CHANGED HERE: Wrap with str()
                })
            return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)

        # 3. SEAT CALCULATION LOGIC
        total_seats = int(bus.no_seats)
        levels = bus.level
        booked_tickets = Ticket.objects.filter(
            depcity=depcity, descity=descity, date=date, plate_no=plate_no
        ).values_list('no_seat', flat=True)

        booked_seats = sorted([int(seat) for seat in booked_tickets if str(seat).isdigit()])
        unbooked_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_seats]

        response_data = {
            'routes': RouteSerializer(routes, many=True).data,
            'levels': levels,
            'remaining_seats': len(unbooked_seats),
            'unbooked_seats': unbooked_seats,
            'booked_seats': booked_seats,
            'all_seats': list(range(1, total_seats + 1)),
            'username': username,
            'buschanges_count': buschanges_count,
            'total_today': str(total_today)  # <-- CHANGED HERE: Wrap with str()
        }

        # 4. RESPONSE DISPATCH
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/booker.html', response_data)
        return Response(response_data, status=status.HTTP_200_OK)



from django.shortcuts import redirect
from rest_framework.views import APIView
class LogoutView(APIView):
    @extend_schema(responses={204: None}, description="Logs out the user and clears session")
    def get(self, request):
        # This removes the 'sc_id' and 'name' from the database and browser
        request.session.flush() 
        # Now that the session is gone, go back to login
        #return redirect('login')
        return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })







"""
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Bus, Sc
from .serializers import BusDeleteActionSerializer, BusDeleteDisplaySerializer
@extend_schema(tags=['Bus & Driver Management'])
class BusDeleteViews(APIView):
    serializer_class = BusDeleteActionSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    def get_filtered_buses(self, sc_user):
        
        side = sc_user.side.strip()
        level = getattr(sc_user, 'level', '1st')
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']

        if not first_part:
            return Bus.objects.none()

        # 1. Geographic Side Filter
        if first_part == '3' or second_part == '3':
            side_filter = Q(sideno__regex=r'^\d{3}$')
        else:
            side_filter = Q(sideno__startswith=first_part) & Q(sideno__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(sideno__startswith=second_part) & Q(sideno__regex=r'^\d{4}$')

        # 2. Level Category Constraint
        target_level = level if level in standard_levels else 'Special Bus'

        return Bus.objects.filter(side_filter & Q(level=target_level))

    @extend_schema(responses={200: BusDeleteDisplaySerializer(many=True)})
    def get(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        buses = self.get_filtered_buses(sc_user)
        data = BusDeleteDisplaySerializer(buses, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busdelet.html', {
                'buses': data,
                'name': sc_user.name,
                'level': getattr(sc_user, 'level', '1st')
            })
        return Response(data)

    @extend_schema(request=BusDeleteActionSerializer)
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        plate_no = request.data.get('plate_no')

        # Security: Only delete if the bus belongs to this user's Side AND Level
        bus_to_delete = self.get_filtered_buses(sc_user).filter(plate_no=plate_no)

        if bus_to_delete.exists():
            bus_to_delete.delete()
            success_msg = f'Bus {plate_no} deleted successfully'
        else:
            success_msg = f'Error: Bus {plate_no} not found or unauthorized'

        # Re-fetch the updated list using the same secure filter
        updated_buses = self.get_filtered_buses(sc_user)
        data = BusDeleteDisplaySerializer(updated_buses, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busdelet.html', {
                'buses': data,
                'company': sc_user,
                'level': sc_user.level,
                'name': sc_user.name,
                'success': success_msg
            })
        return Response({'message': success_msg}, status=status.HTTP_200_OK)
"""


from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

from drf_spectacular.utils import extend_schema

from .models import Bus, Sc
from .serializers import (
    BusDeleteActionSerializer,
    BusDeleteDisplaySerializer
)


@extend_schema(tags=['Bus & Driver Management'])
class BusDeleteViews(APIView):
    serializer_class = BusDeleteActionSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    def get_filtered_buses(self, sc_user):
        side = (sc_user.side or "").strip()
        level = getattr(sc_user, 'level', '1st')

        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']

        if not first_part:
            return Bus.objects.none()

        # 1. Geographic Side Filter
        if first_part == '3' or second_part == '3':
            side_filter = Q(sideno__regex=r'^\d{3}$')
        else:
            side_filter = Q(sideno__startswith=first_part) & Q(sideno__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(sideno__startswith=second_part) & Q(sideno__regex=r'^\d{4}$')

        # 2. Level Category Constraint
        target_level = level if level in standard_levels else 'Special Bus'

        return Bus.objects.filter(side_filter & Q(level=target_level))

    def get_target_level_for_display(self, sc_user):
        level = getattr(sc_user, 'level', '1st')
        standard_levels = ['1st', '2nd', '3rd']
        return level if level in standard_levels else 'Special Bus'

    @extend_schema(responses={200: BusDeleteDisplaySerializer(many=True)})
    def get(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        buses = self.get_filtered_buses(sc_user)
        data = BusDeleteDisplaySerializer(buses, many=True).data

        # ✅ display level should match what buses are filtered with
        target_level = self.get_target_level_for_display(sc_user)

        # ✅ pass company so template can render logo
        # IMPORTANT: Change this line ONLY if logo is not directly on Sc.
        company = sc_user  # <-- if logo is Sc.logo. If it's Sc.company.logo then use: company = sc_user.company

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busdelet.html', {
                'buses': data,
                'name': sc_user.name,
                'level': target_level,
                'company': company,
            })

        return Response(data)

    @extend_schema(request=BusDeleteActionSerializer)
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        plate_no = request.data.get('plate_no')

        # Security: Only delete if the bus belongs to this user's Side AND Level
        bus_to_delete = self.get_filtered_buses(sc_user).filter(plate_no=plate_no)

        if bus_to_delete.exists():
            bus_to_delete.delete()
            success_msg = f'Bus {plate_no} deleted successfully'
        else:
            success_msg = f'Error: Bus {plate_no} not found or unauthorized'

        # Re-fetch updated list using the same secure filter
        updated_buses = self.get_filtered_buses(sc_user)
        data = BusDeleteDisplaySerializer(updated_buses, many=True).data

        target_level = self.get_target_level_for_display(sc_user)

        # ✅ pass company so template can render logo
        company = sc_user  # <-- change to sc_user.company if needed

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busdelet.html', {
                'buses': data,
                'company': company,
                'level': target_level,
                'name': sc_user.name,
                'success': success_msg,
            })

        return Response({'message': success_msg}, status=status.HTTP_200_OK)







from django.db.models import Q, OuterRef, Subquery  # Fixed: Added .models
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Route, Sc, Bus
from .serializers import RoutSerializer

@extend_schema(tags=['Routes & Cities'])
class MyRoute(generics.GenericAPIView):
    queryset = Route.objects.all()
    serializer_class = RoutSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # 1. Authentication Check
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login.'
            })

        # 2. Extract User Side and Level
        side = sc_user.side.strip()
        user_level = getattr(sc_user, 'level', '1st')
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']

        if first_part is None:
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Subquery: Retrieve 'level' from Bus where Bus.sideno == Route.side_no
        bus_level_subquery = Bus.objects.filter(
            sideno=OuterRef('side_no')
        ).values('level')[:1]

        # 4. Define Geographic Side Filter
        if first_part == '3' or second_part == '3':
            side_filter = Q(side_no__regex=r'^\d{3}$')
        else:
            side_filter = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')

        # 5. Determine Target Level (Matching Bus logic)
        target_level = user_level if user_level in standard_levels else 'Special Bus'

        # 6. Final Combined Query
        # Annotate each Route with the level found in the Bus table, then filter
        routes = Route.objects.annotate(
            retrieved_bus_level=Subquery(bus_level_subquery)
        ).filter(
            side_filter & Q(retrieved_bus_level=target_level)
        ).distinct()
        serialized_routes = RoutSerializer(routes, many=True).data
        # 7. Response (HTML or JSON)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/rooteees.html', {
                'routes': serialized_routes,
                 'company': sc_user,           # <--- ADD THIS LINE HERE
                'name': sc_user.name,
                'level': user_level
            })
        return Response(serialized_routes)






















































"""
from django.db.models import Q, OuterRef, Subquery
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Route, Sc, Bus
from .serializers import RoutSerializer, SpecificFilterSerializer
@extend_schema(tags=['Routes & Cities'])
class Specific(generics.GenericAPIView):
    queryset = Route.objects.all()
    serializer_class = RoutSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    def get_filtered_routes(self, sc_user, start_date, end_date):
        
        side = sc_user.side.strip()
        user_level = getattr(sc_user, 'level', '1st')
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']

        if not first_part:
            return None

        # 1. Subquery: Retrieve 'level' from Bus where Bus.sideno == Route.side_no
        bus_level_subquery = Bus.objects.filter(
            sideno=OuterRef('side_no')
        ).values('level')[:1]

        # 2. Determine Target Level
        target_level = user_level if user_level in standard_levels else 'Special Bus'

        # 3. Define Geographic Side Filter (regex logic)
        if first_part == '3' or second_part == '3':
            side_filter = Q(side_no__regex=r'^\d{3}$')
        else:
            side_filter = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')

        # 4. Final Query with Date range and Subquery Level check
        return Route.objects.annotate(
            retrieved_bus_level=Subquery(bus_level_subquery)
        ).filter(
            side_filter,
            Q(date__gte=start_date, date__lte=end_date),
            Q(retrieved_bus_level=target_level)
        ).distinct()

    @extend_schema(
        summary="Filter routes via Query Parameters (GET)",
        parameters=[
            OpenApiParameter(name='from', description="Start Date", required=True, type=str),
            OpenApiParameter(name='to', description="End Date", required=True, type=str),
        ],
        responses={200: RoutSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html', {'error': 'Authentication required.'})
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        start_date = request.query_params.get('from')
        end_date = request.query_params.get('to')

        if not start_date or not end_date:
            error_msg = 'Provide both from and to dates.'
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/specific.html', {'error': error_msg, 'name': sc_user.name})
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        routes = self.get_filtered_routes(sc_user, start_date, end_date)
        if routes is None:
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = RoutSerializer(routes, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/specific.html', {
                'routes': serialized_data,
                'campany': sc_user,
                'name': sc_user.name,
                'level': sc_user.level,
                'from': start_date,
                'to': end_date
            })
        return Response(serialized_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Filter routes via Request Body (POST)",
        request=SpecificFilterSerializer,
        responses={200: RoutSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        start_date = request.data.get('from')
        end_date = request.data.get('to')

        routes = self.get_filtered_routes(sc_user, start_date, end_date)
        if routes is None:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = RoutSerializer(routes, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/specific.html', {
                'routes': serialized_data,
                'campany': sc_user,
                'name': sc_user.name,
                'level': sc_user.level,
                'from': start_date,
                'to': end_date
            })
        return Response(serialized_data, status=status.HTTP_200_OK)
"""

from django.db.models import Q, OuterRef, Subquery
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Route, Sc, Bus
from .serializers import RoutSerializer, SpecificFilterSerializer

@extend_schema(tags=['Routes & Cities'])
class Specific(generics.GenericAPIView):
    queryset = Route.objects.all()
    serializer_class = RoutSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    # NEW: Global helper to make sure company & level are never forgotten
    def get_base_context(self, sc_user):
        return {
            'company': sc_user,  # FIXED: Spelling corrected from 'campany' to 'company'
            'name': sc_user.name,
            'level': sc_user.level,
            'side': sc_user.side
        }

    def get_filtered_routes(self, sc_user, start_date, end_date):
        side = sc_user.side.strip()
        user_level = getattr(sc_user, 'level', '1st')
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']

        if not first_part:
            return None

        bus_level_subquery = Bus.objects.filter(
            sideno=OuterRef('side_no')
        ).values('level')[:1]

        target_level = user_level if user_level in standard_levels else 'Special Bus'

        if first_part == '3' or second_part == '3':
            side_filter = Q(side_no__regex=r'^\d{3}$')
        else:
            side_filter = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')

        return Route.objects.annotate(
            retrieved_bus_level=Subquery(bus_level_subquery)
        ).filter(
            side_filter,
            Q(date__gte=start_date, date__lte=end_date),
            Q(retrieved_bus_level=target_level)
        ).distinct()

    @extend_schema(
        summary="Filter routes via Query Parameters (GET)",
        parameters=[
            OpenApiParameter(name='from', description="Start Date", required=True, type=str),
            OpenApiParameter(name='to', description="End Date", required=True, type=str),
        ],
        responses={200: RoutSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/login.html', {'error': 'Authentication required.'})
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        start_date = request.query_params.get('from')
        end_date = request.query_params.get('to')

        if not start_date or not end_date:
            error_msg = 'Provide both from and to dates.'
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                # FIXED: Logo and level variables are now bundled correctly during validation drops
                context = self.get_base_context(sc_user)
                context['error'] = error_msg
                return render(request, 'users/specific.html', context)
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        routes = self.get_filtered_routes(sc_user, start_date, end_date)
        if routes is None:
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = RoutSerializer(routes, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            context = self.get_base_context(sc_user)
            context.update({
                'routes': serialized_data,
                'from': start_date,
                'to': end_date
            })
            return render(request, 'users/specific.html', context)
        return Response(serialized_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Filter routes via Request Body (POST)",
        request=SpecificFilterSerializer,
        responses={200: RoutSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        start_date = request.data.get('from')
        end_date = request.data.get('to') 
        
        routes = self.get_filtered_routes(sc_user, start_date, end_date)
        if routes is None:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = RoutSerializer(routes, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            context = self.get_base_context(sc_user)
            context.update({
                'routes': serialized_data,
                'from': start_date,
                'to': end_date
            })
            return render(request, 'users/specific.html', context)
        return Response(serialized_data, status=status.HTTP_200_OK)


from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import generics
from django.db.models import Q
from .models import Bus, Worker, Route, Sc
from .serializers import BusSerializer
@extend_schema(tags=['Bus & Driver Management'])
class DriverUpdateViewss(generics.GenericAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')  # Get SC ID from session
        if user_id:
            return Sc.objects.get(id=user_id)
        return None

    def get_sc_names(self):
        sc_instances = Sc.objects.all()
        return [sc.name for sc in sc_instances]

    def get_side_parts(self, side):
        side_parts = side.split('/')
        if len(side_parts) == 1:
            return side_parts[0].strip(), None  # Single part
        elif len(side_parts) == 2:
            return side_parts[0].strip(), side_parts[1].strip()  # Two parts
        else:
            return None, None  # Invalid format

    def get(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        side = sc_user.side.strip()  # Get the side of buses
        first_part, second_part = self.get_side_parts(side)

        if first_part is None:  # Invalid side format
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)
        if first_part == '3' or second_part == '3':
            buses = Worker.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
            buses = Worker.objects.filter(filters)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/driverupdate.html', {
                'name': sc_user.name,
                'side': side,
                'buses': buses
            })
        return Response(BusSerializer(buses, many=True).data)  # Return JSON response

    def post(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        side = sc_user.side.strip()  # Get the side of buses
        first_part, second_part = self.get_side_parts(side)

        if first_part is None:  # Invalid side format
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)
        if first_part == '3' or second_part == '3':
            buses = Worker.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
            buses = Worker.objects.filter(filters)

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/driverupdate.html', {
                'name': sc_user.name,
                'side': side,
                'buses': buses
            })
        return Response(BusSerializer(buses, many=True).data)  # Return JSON response

    def post(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        side = sc_user.side.strip()  # Get the side of buses
        first_part, second_part = self.get_side_parts(side)

        if first_part is None:  # Invalid side format
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)
        if first_part == '3' or second_part == '3':
            buses = Worker.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
            buses = Worker.objects.filter(filters)

        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        username = request.data.get('username')
        new_username = request.data.get('new_username')
        new_phone = request.POST.get('new_phone')
        bus_exists = Worker.objects.filter(plate_no=plate_no).first()
        if bus_exists:
            if Worker.objects.filter(username=new_username).exists():
                return render(request, 'users/driverupdate.html', {
                    'buses': buses,
                    'error': 'This username already exists.',
                })
            if Worker.objects.filter(phone = new_phone).exists():
                return render(request, 'users/driverupdate.html', {
                    'buses': buses,
                    'error': 'This Phone already exists.',
                })
            bus_exists.side_no = side_no
            bus_exists.plate_no = plate_no
            bus_exists.username = new_username
            bus_exists.phone = new_phone
            bus_exists.save()
            sc_user = self.get_user_from_session(request)
            if not sc_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            sc_user = self.get_user_from_session(request)
            if not sc_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            sc_user = self.get_user_from_session(request)
            if not sc_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            sc_user = self.get_user_from_session(request)
            if not sc_user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            side = sc_user.side.strip()  # Get the side of buses
            first_part, second_part = self.get_side_parts(side)

            if first_part is None:  # Invalid side format
                return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)
            if first_part == '3' or second_part == '3':
                buses = Worker.objects.filter(side_no__regex=r'^\d{3}$')
            else:
                filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
                buses = Worker.objects.filter(filters)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/driverupdate.html', {
                    'buses': buses,
                    'success': 'Driver updated successfully.'
                })
        else:
            buses = Bus.objects.filter(filters)
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/driverupdate.html', {
                    'buses': buses,
                    'error_message': 'Bus not found.'
                })
        return Response({'message': 'Request processed successfully'}, status=status.HTTP_200_OK)






"""
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Bus, Sc, Route
from .serializers import BusUpdateActionSerializer, BusTableResponseSerializer
@extend_schema(tags=['Bus & Driver Management'])
class BusUpdateViewss(APIView):
    serializer_class = BusUpdateActionSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)

    def get_buses(self, side, level):
        
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']
        
        if not first_part:
            return None, {'error': 'Invalid side format'}

        # 1. Geographic Side Filter
        if first_part == '3' or second_part == '3':
            side_filter = Q(sideno__regex=r'^\d{3}$')
        else:
            side_filter = Q(sideno__startswith=first_part) & Q(sideno__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(sideno__startswith=second_part) & Q(sideno__regex=r'^\d{4}$')

        # 2. Level Category Filter
        if level in standard_levels:
            final_query = side_filter & Q(level=level)
        else:
            final_query = side_filter & Q(level='Special Bus')

        return Bus.objects.filter(final_query), None

    @extend_schema(responses={200: BusTableResponseSerializer(many=True)})
    def get(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })
        # Retrieve level and filter buses
        level = getattr(sc_user, 'level', '1st')
        buses, error = self.get_buses(sc_user.side, level)
        if error:
            return Response(error, status=400)
        data = BusTableResponseSerializer(buses, many=True).data
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busupdate.html', {
                'buses': data,
                'side': sc_user.side,
                'level': level,
                'name': sc_user.name
            })
        return Response(data)

    @extend_schema(request=BusUpdateActionSerializer, responses={200: BusTableResponseSerializer(many=True)})
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        plate_no = request.data.get('plate_no')
        new_sideno = request.data.get('new_sideno')
        no_seats = request.data.get('no_seats')
        level = getattr(sc_user, 'level', '1st')

        # Synchronize update across both models
        Bus.objects.filter(plate_no=plate_no).update(sideno=new_sideno, no_seats=no_seats)
        Route.objects.filter(plate_no=plate_no).update(side_no=new_sideno)

        # Re-fetch filtered buses using the updated level logic
        buses, _ = self.get_buses(sc_user.side, level)
        data = BusTableResponseSerializer(buses, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busupdate.html', {
                'buses': data,
                'side': sc_user.side,
                'level': level,
                'name': sc_user.name,
                'success': 'Fleet successfully updated!'
            })
        return Response(data, status=200)
"""





from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Bus, Sc, Route
from .serializers import BusUpdateActionSerializer, BusTableResponseSerializer
@extend_schema(tags=['Bus & Driver Management'])
class BusUpdateViewss(APIView):
    serializer_class = BusUpdateActionSerializer
    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None
    def get_side_parts(self, side):
        if not side:
            return None, None
        parts = side.split('/')
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else None)
    #  FIXED INDENTATION: Now properly nested inside the class
    def get_buses(self, side, level):
        first_part, second_part = self.get_side_parts(side)
        standard_levels = ['1st', '2nd', '3rd']
        if not first_part:
            # Safe fallback: return an empty queryset instead of None
            return Bus.objects.none(), {'error': 'Invalid side format'}
        # 1. Geographic Side Filter
        if first_part == '3' or second_part == '3':
            side_filter = Q(sideno__regex=r'^\d{3}$')
        else:
            side_filter = Q(sideno__startswith=first_part) & Q(sideno__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(sideno__startswith=second_part) & Q(sideno__regex=r'^\d{4}$')
        # 2. Level Category Filter
        if level in standard_levels:
            final_query = side_filter & Q(level=level)
        else:
            final_query = side_filter & Q(level='Special Bus')
        return Bus.objects.filter(final_query), None
    @extend_schema(responses={200: BusTableResponseSerializer(many=True)})
    def get(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })
        # Retrieve level and filter buses
        level = getattr(sc_user, 'level', '1st')
        buses, error = self.get_buses(sc_user.side, level)
        if error:
            return Response(error, status=400)

        data = BusTableResponseSerializer(buses, many=True).data

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busupdate.html', {
                'buses': data,
                'side': sc_user.side,
                'level': level,
                'company': sc_user,
                'name': sc_user.name
            })
        return Response(data)

    @extend_schema(request=BusUpdateActionSerializer, responses={200: BusTableResponseSerializer(many=True)})
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        plate_no = request.data.get('plate_no')
        new_sideno = request.data.get('new_sideno')
        no_seats = request.data.get('no_seats')
        level = getattr(sc_user, 'level', '1st')

        # Synchronize update across both models (Bus and Route)
        Bus.objects.filter(plate_no=plate_no).update(sideno=new_sideno, no_seats=no_seats)
        Route.objects.filter(plate_no=plate_no).update(side_no=new_sideno)

        # Re-fetch filtered buses using the updated level logic
        buses, _ = self.get_buses(sc_user.side, level)
        data = BusTableResponseSerializer(buses, many=True).data
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busupdate.html', {
                'buses': data,
                'side': sc_user.side,
                'level': level,
                'company': sc_user,
                'name': sc_user.name,
                'success': 'Fleet successfully updated!'
            })
        return Response(data, status=200)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .models import Worker, City, Buschange, CustomUser # Added CustomUser
from .serializers import WorkerSerializer
@extend_schema(tags=['Bus & Driver Management'])
class Workers(APIView):
    serializer_class = WorkerSerializer

    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to access Worker management.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required for personnel registration.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        if is_html:
            des = City.objects.all()
            return render(request, 'users/worker.html', {
                'des': des,
                'buschanges_count': buschanges_count,
                'username': current_user.username
            })

        workers = Worker.objects.all()
        serializer = WorkerSerializer(workers, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        des = City.objects.all()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION & REGISTRY LOGIC
        serializer = WorkerSerializer(data=request.data)
        context = {
            'des': des,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if serializer.is_valid():
            username_input = serializer.validated_data.get('username')
            phone_input = serializer.validated_data.get('phone')

            # Business Logic: Uniqueness checks
            if Worker.objects.filter(username=username_input).exists():
                context['error'] = 'Registry Conflict: System username already exists.'
            elif Worker.objects.filter(phone=phone_input).exists():
                context['error'] = 'Registry Conflict: Contact phone number already exists.'
            
            if 'error' in context:
                if is_html: return render(request, 'users/worker.html', context)
                return Response({'error': context['error']}, status=status.HTTP_400_BAD_REQUEST)

            # 4. SAVE & SUCCESS RESPONSE
            serializer.save()
            context['success'] = 'Personnel Registry: Worker initialized successfully.'

            if is_html:
                return render(request, 'users/worker.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)

        # 5. HANDLE VALIDATION ERRORS
        context['error'] = serializer.errors
        if is_html:
            return render(request, 'users/worker.html', context)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db.models import Q  # Make sure to import Q if you are using it
from .models import Worker, Sc  # Ensure Sc is imported
@extend_schema(tags=['Bus & Driver Management'])
class WorkerDeleteViews(APIView):
    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')  # Get SC ID from session
        if user_id:
            return Sc.objects.get(id=user_id)
        return None

    def get_side_parts(self, side):
        side_parts = side.split('/')
        if len(side_parts) == 1:
            return side_parts[0].strip(), None  # Single part
        elif len(side_parts) == 2:
            return side_parts[0].strip(), side_parts[1].strip()  # Two parts
        else:
            return None, None  # Invalid format

    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        side = sc_user.side.strip()
        first_part, second_part = self.get_side_parts(side)
        if first_part is None:  # Invalid side format
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)

        if first_part == '3' or second_part == '3':
            driver = Worker.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
            driver = Worker.objects.filter(filters)
        return render(request, 'users/driverdelete.html', {'driver': driver})

    def post(self, request):
        if request.data.get('_method') == 'DELETE':
            plate_no = request.data.get('plate_no')
            side_no = request.data.get('side_no')
            fname = request.data.get('fname')
            lname = request.data.get('lname')
            print(f"Received data: plate_no={plate_no}, side_no={side_no}, fname={fname}, lname={lname}")
            worker_exists = Worker.objects.filter(plate_no=plate_no, side_no=side_no, fname=fname, lname=lname).exists()
            if worker_exists:
                worker = Worker.objects.get(plate_no=plate_no, side_no=side_no, fname=fname, lname=lname)
                print(worker)  # Print the worker object to the console
                worker.delete()
                context = {
                    'driver': Worker.objects.all(),
                    'success': 'Driver Deleted Successfully'
                }
                return self._render_response(request, context, status.HTTP_200_OK)
            context = {
                'driver': Worker.objects.all(),
                'error': 'Driver not found'  # Optional error message
            }
            return self._render_response(request, context, status.HTTP_200_OK)
        context = {
            'driver': Worker.objects.all(),
        }
        return self._render_response(request, context, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def _render_response(self, request, context, http_status):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/driverdelete.html', context)
        return Response(context, status=http_status)












from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .models import Worker, Bus
from .serializers import BusesSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render
from .models import Bus, Sc
from .serializers import BusSerializer
@extend_schema(tags=['Bus & Driver Management'])
class MyDriver(generics.GenericAPIView):
    queryset = Worker.objects.all()

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')  # Get SC ID from session
        if user_id:
            return Sc.objects.get(id=user_id)
        return None
    def get_side_parts(self, side):
        side_parts = side.split('/')
        if len(side_parts) == 1:
            return side_parts[0].strip(), None  # Single part
        elif len(side_parts) == 2:
            return side_parts[0].strip(), side_parts[1].strip()  # Two parts
        else:
            return None, None  # Invalid format

    def get(self, request):
        sc_user = self.get_user_from_session(request)
        if not sc_user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        side = sc_user.side.strip()  # Get the side of buses
        first_part, second_part = self.get_side_parts(side)
        if first_part is None:  # Invalid side format
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)
        if first_part == '3' or second_part == '3':
            buses = Worker.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=first_part) & Q(side_no__regex=r'^\d{4}$')
            if second_part:
                filters |= Q(side_no__startswith=second_part) & Q(side_no__regex=r'^\d{4}$')
            buses = Worker.objects.filter(filters)        

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/mydriver.html', {
                'name': sc_user.name,
                'level': sc_user.level,
                'side': side,
                'buses': buses
            })
        return Response(BusSerializer(buses, many=True).data)  # Return JSON response













from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Bus, Sc
from .serializers import BusSerializer
@extend_schema(tags=['Bus & Driver Management'])
class MyBus(generics.GenericAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    def get_user_from_session(self, request):
        
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_side_parts(self, side):
        
        if not side:
            return None, None
        side_parts = side.split('/')
        if len(side_parts) == 1:
            return side_parts[0].strip(), None
        elif len(side_parts) >= 2:
            return side_parts[0].strip(), side_parts[1].strip()
        return None, None

    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # --- MANDATORY AUTH CHECK ---
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        # --- PREPARE FILTER VARIABLES ---
        side = sc_user.side.strip()
        level = getattr(sc_user, 'level', '1st')  # Retrieve level from sc_user
        first_part, second_part = self.get_side_parts(side)

        if first_part is None:
            return Response({'error': 'Invalid side format'}, status=status.HTTP_400_BAD_REQUEST)

        # --- FILTERING LOGIC ---
        # Define the category groups based on your system requirements
        standard_levels = ['1st', '2nd', '3rd']

        # 1. Start with the Side Number logic
        if first_part == '3' or second_part == '3':
            side_filter = Q(sideno__regex=r'^\d{3}$')
        else:
            side_filter = Q(sideno__startswith=first_part) & Q(sideno__regex=r'^\d{4}$')
            if second_part:
                side_filter |= Q(sideno__startswith=second_part) & Q(sideno__regex=r'^\d{4}$')

        # 2. Add the Level constraint to the existing filter
        # If the user is in a standard level, they see buses from that specific standard level group
        if level in standard_levels:
            final_query = side_filter & Q(level=level)
        else:
            # If the user is 'Special Bus', they only see buses marked as 'Special Bus'
            final_query = side_filter & Q(level='Special Bus')

        buses = Bus.objects.filter(final_query)

        # --- RESPONSE ---
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/mybus.html', {
                'company': sc_user,           # <--- ADD THIS LINE HERE
                'name': sc_user.name,
                'side': side,
                'level': level,
                'buses': buses
            })
        serializer = BusSerializer(buses, many=True)
        return Response(serializer.data)



from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import render
from django.db.models import Q, OuterRef, Subquery
from .models import Ticket, Route, Sc, Bus
from .serializers import (TicketSearchRequestSerializer, RoutSerializer, TicketNotFoundErrorSerializer)
@extend_schema(tags=['Booking & Tickets'])
class ShowTicketsViewss(APIView):
    serializer_class = TicketSearchRequestSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    @extend_schema(summary="Get the ticket search page")
    def get(self, request):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        return render(request, 'users/ourticketoche.html', {'name': sc_user.name})

    @extend_schema(
        summary="Search tickets (API & Web)",
        request=TicketSearchRequestSerializer,
        responses={
            200: TicketSearchRequestSerializer(many=True),
            404: TicketNotFoundErrorSerializer
        }
    )
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return self.handle_html_post(request, sc_user)
        else:
            return self.handle_json_request(request, sc_user)

    def handle_html_post(self, request, sc_user):
        plate_no = request.POST.get('plate_no')
        side_no = request.POST.get('side_no')
        date = request.POST.get('date')
        depcity = request.POST.get('depcity')
        descity = request.POST.get('descity')

        tickets = Ticket.objects.filter(
            plate_no=plate_no,
            side_no=side_no,
            date=date,
            depcity=depcity,
            descity=descity
        )

        if tickets.exists():
            return render(request, 'users/ourticketoche.html', {
                'route': tickets,
                'name': sc_user.name,
                'company': sc_user,
                'level': sc_user.level
            })
        else:
            return self.handle_no_tickets(request, sc_user)

    def handle_no_tickets(self, request, sc_user):
        side_parts = [s.strip() for s in sc_user.side.split('/')]
        user_level = getattr(sc_user, 'level', '1st')
        standard_levels = ['1st', '2nd', '3rd']

        # 1. Bus level subquery configuration
        bus_level_subquery = Bus.objects.filter(
            sideno=OuterRef('side_no')
        ).values('level')[:1]

        # 2. Dynamic side rule logic
        if '3' in side_parts:
            side_filter = Q(side_no__regex=r'^\d{3}$')
        else:
            side_filter = Q(side_no__startswith=side_parts[0]) & Q(side_no__regex=r'^\d{4}$')
            if len(side_parts) > 1:
                side_filter |= Q(side_no__startswith=side_parts[1]) & Q(side_no__regex=r'^\d{4}$')

        # 3. Determine target bus logic level
        target_level = user_level if user_level in standard_levels else 'Special Bus'

        # 4. Fetch matching routes via annotation fallback
        routes = Route.objects.annotate(
            retrieved_bus_level=Subquery(bus_level_subquery)
        ).filter(
            side_filter & Q(retrieved_bus_level=target_level)
        ).distinct()

        return render(request, 'users/rooteees.html', {
            'error': 'No booked tickets found',
            'routes': self.serialize_routes(routes),
            'company': sc_user,
            'name': sc_user.name,
            'level': user_level
        })
    def serialize_routes(self, routes):
        return [
            {
                'id': r.id,
                'depcity': r.depcity,
                'descity': r.descity,
                'date': r.date,
                'plate_no': r.plate_no,
                'side_no': r.side_no,
            } for r in routes
        ]
    def handle_json_request(self, request, sc_user):
        plate_no = request.data.get('plate_no')
        date = request.data.get('date')
        tickets = Ticket.objects.filter(plate_no=plate_no, date=date)
        if tickets.exists():
            return Response(list(tickets.values()), status=200)
        return Response({"error": "No tickets found"}, status=404)



"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db.models import Q
from .models import Ticket, Route, Sc
from .serializers import (TicketSearchRequestSerializer, AvailableRouteSerializer, TicketNotFoundErrorSerializer)
@extend_schema(tags=['Booking & Tickets'])
class ShowTicketsViewss(APIView):
    serializer_class = TicketSearchRequestSerializer
    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None
    @extend_schema(summary="Get the ticket search page")
    def get(self, request):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        return render(request, 'users/ourticketoche.html', {'name': sc_user.name})

    @extend_schema(
        summary="Search tickets (API & Web)",
        request=TicketSearchRequestSerializer,
        responses={
            200: TicketSearchRequestSerializer(many=True),
            404: TicketNotFoundErrorSerializer
        }
    )
    def post(self, request):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTHENTICATION CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return self.handle_html_post(request, sc_user)
        else:
            return self.handle_json_request(request, sc_user)

    def handle_html_post(self, request, sc_user):
        plate_no = request.POST.get('plate_no')
        side_no = request.POST.get('side_no')
        date = request.POST.get('date')
        depcity = request.POST.get('depcity')
        descity = request.POST.get('descity')

        tickets = Ticket.objects.filter(
            plate_no=plate_no,
            side_no=side_no,
            date=date,
            depcity=depcity,
            descity=descity
        )

        if tickets.exists():
            return render(request, 'users/ourticketoche.html', {
                'route': tickets,
                'name': sc_user.name
            })
        else:
            return self.handle_no_tickets(request, sc_user)
    def handle_no_tickets(self, request, sc_user):
        # We use the sc_user passed from the post/get method
        side_parts = [s.strip() for s in sc_user.side.split('/')]
        
        if '3' in side_parts:
            routes = Route.objects.filter(side_no__regex=r'^\d{3}$')
        else:
            filters = Q(side_no__startswith=side_parts[0])
            if len(side_parts) > 1:
                filters |= Q(side_no__startswith=side_parts[1])
            routes = Route.objects.filter(filters)

        return render(request, 'users/rooteees.html', {
            'error': 'No booked tickets found',
            'routes': self.serialize_routes(routes),
            'name': sc_user.name
        })

    def serialize_routes(self, routes):
        return [
            {
                'id': r.id,
                'depcity': r.depcity,
                'descity': r.descity,
                'date': r.date,
                'plate_no': r.plate_no,
                'side_no': r.side_no,
            } for r in routes
        ]

    def handle_json_request(self, request, sc_user):
        plate_no = request.data.get('plate_no')
        date = request.data.get('date')

        tickets = Ticket.objects.filter(plate_no=plate_no, date=date)

        if tickets.exists():
            return Response(list(tickets.values()), status=200)
        return Response({"error": "No tickets found"}, status=404)
"""



from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render
from .models import Bus, Sc
from .serializers import BusSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Bus & Driver Management'])
class BusInsertView(generics.GenericAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    # FIXED: Added company and level directly into the core context generator
    def get_context_data(self, sc_user):
        sc_instances = Sc.objects.all()
        return {
            'company': sc_user,               # Added for the Logo context
            'level': sc_user.level,           # Added for the Level Badge context
            'name': sc_user.name,
            'side': sc_user.side,
            'names': [sc.name for sc in sc_instances]
        }

    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTH CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        # Now properly contains 'company' and 'level'
        context = self.get_context_data(sc_user)
        return render(request, 'users/Businsert.html', context)

    def post(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTH CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        data = request.data.copy()

        level = getattr(sc_user, 'level', '1st')

        data['level'] = level
        data['owner_sc'] = sc_user.id
        data['name'] = sc_user.name

        raw_input = data.get('plate_no', '').strip().upper()
        clean_input = raw_input.replace('ET-', '').replace('ET', '').replace(' ', '').replace('-', '')
        data['plate_no'] = f"ET-{clean_input}" if clean_input else raw_input

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            plate_no = serializer.validated_data['plate_no']
            sideno = serializer.validated_data['sideno']

            if Bus.objects.filter(plate_no=plate_no).exists():
                return self.handle_error(request, sc_user, f'Plate number {plate_no} already exists.')

            standard_levels = ['1st', '2nd', '3rd']
            if (
                (level in standard_levels and Bus.objects.filter(sideno=sideno, level__in=standard_levels).exists()) or
                (level == 'Special Bus' and Bus.objects.filter(sideno=sideno, level='Special Bus').exists())
            ):
                return self.handle_error(request, sc_user, f'Side number "{sideno}" is already registered for this level category.')

            serializer.save()
            return self.handle_success(request, sc_user, f'Bus {plate_no} registered successfully.')

        return self.handle_error(request, sc_user, serializer.errors)

    def handle_success(self, request, sc_user, message):
        context = self.get_context_data(sc_user)
        context['success'] = message
        return render(request, 'users/Businsert.html', context)

    # FIXED: Level and company info are now always injected regardless of error type
    def handle_error(self, request, sc_user, error):
        context = self.get_context_data(sc_user)

        if isinstance(error, dict):
            error_list = [f"{(field or '').replace('_', ' ').title()}: {msgs[0]}" for field, msgs in error.items()]
            context['errors'] = ", ".join(error_list)
        else:
            context['errors'] = str(error)

        return render(request, 'users/Businsert.html', context)





"""
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render
from .models import Bus, Sc
from .serializers import BusSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Bus & Driver Management'])
class BusInsertView(generics.GenericAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

    def get_user_from_session(self, request):
        
        user_id = request.session.get('sc_id')
        return Sc.objects.filter(id=user_id).first() if user_id else None

    def get_context_data(self, sc_user):
        
        sc_instances = Sc.objects.all()
        return {
            'name': sc_user.name,
            'side': sc_user.side,
            'names': [sc.name for sc in sc_instances]
        }

    def get(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTH CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Authentication required. Please login to access this page.'
            })

        context = self.get_context_data(sc_user)
        return render(request, 'users/Businsert.html', context)

    def post(self, request, *args, **kwargs):
        sc_user = self.get_user_from_session(request)

        # MANDATORY AUTH CHECK
        if not sc_user or not getattr(sc_user, 'name', None):
            request.session.flush()
            return render(request, 'users/login.html')

        data = request.data.copy()

        # 1. DEFINE VARIABLE FIRST (Prevents NameError)
        # Pull level from the session-based sc_user
        level = getattr(sc_user, 'level', '1st')

        # 2. INJECT DATA FOR SERIALIZER
        data['level'] = level
        data['owner_sc'] = sc_user.id
        data['name'] = sc_user.name

        # Plate Number Formatting (International Standard ET-XXXX)
        raw_input = data.get('plate_no', '').strip().upper()
        clean_input = raw_input.replace('ET-', '').replace('ET', '').replace(' ', '').replace('-', '')
        data['plate_no'] = f"ET-{clean_input}" if clean_input else raw_input

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            plate_no = serializer.validated_data['plate_no']
            sideno = serializer.validated_data['sideno']

            # 3. PLATE DUPLICATE CHECK
            if Bus.objects.filter(plate_no=plate_no).exists():
                return self.handle_error(request, sc_user, f'Plate number {plate_no} already exists.')

            # 4. SIDE NUMBER CATEGORY VALIDATION
            # Standard levels (1st, 2nd, 3rd) conflict with each other.
            # Special Bus only conflicts with other Special Bus entries.
            standard_levels = ['1st', '2nd', '3rd']
            
            if (
                (level in standard_levels and Bus.objects.filter(sideno=sideno, level__in=standard_levels).exists()) or
                (level == 'Special Bus' and Bus.objects.filter(sideno=sideno, level='Special Bus').exists())
            ):
                return self.handle_error(request, sc_user, f'Side number "{sideno}" is already registered for this level category.')

            serializer.save()
            return self.handle_success(request, sc_user, f'Bus {plate_no} registered successfully.')

        return self.handle_error(request, sc_user, serializer.errors)

    def handle_success(self, request, sc_user, message):
        
        context = self.get_context_data(sc_user)
        context['success'] = message
        context['name'] = sc_user.name
        context['side'] = sc_user.side
        context['level'] = sc_user.level
        context['company'] = sc_user
        return render(request, 'users/Businsert.html', context)

    def handle_error(self, request, sc_user, error):
        
        context = self.get_context_data(sc_user)
        if isinstance(error, dict):
            error_list = [f"{field.replace('_', ' ').title()}: {msgs[0]}" for field, msgs in error.items()]
            context['errors'] = ", ".join(error_list)
        else:
            context['errors'] = str(error)
            context['name'] = sc_user.name
            context['side'] = sc_user.side
            context['level'] = sc_user.level
            context['company'] = sc_user
        return render(request, 'users/Businsert.html', context)

"""


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from .models import CustomUser, Sc
from .serializers import ForgotPasswordSerializer
@extend_schema(tags=['Authentication'])
class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer
    @extend_schema(summary="Get forgot password page")
    def get(self, request):
        return render(request, 'users/forgot_password.html')
    @extend_schema(
        summary="Reset password and send via email",
        request=ForgotPasswordSerializer
    )
    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        role = request.data.get('role')
        error_message = None
        user_obj = None
        if role == 'user':
            user_obj = CustomUser.objects.filter(username=username_or_email).first() or \
                       CustomUser.objects.filter(email=username_or_email).first()
        elif role == 'sc':
            user_obj = Sc.objects.filter(username=username_or_email).first() or \
                       Sc.objects.filter(email=username_or_email).first()
        if user_obj:
            new_password = get_random_string(length=12)
            if role == 'user':
                user_obj.set_password(new_password)
            else:
                user_obj.password = make_password(new_password)

            user_obj.save()
            try:
                send_mail(
                    'Password Reset Request',
                    f'Hello, your new temporary password is: {new_password}\n'
                    f'Please login and change it immediately.',
                    'teklemariammossie1@gmail.com',
                    [user_obj.email],
                    fail_silently=False,
                )
                success_msg = "Password reset successfully. Check your email."
                return self._handle_response(request, {"message": success_msg}, status.HTTP_200_OK)
            except Exception as e:
                error_message = "Email could not be sent. Please contact support."
        else:
            error_message = f"No {role} found with that username or email."

        return self._handle_response(request, {"error": error_message}, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/forgot_password.html', context)
        return Response(context, status=status_code)









from django.shortcuts import render
from django.views import View
class MainPageView(View):  # Your view class
    def get(self, request):
        print("MainPageView called")  # Debugging line
        return render(request, 'users/index.html')  # Ensure this path is correct






from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .models import Ticket, City, Bus, Route, Worker  # Ensure Worker is imported
from .serializers import TicketSerializer, RouteSerializer
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from rest_framework import status
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['Booking & Tickets'])
class AgentBookingViews(APIView):
    serializer_class = TicketSerializer

    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/booker.html', {'des': des})
        return Response({'cities': [city.depcity for city in des]})

    def post(self, request):
        # 1. Retrieve Data Lists
        firstnames = request.data.getlist('firstname[]')
        emails = request.data.getlist('email[]')
        genders = request.data.getlist('gender[]')
        lastnames = request.data.getlist('lastname[]')
        phones = request.data.getlist('phone[]')
        prices = request.data.getlist('price[]')
        side_nos = request.data.getlist('side_no[]')
        plate_nos = request.data.getlist('plate_no[]')
        usernames = request.data.getlist('username[]')
        dates = request.data.getlist('date[]')
        no_seats = request.data.getlist('no_seat[]')
        depcitys = request.data.getlist('depcity[]')
        descitys = request.data.getlist('descity[]')
        prs = request.data.getlist('pr[]')
        das = request.data.getlist('da[]')

        # 2. Total Price Calculation
        try:
            total_price = sum(float(price) for price in prices)
            if prs:
                total_price -= sum(float(p) for p in prs)
        except (ValueError, TypeError):
            total_price = 0

        min_length = min(
            len(firstnames), len(lastnames), len(emails), len(genders),
            len(phones), len(prices), len(side_nos), len(plate_nos),
            len(depcitys), len(descitys), len(dates), len(no_seats)
        )

        used_seats = set()
        tickets = []
        fname = ""
        lname = ""
        level = "Standard"

        try:
            with transaction.atomic():
                for i in range(min_length):
                    current_seat = no_seats[i]
                    current_date = dates[i]
                    alt_date = das[i] if i < len(das) else None
                    dep = depcitys[i]
                    des = descitys[i]
                    plate = plate_nos[i]
                    current_user = usernames[i] if i < len(usernames) else ""

                    # --- ROUTE & BUS VALIDATION ---
                    routes = Route.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate)
                    bus = Bus.objects.filter(plate_no=plate).first()

                    if not bus:
                        return Response({'error': f'Bus {plate} not found'}, status=404)

                    # --- PREPARE ERROR CONTEXT ---
                    total_seats = int(bus.no_seats)
                    booked_in_db = Ticket.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate).values_list('no_seat', flat=True)
                    booked_seats_list = list(set(int(s) for s in booked_in_db if s))
                    unbooked_seats = [s for s in range(1, total_seats + 1) if s not in booked_seats_list]

                    error_context = {
                        'des': City.objects.all(),
                        'routes': RouteSerializer(routes, many=True).data,
                        'levels': bus.level,
                        'remaining_seats': total_seats - len(booked_seats_list),
                        'unbooked_seats': unbooked_seats,
                        'booked_seats': booked_seats_list,
                        'all_seats': list(range(1, total_seats + 1)),
                    }

                    # --- VALIDATION: SEAT SELECTION ---
                    if current_seat in used_seats or int(current_seat) in booked_seats_list:
                        error_msg = f'Seat {current_seat} already selected.'
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            return render(request, 'users/booker.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- VALIDATION: ALREADY BOOKED CHECK ---
                    already_booked = Ticket.objects.filter(
                        firstname=firstnames[i],
                        lastname=lastnames[i],
                        depcity=dep,
                        descity=des
                    ).filter(Q(date=current_date) | Q(date=alt_date)).exists()

                    if already_booked:
                        error_msg = f"Person already booked: {firstnames[i]} {lastnames[i]} for {current_date}{f' or {alt_date}' if alt_date and alt_date != 'None' else ''}."
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            return render(request, 'users/booker.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- SAVE TICKET ---
                    used_seats.add(current_seat)
                    level = bus.level if bus else "Standard"

                    validated_data = {
                        'firstname': firstnames[i],
                        'lastname': lastnames[i],
                        'phone': phones[i],
                        'price': prices[i],
                        'side_no': side_nos[i],
                        'plate_no': plate,
                        'date': current_date,
                        'email': emails[i],
                        'gender': genders[i],
                        'depcity': dep,
                        'descity': des,
                        'username': current_user,
                        'no_seat': current_seat,
                    }
                    
                    ticket_instance = Ticket.objects.create(**validated_data)
                    tickets.append(ticket_instance)

                    # Lookup Agent Name for the context
                    if current_user:
                        worker = Worker.objects.filter(username=current_user).first()
                        if worker:
                            fname = worker.fname
                            lname = worker.lname

                # --- DELETE EXISTING TICKETS FOR DA (Transfer Logic) ---
                if prs:
                    for i in range(min_length):
                        if i < len(das):
                            Ticket.objects.filter(
                                firstname=firstnames[i],
                                lastname=lastnames[i],
                                date=das[i],
                                depcity=depcitys[i],
                                descity=descitys[i]
                            ).delete()

            # --- SUCCESS RESPONSES ---
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                context = {
                    'success': 'Ticket(s) booked successfully!',
                    'tickets': tickets,
                    'total_price': total_price,
                    'level': level,
                    'fname': fname,
                    'lname': lname
                }
                if not usernames or not usernames[0]:
                    return render(request, 'users/payment.html', context)
                else:
                    return render(request, 'users/myticket.html', context)

            serializer = TicketSerializer(tickets, many=True)
            return Response({'message': 'Booking successful.', 'tickets': serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .models import Ticket, City, Bus, Route, Worker
from .serializers import TicketSerializer, RouteSerializer
from django.db import transaction
from django.db.models import Q, Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from django.conf import settings
from rest_framework import status
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['Booking & Tickets'])
class TicketBookingViews(APIView):
    serializer_class = TicketSerializer

    def get_user_from_session(self, request):
        user_id = request.session.get('worker_id')
        if user_id:
            try:
                return Worker.objects.get(id=user_id)
            except Worker.DoesNotExist:
                return None
        return None

    def get_daily_total(self, username):
        today = timezone.now().date()
        total = Ticket.objects.filter(
            username=username,
            booked_time__date=today
        ).annotate(
            price_as_float=Cast('price', FloatField())
        ).aggregate(total=Sum('price_as_float'))['total'] or 0
        return total

    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/ticket.html', {'des': des})
        return Response({'cities': [city.depcity for city in des]})

    def post(self, request):
        # 1. Retrieve Data Lists
        firstnames = request.data.getlist('firstname[]')
        emails = request.data.getlist('email[]')
        genders = request.data.getlist('gender[]')
        passenger_types = request.data.getlist('passenger_type[]')
        lastnames = request.data.getlist('lastname[]')
        phones = request.data.getlist('phone[]')
        prices = request.data.getlist('price[]')
        side_nos = request.data.getlist('side_no[]')
        plate_nos = request.data.getlist('plate_no[]')
        usernames = request.data.getlist('username[]')
        dates = request.data.getlist('date[]')
        no_seats = request.data.getlist('no_seat[]')
        depcitys = request.data.getlist('depcity[]')
        descitys = request.data.getlist('descity[]')
        prs = request.data.getlist('pr[]')
        das = request.data.getlist('da[]')

        # 2. Total Price Calculation
        try:
            total_price = sum(float(price) for price in prices)
            if prs:
                total_price -= sum(float(p) for p in prs)
        except (ValueError, TypeError):
            total_price = 0

        min_length = min(
            len(firstnames), len(lastnames), len(emails), len(genders),
            len(phones), len(prices), len(side_nos), len(plate_nos),
            len(depcitys), len(descitys), len(dates), len(no_seats), len(passenger_types)
        )

        used_seats = set()
        tickets = []
        fname = ""
        lname = ""
        level = "Standard"
        try:
            with transaction.atomic():
                for i in range(min_length):
                    current_seat = no_seats[i]
                    current_date = dates[i]
                    alt_date = das[i] if i < len(das) else None
                    dep = depcitys[i]
                    des = descitys[i]
                    plate = plate_nos[i]
                    current_user = usernames[i] if i < len(usernames) else ""

                    # --- ROUTE & BUS VALIDATION ---
                    routes = Route.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate)
                    bus = Bus.objects.filter(plate_no=plate).first()

                    if not bus:
                        return Response({'error': f'Bus {plate} not found'}, status=404)

                    # --- PREPARE ERROR CONTEXT ---
                    total_seats = int(bus.no_seats)
                    booked_in_db = Ticket.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate).values_list('no_seat', flat=True)
                    booked_seats_list = list(set(int(s) for s in booked_in_db if s))
                    unbooked_seats = [s for s in range(1, total_seats + 1) if s not in booked_seats_list]

                    error_context = {
                        'des': City.objects.all(),
                        'routes': RouteSerializer(routes, many=True).data,
                        'levels': bus.level,
                        'remaining_seats': total_seats - len(booked_seats_list),
                        'unbooked_seats': unbooked_seats,
                        'booked_seats': booked_seats_list,
                        'all_seats': list(range(1, total_seats + 1)),
                    }

                    # --- VALIDATION: SEAT SELECTION ---
                    seat_is_taken = current_seat in used_seats or int(current_seat) in booked_seats_list

                    if seat_is_taken:
                        error_msg = f'Seat {current_seat} already selected.'
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            if current_user:
                                #worker_obj = Worker.objects.filter(username=current_user).first()
                                #error_context['username'] = worker_obj
                                error_context['username'] = current_user
                                error_context['total_today'] = self.get_daily_total(current_user)
                                return render(request, 'users/booker.html', error_context, status=400)
                            else:
                                return render(request, 'users/ticket.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- VALIDATION: ALREADY BOOKED CHECK ---
                    already_booked = Ticket.objects.filter(
                        firstname=firstnames[i],
                        lastname=lastnames[i],
                        depcity=dep,
                        descity=des
                    ).filter(Q(date=current_date) & Q(date=alt_date)).exists()

                    if already_booked:
                        error_msg = f"Person already booked: {firstnames[i]} {lastnames[i]} for {current_date}{f' or {alt_date}' if alt_date and alt_date != 'None' else ''}."
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            if current_user:
                                #worker_obj = Worker.objects.filter(username=current_user).first()
                                #error_context['username'] = worker_obj
                                error_context['username'] = current_user
                                error_context['total_today'] = self.get_daily_total(current_user)
                                return render(request, 'users/booker.html', error_context, status=400)
                            else:
                                return render(request, 'users/ticket.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- SAVE TICKET ---
                    used_seats.add(current_seat)
                    level = bus.level if bus else "Standard"

                    validated_data = {
                        'firstname': firstnames[i],
                        'lastname': lastnames[i],
                        'phone': phones[i],
                        'price': prices[i],
                        'side_no': side_nos[i],
                        'plate_no': plate,
                        'date': current_date,
                        'email': emails[i],
                        'gender': genders[i],
                        'passenger_type': passenger_types[i],
                        'depcity': dep,
                        'descity': des,
                        'username': current_user,
                        'no_seat': current_seat,
                    }
                    ticket_instance = Ticket.objects.create(**validated_data)
                    tickets.append(ticket_instance)
                    if current_user:
                        worker = Worker.objects.filter(username=current_user).first()
                        if worker:
                            fname = worker.fname
                            lname = worker.lname

                # --- DELETE EXISTING TICKETS FOR DA (Transfer Logic) ---
                if prs:
                    for i in range(min_length):
                        if i < len(das):
                            Ticket.objects.filter(
                                firstname=firstnames[i],
                                lastname=lastnames[i],
                                date=das[i],
                                depcity=depcitys[i],
                                descity=descitys[i]
                            ).delete()
            bus_name = bus.name if bus else "Operator Name"

            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                context = {
                    'success': 'Ticket(s) booked successfully!',
                    'tickets': tickets,
                    'total_price': total_price,
                    'level': level,
                    'name': bus_name,
                    'fname': fname,
                    'lname': lname
                }
                if not usernames or not usernames[0]:
                    return render(request, 'users/payment.html', context)
                else:
                    return render(request, 'users/myticket.html', context)
            serializer = TicketSerializer(tickets, many=True)
            return Response({'message': 'Booking successful.', 'tickets': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""




import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.db import transaction
from django.db.models import Q, Sum, FloatField
from django.db.models.functions import Cast
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .models import Ticket, City, Bus, Route, Worker
from .serializers import TicketSerializer, RouteSerializer
@extend_schema(tags=['Booking & Tickets'])
class TicketBookingViews(APIView):
    serializer_class = TicketSerializer
    def get_user_from_session(self, request):
        user_id = request.session.get('worker_id')
        if user_id:
            try:
                return Worker.objects.get(id=user_id)
            except Worker.DoesNotExist:
                return None
        return None

    def get_daily_total(self, username):
        today = timezone.now().date()
        total = Ticket.objects.filter(
            username=username,
            booked_time__date=today
        ).annotate(
            price_as_float=Cast('price', FloatField())
        ).aggregate(total=Sum('price_as_float'))['total'] or 0
        return total

    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/ticket.html', {'des': des})
        return Response({'cities': [city.depcity for city in des]})

    def post(self, request):
        # 1. Retrieve Data Lists
        firstnames = request.data.getlist('firstname[]')
        emails = request.data.getlist('email[]')
        genders = request.data.getlist('gender[]')
        passenger_types = request.data.getlist('passenger_type[]')
        lastnames = request.data.getlist('lastname[]')
        phones = request.data.getlist('phone[]')
        prices = request.data.getlist('price[]')
        side_nos = request.data.getlist('side_no[]')
        plate_nos = request.data.getlist('plate_no[]')
        usernames = request.data.getlist('username[]')
        dates = request.data.getlist('date[]')
        no_seats = request.data.getlist('no_seat[]')
        depcitys = request.data.getlist('depcity[]')
        descitys = request.data.getlist('descity[]')
        prs = request.data.getlist('pr[]')
        das = request.data.getlist('da[]')

        # 2. Total Price & Recovery Calculation Adjustment
        try:
            total_price_base = sum(float(price) for price in prices if price)
            total_prs = sum(float(p) for p in prs if p) if prs else 0.0

            if total_prs > total_price_base:
                # Scenario: Previous value is greater than new ticket cost -> Recovery Mode
                total_price = total_prs - total_price_base
                is_recovery = True
            else:
                # Scenario: Standard booking or paying remaining differences
                total_price = total_price_base - total_prs
                is_recovery = False
        except (ValueError, TypeError):
            total_price = 0
            is_recovery = False

        min_length = min(
            len(firstnames), len(lastnames), len(emails), len(genders),
            len(phones), len(prices), len(side_nos), len(plate_nos),
            len(depcitys), len(descitys), len(dates), len(no_seats), len(passenger_types)
        )

        used_seats = set()
        tickets = []
        fname = ""
        lname = ""
        level = "Standard"
        bus_name = "Operator Name"

        try:
            with transaction.atomic():
                for i in range(min_length):
                    current_seat = no_seats[i]
                    current_date = dates[i]
                    alt_date = das[i] if i < len(das) else None
                    dep = depcitys[i]
                    des = descitys[i]
                    plate = plate_nos[i]
                    current_user = usernames[i] if i < len(usernames) else ""

                    # --- ROUTE & BUS VALIDATION ---
                    routes = Route.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate)
                    bus = Bus.objects.filter(plate_no=plate).first()

                    if not bus:
                        return Response({'error': f'Bus {plate} not found'}, status=404)

                    bus_name = bus.name if bus else "Operator Name"
                    total_seats = int(bus.no_seats)
                    booked_in_db = Ticket.objects.filter(depcity=dep, descity=des, date=current_date, plate_no=plate).values_list('no_seat', flat=True)
                    booked_seats_list = list(set(int(s) for s in booked_in_db if s))
                    unbooked_seats = [s for s in range(1, total_seats + 1) if s not in booked_seats_list]

                    error_context = {
                        'des': City.objects.all(),
                        'routes': RouteSerializer(routes, many=True).data,
                        'levels': bus.level,
                        'remaining_seats': total_seats - len(booked_seats_list),
                        'unbooked_seats': unbooked_seats,
                        'booked_seats': booked_seats_list,
                        'all_seats': list(range(1, total_seats + 1)),
                    }

                    # --- VALIDATION: SEAT SELECTION ---
                    seat_is_taken = current_seat in used_seats or int(current_seat) in booked_seats_list

                    if seat_is_taken:
                        error_msg = f'Seat {current_seat} already selected.'
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            if current_user:
                                error_context['username'] = current_user
                                error_context['total_today'] = self.get_daily_total(current_user)
                                return render(request, 'users/booker.html', error_context, status=400)
                            else:
                                return render(request, 'users/ticket.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- VALIDATION: ALREADY BOOKED CHECK ---
                    already_booked = Ticket.objects.filter(
                        firstname=firstnames[i],
                        lastname=lastnames[i],
                        depcity=dep,
                        descity=des
                    ).filter(Q(date=current_date) & Q(date=alt_date)).exists()

                    if already_booked:
                        error_msg = f"Person already booked: {firstnames[i]} {lastnames[i]} for {current_date}{f' or {alt_date}' if alt_date and alt_date != 'None' else ''}."
                        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                            error_context['error'] = error_msg
                            if current_user:
                                error_context['username'] = current_user
                                error_context['total_today'] = self.get_daily_total(current_user)
                                return render(request, 'users/booker.html', error_context, status=400)
                            else:
                                return render(request, 'users/ticket.html', error_context, status=400)
                        return Response({'error': error_msg}, status=400)

                    # --- SAVE TICKET ---
                    used_seats.add(current_seat)
                    level = bus.level if bus else "Standard"

                    validated_data = {
                        'firstname': firstnames[i],
                        'lastname': lastnames[i],
                        'phone': phones[i],
                        'price': prices[i],
                        'side_no': side_nos[i],
                        'plate_no': plate,
                        'date': current_date,
                        'email': emails[i],
                        'gender': genders[i],
                        'passenger_type': passenger_types[i],
                        'depcity': dep,
                        'descity': des,
                        'username': current_user,
                        'no_seat': current_seat,
                    }
                    ticket_instance = Ticket.objects.create(**validated_data)
                    tickets.append(ticket_instance)

                    if current_user:
                        worker = Worker.objects.filter(username=current_user).first()
                        if worker:
                            fname = worker.fname
                            lname = worker.lname

                # --- DELETE EXISTING TICKETS FOR DA (Transfer Logic) ---
                if prs:
                    for i in range(min_length):
                        if i < len(das):
                            Ticket.objects.filter(
                                firstname=firstnames[i],
                                lastname=lastnames[i],
                                date=das[i],
                                depcity=depcitys[i],
                                descity=descitys[i]
                            ).delete()

            # --- RENDER DESK FOR WEB OR REST RESPONSE ---
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                context = {
                    'success': 'Ticket(s) processed successfully!',
                    'tickets': tickets,
                    'total_price': total_price,
                    'level': level,
                    'name': bus_name,
                    'fname': fname,
                    'lname': lname
                }
                # Direct recovery routing logic
                if is_recovery:
                    return render(request, 'users/recover.html', context)
                if not usernames or not usernames[0]:
                    return render(request, 'users/payment.html', context)
                else:
                    return render(request, 'users/myticket.html', context)
            serializer = TicketSerializer(tickets, many=True)
            return Response({'message': 'Booking successful.', 'tickets': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




"""
class CancelTicketView(APIView):
    def post(self, request):
        # 1. Retrieve data from form
        method = request.data.get('refund_method')
        account_number = request.data.get('refund_account')
        password = request.data.get('password')

        # Hidden ticket identifiers for deletion
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        price = request.data.get('price')

        # Find the specific ticket to delete
        ticket_to_delete = Ticket.objects.filter(
            firstname=firstname,
            lastname=lastname,
            plate_no=plate_no,
            side_no=side_no
        ).first()

        if ticket_to_delete:
            ticket_to_delete.delete()
            context = {
                'success': 'Refund processed and ticket cancelled successfully.'
            }
            return render(request, 'users/index.html', context)

        return render(request, 'users/index.html', {
            'error': 'Ticket not found or already cancelled.'
        })

"""




from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .models import Ticket, City, Worker, Buschange  # Added Buschange for the count
from .serializers import (
    BalanceSearchSerializer,
    TotalBalanceResponseSerializer
)
@extend_schema(tags=['Finance & Accounting'])
class Totalballance(APIView):
    serializer_class = TotalBalanceResponseSerializer
    @extend_schema(
        summary="Get balance page or city list",
        responses={200: OpenApiTypes.ANY}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to view balances.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch data
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/ballance.html', {
                'des': des,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })
        return Response({'cities': [city.depcity for city in des]}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Calculate total balance by username and city",
        request=BalanceSearchSerializer,
        responses={200: TotalBalanceResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. LOGIC: Handle dates
        dates = request.data.getlist('date[]') if 'date[]' in request.data else request.data.get('date', [])

        if not dates:
            if is_html:
                return render(request, 'users/ballance.html', {
                    'error': 'No dates provided', 
                    'des': City.objects.all(),
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'No dates provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 5. DATA PROCESSING: Sum up ticket prices
        totals_by_username = {}
        tickets = Ticket.objects.filter(booked_time__date__in=dates)

        for ticket in tickets:
            username = ticket.username if ticket.username else "Selfbook"
            try:
                price = float(ticket.price)
            except (ValueError, TypeError):
                continue
            totals_by_username[username] = totals_by_username.get(username, 0) + price

        # 6. ENRICHMENT: Get Worker details
        workers = Worker.objects.filter(username__in=totals_by_username.keys())
        worker_info = {
            worker.username: {
                'city': worker.city,
                'fname': worker.fname,
                'lname': worker.lname,
                'phone': worker.phone
            } for worker in workers
        }

        # 7. FINAL DATA MAPPING
        total_data = {
            username: {
                'total_balance': total,
                'city': worker_info.get(username, {}).get('city', 'Self'),
                'fname': worker_info.get(username, {}).get('fname', 'N/A'),
                'lname': worker_info.get(username, {}).get('lname', ''),
                'phone': worker_info.get(username, {}).get('phone', 'N/A'),
            }
            for username, total in totals_by_username.items() if total > 0
        }

        # 8. RESPONSE
        if is_html:
            return render(request, 'users/totalballance.html', {
                'totals': total_data,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        return Response({'totals': total_data}, status=status.HTTP_200_OK)




from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import City, Bus
from .serializers import WorkSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from .models import City, Bus, Route
@extend_schema(tags=['Routes & Cities'])
class RouteView(APIView):
    def get(self, request):
        des = City.objects.all()
        bus = Bus.objects.all()
        return Response({
            'cities': [city.name for city in des],
            'buses': [bus.plate_no for bus in bus]
        }, status=status.HTTP_200_OK)
    def post(self, request):
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        price = request.data.get('price')
        kilometer = request.data.get('kilometer')
        if depcity.strip() == descity.strip():
            return Response({'error': 'Departure and Destination cannot be the same!'}, status=status.HTTP_400_BAD_REQUEST)
        if Route.objects.filter(depcity=depcity, descity=descity, plate_no=plate_no, side_no=side_no, date=date).exists():
            return Response({'error': 'Route already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if Route.objects.filter(side_no=side_no, date=date, plate_no=plate_no).exists():
            return Response({'error': 'This bus is already reserved for another route for this date'}, status=status.HTTP_400_BAD_REQUEST)
        Route.objects.create(
            depcity=depcity,
            descity=descity,
            kilometer=kilometer,
            plate_no=plate_no,
            side_no=side_no,
            price=price,
            date=date
        )
        if depcity.strip() == "Addisababa":
            date = timezone.datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
            date = date.strftime('%Y-%m-%d')
            depcity, descity = descity, depcity
            Route.objects.create(
                depcity=depcity,
                descity=descity,
                kilometer=kilometer,
                plate_no=plate_no,
                side_no=side_no,
                price=price,
                date=date
            )
        return Response({'success': 'Route registered successfully!'}, status=status.HTTP_201_CREATED)

def city_view(request):
    if request.method == 'POST':
        depcity = request.POST['depcity']
        if City.objects.filter(depcity=depcity).exists():
            return render(request, 'users/city.html', {'error': 'This city already exists.'})
        city = City.objects.create(
            depcity=depcity,
        )
        city.save()
        return render(request, 'users/city.html', {'success': 'City registored Successfully!'})
    return render(request, 'users/city.html')













from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import TelebirrInitiateSerializer

@extend_schema(tags=['Payment Auth'])
class TelebirrPaymentView(APIView):
    serializer_class = TelebirrInitiateSerializer

    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tele.html')
        return Response({"message": "Use POST to initiate payment"}, status=200)

    @extend_schema(
        summary="Initiate Telebirr Payment",
        request=TelebirrInitiateSerializer,
        responses={200: TelebirrInitiateSerializer}
    )
    def post(self, request):
        phone_number = request.data.get('phone') or request.data.get('phone[]')
        price = request.data.get('price')
        if phone_number and len(phone_number) == 10 and phone_number.startswith('09'):
            context = {'phone_number': phone_number, 'price': price}
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/telepassword.html', context)
            return Response(context, status=status.HTTP_200_OK)

        else:
            error_message = "Invalid phone number. Please check and try again."
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/tele.html', {'error': error_message})

            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)


from django.views import View
from django.shortcuts import render, redirect
class Update(View):
    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tele.html')
    def post(self, request):
        phone_number = request.POST.get('phone[]')
        price = request.POST.get('price')
        if phone_number and len(phone_number) == 10 and phone_number.startswith('09'):
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/telepassword.html', {'phone_number': phone_number, 'price': price})
        else:
            error_message = "Invalid phone number. Please check and try again."
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/tele.html', {'error': error_message})



import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Service_fee
from .serializers import TelebirrAuthSerializer
@extend_schema(tags=['Payment Auth'])
class Telebirrpassword(APIView):
    serializer_class = TelebirrAuthSerializer

    def get(self, request):
        return render(request, 'users/telepassword.html')

    @extend_schema(
        summary="Process Telebirr Payment",
        request=TelebirrAuthSerializer,
        responses={200: dict}
    )
    def post(self, request):
        phone_number = request.data.get('phone')
        password = request.data.get('password')
        
        try:
            price_raw = request.data.get('price', 0)
            price = float(price_raw) if price_raw else 0.0
        except (ValueError, TypeError):
            price = 0.0

        recipient_phone = "0975143134"
        recipient_service_fee_phone = "0949949849"
        
        service_fee_instance = Service_fee.objects.first()
        value = service_fee_instance.service_fee if service_fee_instance else 0
        if phone_number and len(phone_number) == 10 and phone_number.startswith('09'):
            if self.is_phone_and_password_valid(phone_number, password):
                user_balance = self.get_balance(phone_number)
                recipient_balance = self.get_balance(recipient_phone)
                recipient_balance_service_fee = self.get_balance(recipient_service_fee_phone)

                if user_balance is not None and recipient_balance is not None:
                    if user_balance >= price:
                        transaction_response = self.create_transaction(recipient_phone, price)
                        
                        if transaction_response.get('success'):
                            fee = price - value
                            share_value = price - fee # Your original logic kept exactly
                            
                            new_recipient_balance_service_fee = (recipient_balance_service_fee or 0) + share_value
                            new_recipient_balance = (recipient_balance or 0) + fee
                            res1 = self.add_balance(recipient_phone, new_recipient_balance)
                            res2 = self.add_balance(recipient_service_fee_phone, new_recipient_balance_service_fee)

                            if res1.get('success') and res2.get('success'):
                                context = {
                                    'success': 'Successfully paid and balances updated.',
                                    'transaction_id': transaction_response.get('transaction_id'),
                                    'recipient_balance': new_recipient_balance
                                }
                                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                                    return render(request, 'users/payment_success.html', context)
                                return Response(context, status=status.HTTP_200_OK)
                            else:
                                return self.render_error(request, "Failed to update balances.", phone_number, price)
                        else:
                            return self.render_error(request, "Transaction failed.", phone_number, price)
                    else:
                        return self.render_error(request, "Insufficient balance.", phone_number, price)
                else:
                    return self.render_error(request, "Unable to retrieve balance.", phone_number, price)
            else:
                return self.render_error(request, "Invalid password.", phone_number, price)
        else:
            return self.render_error(request, "Invalid phone number format.", phone_number, price)

    def render_error(self, request, message, phone, price):
        context = {'error': message, 'phone_number': phone, 'price': price}
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/telepassword.html', context)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    def is_phone_and_password_valid(self, phone_number, password):
        try:
            url = "https://www.ethiotelecom.et/telebirr/validate"
            payload = {'phone': phone_number, 'password': password}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json().get('valid', False) if response.status_code == 200 else False
        except Exception: return False

    def get_balance(self, phone_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'phone': phone_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception: return None

    def create_transaction(self, recipient_phone, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'phone': recipient_phone, 'amount': amount, 'description': 'Payment'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}

    def add_balance(self, phone_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'phone': phone_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import CbeInputSerializer  # Import the serializer defined above

@extend_schema(tags=['Payment Auth'])
class CbePaymentView(APIView):
    serializer_class = CbeInputSerializer

    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cbe.html')
        return Response({"message": "Please use a POST request to initiate payment."}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Initiate CBE Payment",
        request=CbeInputSerializer,
        responses={
            200: CbeInputSerializer, 
            400: dict
        }
    )
    def post(self, request):
        account_number = request.data.get('account')
        price = request.data.get('price')
        
        print(f"Processing payment: Account {account_number}, Price {price}")
        if account_number and len(account_number) == 13 and account_number.startswith('1000'):
            context = {'account_number': account_number, 'price': price}
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/cbepassword.html', context)
            
            return Response(context, status=status.HTTP_200_OK)
        
        else:
            error_message = "Invalid Account number. Please check and try again."
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/cbe.html', {'error': error_message})
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)





import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from users.models import Service_fee
from .serializers import CbeAuthSerializer
@extend_schema(tags=['Payment Auth'])
class Cbepassword(APIView):
    serializer_class = CbeAuthSerializer

    def get(self, request):
        return render(request, 'users/cbepassword.html')

    @extend_schema(
        summary="Process CBE Payment",
        request=CbeAuthSerializer,
        responses={200: dict}
    )
    def post(self, request):
        account_number = request.data.get('account')
        password = request.data.get('password')
        
        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        recipient_account = "1000327248549"
        recipient_service_fee_account = "1000136832598"
        
        service_fee_instance = Service_fee.objects.first()
        value = service_fee_instance.service_fee if service_fee_instance else 0
        if account_number and len(account_number) == 13 and account_number.startswith('1000'):
            if self.is_phone_and_password_valid(account_number, password):
                user_balance = self.get_balance(account_number)
                recipient_balance = self.get_balance(recipient_account)
                recipient_balance_service_fee = self.get_balance(recipient_service_fee_account)

                if user_balance is not None and recipient_balance is not None:
                    if user_balance >= price:
                        transaction_response = self.create_transaction(recipient_account, price)

                        if transaction_response.get('success'):
                            fee = price - value
                            share_value = price - fee
                            
                            new_recipient_balance_service_fee = (recipient_balance_service_fee or 0) + share_value
                            new_recipient_balance = (recipient_balance or 0) + fee
                            self.add_balance(recipient_account, new_recipient_balance)
                            add_balance_response = self.add_balance(recipient_service_fee_account, new_recipient_balance_service_fee)

                            if add_balance_response.get('success'):
                                context = {
                                    'success': 'Successfully paid and balance updated.',
                                    'transaction_id': transaction_response.get('transaction_id'),
                                    'recipient_balance': new_recipient_balance
                                }
                                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                                    return render(request, 'users/cbe_success.html', context)
                                return Response(context, status=status.HTTP_200_OK)
                            else:
                                return self.render_error(request, "Failed to update recipient balance.", account_number, price)
                        else:
                            return self.render_error(request, "Transaction failed. Please try again.", account_number, price)
                    else:
                        return self.render_error(request, "Insufficient balance.", account_number, price)
                else:
                    return self.render_error(request, "Unable to retrieve balance.", account_number, price)
            else:
                return self.render_error(request, "Invalid password.", account_number, price)
        else:
            return self.render_error(request, "Invalid account number format.", account_number, price)

    def render_error(self, request, message, account, price):
        context = {'error': message, 'account_number': account, 'price': price}
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cbepassword.html', context)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    def is_phone_and_password_valid(self, account_number, password):
        try:
            url = "https://www.ethiotelecom.et/telebirr/validate"
            payload = {'account': account_number, 'password': password}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json().get('valid', False) if response.status_code == 200 else False
        except Exception: return False

    def get_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception: return None

    def create_transaction(self, recipient_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': recipient_account, 'amount': amount, 'description': 'International payment'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}

    def add_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import BoaInputSerializer

@extend_schema(tags=['Payment Auth'])
class BoaPaymentView(APIView):
    serializer_class = BoaInputSerializer

    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/boa.html')
        return Response({"message": "Use a POST request with 'account' and 'price'."})

    @extend_schema(
        summary="Validate BOA Account",
        request=BoaInputSerializer,
        responses={200: BoaInputSerializer, 400: dict}
    )
    def post(self, request):
        account_number = request.data.get('account')
        price = request.data.get('price')
        if account_number and len(account_number) == 8 and account_number.startswith('48'):
            context = {'account_number': account_number, 'price': price}
            
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/boapassword.html', context)
            
            return Response(context, status=status.HTTP_200_OK)
        
        else:
            error_message = "Invalid Account number. Please check and try again."
            
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/boa.html', {'error': error_message})
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from users.models import Service_fee
from .serializers import BoaAuthSerializer

@extend_schema(tags=['Payment Auth'])
class Boapassword(APIView):
    serializer_class = BoaAuthSerializer

    def get(self, request):
        return render(request, 'users/boapassword.html')

    @extend_schema(
        summary="Verify BOA Password and Complete Payment",
        request=BoaAuthSerializer,
        responses={200: dict}
    )
    def post(self, request):
        account_number = request.data.get('account')
        password = request.data.get('password')

        try:
            price_raw = request.data.get('price', '0')
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        recipient_account = "48710778"
        recipient_service_fee_account = "48710779"

        service_fee_instance = Service_fee.objects.first()
        value = service_fee_instance.service_fee if service_fee_instance else 0
        if account_number and len(account_number) == 8 and account_number.startswith('48'):
            if self.is_phone_and_password_valid(account_number, password):
                user_balance = self.get_balance(account_number)
                recipient_balance = self.get_balance(recipient_account)
                recipient_balance_service_fee = self.get_balance(recipient_service_fee_account)

                if user_balance is not None and recipient_balance is not None:
                    if user_balance >= price:
                        transaction_response = self.create_transaction(recipient_account, price)

                        if transaction_response.get('success'):
                            fee = price - value
                            share_value = price - fee

                            new_recipient_balance_service_fee = (recipient_balance_service_fee or 0) + share_value
                            new_recipient_balance = (recipient_balance or 0) + fee
                            self.add_balance(recipient_account, new_recipient_balance)
                            add_res = self.add_balance(recipient_service_fee_account, new_recipient_balance_service_fee)

                            if add_res.get('success'):
                                context = {
                                    'success': 'Successfully paid and balance updated.',
                                    'transaction_id': transaction_response.get('transaction_id'),
                                    'recipient_balance': new_recipient_balance
                                }
                                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                                    return render(request, 'users/payment_success.html', context)
                                return Response(context, status=status.HTTP_200_OK)
                            else:
                                return self.render_error(request, "Failed to update balances.", account_number, price)
                        else:
                            return self.render_error(request, "Transaction failed.", account_number, price)
                    else:
                        return self.render_error(request, "Insufficient balance.", account_number, price)
                else:
                    return self.render_error(request, "Unable to retrieve balance.", account_number, price)
            else:
                return self.render_error(request, "Invalid password.", account_number, price)
        else:
            return self.render_error(request, "Invalid account number format.", account_number, price)

    def render_error(self, request, message, account, price):
        context = {'error': message, 'account_number': account, 'price': price}
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/boapassword.html', context)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    def is_phone_and_password_valid(self, account_number, password):
        try:
            url = "https://www.ethiotelecom.et/telebirr/validate"
            payload = {'account': account_number, 'password': password}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json().get('valid', False) if response.status_code == 200 else False
        except: return False

    def get_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except: return None

    def create_transaction(self, recipient_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {'account': recipient_account, 'amount': amount, 'description': 'BOA Payment'}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except: return {'success': False}

    def add_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except: return {'success': False}
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import AwashInputSerializer

@extend_schema(tags=['Payment Auth'])
class AwashPaymentView(APIView):
    serializer_class = AwashInputSerializer

    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/awash.html')
        return Response({"message": "Please use POST to initiate payment."}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Initiate Awash Payment",
        request=AwashInputSerializer,
        responses={200: AwashInputSerializer, 400: dict}
    )
    def post(self, request):
        account_number = request.data.get('account')
        price = request.data.get('price')
        if account_number and len(account_number) == 13 and account_number.startswith('1000'):
            context = {'account_number': account_number, 'price': price}
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/awashpassword.html', context)
            return Response(context, status=status.HTTP_200_OK)
        
        else:
            error_message = "Invalid Account number. Please check and try again."
            
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/awash.html', {'error': error_message})
            
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import AwashAuthSerializer
from .models import Service_fee  # Ensure this import is correct
@extend_schema(tags=['Payment Auth'])
class Awashpassword(APIView):
    serializer_class = AwashAuthSerializer

    def get(self, request):
        return render(request, 'users/awashpassword.html')

    @extend_schema(request=AwashAuthSerializer)
    def post(self, request):
        account_number = request.data.get('account')
        password = request.data.get('password')
        try:
            price = float(request.data.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0
        recipient_account = "1000273165634"
        recipient_service_fee_account = "1000327248549"

        service_fee_instance = Service_fee.objects.first()
        value = service_fee_instance.service_fee if service_fee_instance else 0
        if not (account_number and len(account_number) == 13 and account_number.startswith('1000')):
            return self.handle_error(request, "Invalid phone number format.", account_number, price)
        if self.is_phone_and_password_valid(account_number, password):
            user_balance = self.get_balance(account_number)
            recipient_balance = self.get_balance(recipient_account)
            fee_acc_balance = self.get_balance(recipient_service_fee_account)

            if user_balance is not None and recipient_balance is not None:
                if user_balance >= price:
                    transaction_response = self.create_transaction(recipient_account, price)

                    if transaction_response.get('success'):
                        fee = price - value
                        share_value = price - fee

                        new_recipient_balance = (recipient_balance or 0) + fee
                        new_fee_acc_balance = (fee_acc_balance or 0) + share_value
                        self.add_balance(recipient_account, new_recipient_balance)
                        add_balance_response = self.add_balance(recipient_service_fee_account, new_fee_acc_balance)

                        if add_balance_response.get('success'):
                            context = {
                                'success': 'Successfully paid and balance updated.',
                                'transaction_id': transaction_response.get('transaction_id'),
                                'recipient_balance': new_recipient_balance
                            }
                            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                                return render(request, 'users/awash_success.html', context)
                            return Response(context, status=status.HTTP_200_OK)

                        return self.handle_error(request, "Failed to update balances.", account_number, price)
                    return self.handle_error(request, "Transaction failed at Bank API.", account_number, price)
                return self.handle_error(request, "Insufficient balance.", account_number, price)
            return self.handle_error(request, "Unable to retrieve balance.", account_number, price)
        return self.handle_error(request, "Invalid password.", account_number, price)

    def handle_error(self, request, message, account, price):
        context = {'error': message, 'account_number': account, 'price': price}
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/awashpassword.html', context)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)

    def is_phone_and_password_valid(self, account_number, password):
        try:
            url = "https://www.ethiotelecom.et/telebirr/validate"
            payload = {'account': account_number, 'password': password}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.json().get('valid', False) if response.status_code == 200 else False
        except Exception: return False

    def get_balance(self, account_number):
        try:
            url = "https://www.ethiotelecom.et/telebirr/balance"
            payload = {'account': account_number}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return float(response.json().get('balance', 0)) if response.status_code == 200 else None
        except Exception: return None

    def create_transaction(self, recipient_account, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/transaction"
            payload = {
                'account': recipient_account, # Fixed variable name
                'amount': amount,
                'description': 'International payment transaction'
            }
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}

    def add_balance(self, account_number, amount):
        try:
            url = "https://www.ethiotelecom.et/telebirr/add_balance"
            payload = {'account': account_number, 'amount': amount}
            headers = {'Authorization': 'Bearer YOUR_API_KEY', 'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.json() if response.status_code == 200 else {'success': False}
        except Exception: return {'success': False}
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import SafariPhoneSerializer

@extend_schema(tags=['Payment Auth'])
class SafariPaymentView(APIView):
    serializer_class = SafariPhoneSerializer

    def get(self, request):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/safaricom.html')
        return Response({"message": "Please use HTML browser or POST request."}, status=405)

    @extend_schema(
        request=SafariPhoneSerializer,
        responses={200: dict}
    )
    def post(self, request):
        phone_number = request.data.get('phone[]') or request.data.get('phone')
        price = request.data.get('price')
        if phone_number and len(phone_number) == 10 and phone_number.startswith('07'):
            context = {'phone_number': phone_number, 'price': price}
            
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/safaripassword.html', context)
            
            return Response(context, status=status.HTTP_200_OK)
        
        else:
            error_message = "Invalid phone number. Please check and try again."
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/safaricom.html', {'error': error_message})
            
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)





import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .serializers import SafaricomAuthSerializer
from users.models import Service_fee

@extend_schema(tags=['Payment Auth'])
class Safaricompassword(APIView):
    serializer_class = SafaricomAuthSerializer

    def get(self, request):
        return render(request, 'users/safaripassword.html')
    @extend_schema(request=SafaricomAuthSerializer)
    def post(self, request):
        phone_number = request.data.get('phone')
        password = request.data.get('password')
        try:
            price = float(request.data.get('price', 0))
        except (ValueError, TypeError):
            price = 0.0
        recipient_phone = "0722792799"
        recipient_service_fee_phone = "0749942013"

        service_fee_instance = Service_fee.objects.first()
        service_fee_val = service_fee_instance.service_fee if service_fee_instance else 0
        if not (phone_number and len(phone_number) == 10 and phone_number.startswith('07')):
            return self.render_error(request, "Invalid phone format.", phone_number, price)
        if self.is_phone_and_password_valid(phone_number, password):
            user_bal = self.get_balance(phone_number)
            rec_bal = self.get_balance(recipient_phone)
            fee_bal = self.get_balance(recipient_service_fee_phone)

            if user_bal is not None and rec_bal is not None and fee_bal is not None:
                if user_bal >= price:
                    tx_res = self.create_transaction(recipient_phone, price)

                    if tx_res.get('success'):
                        fee_to_merchant = price - service_fee_val
                        fee_to_service = price - fee_to_merchant

                        new_rec_bal = rec_bal + fee_to_merchant
                        new_fee_bal = fee_bal + fee_to_service
                        self.add_balance(recipient_phone, new_rec_bal)
                        add_res = self.add_balance(recipient_service_fee_phone, new_fee_bal)

                        if add_res.get('success'):
                            context = {
                                'success': 'Successfully paid.',
                                'transaction_id': tx_res.get('transaction_id'),
                                'recipient_balance': new_rec_bal
                            }
                            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                                return render(request, 'users/safari_success.html', context)
                            return Response(context, status=status.HTTP_200_OK)

                        return self.render_error(request, "Balance update failed.", phone_number, price)
                    return self.render_error(request, "Transaction failed at API.", phone_number, price)
                return self.render_error(request, "Insufficient balance.", phone_number, price)
            return self.render_error(request, "Could not retrieve balances.", phone_number, price)
        return self.render_error(request, "Invalid password.", phone_number, price)

    def render_error(self, request, message, phone, price):
        context = {'error': message, 'phone_number': phone, 'price': price}
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/safaripassword.html', context)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    def is_phone_and_password_valid(self, phone, pwd):
        try:
            res = requests.post("https://www.ethiotelecom.et/telebirr/validate",
                                json={'phone': phone, 'password': pwd}, timeout=10)
            return res.json().get('valid', False)
        except:
            return False

    def get_balance(self, phone):
        try:
            res = requests.post("https://www.ethiotelecom.et/telebirr/balance",
                                json={'phone': phone}, timeout=10)
            return float(res.json().get('balance', 0))
        except:
            return None

    def create_transaction(self, phone, amount):
        try:
            res = requests.post("https://www.ethiotelecom.et/telebirr/transaction",
                                json={'phone': phone, 'amount': amount}, timeout=10)
            return res.json()
        except:
            return {'success': False}

    def add_balance(self, phone, amount):
        try:
            res = requests.post("https://www.ethiotelecom.et/telebirr/add_balance",
                                json={'phone': phone, 'amount': amount}, timeout=10)
            return res.json()
        except:
            return {'success': False}












from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Route, City, Buschange
from .serializers import RoutSerializer
@extend_schema(tags=['Ticket Management'])
class DeleteTicketViews(APIView):
    serializer_class = TicketSerializer  # Add this
    @extend_schema(responses={204: None}, description="Delete a single ticket")
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage tickets.',
                'buschanges_count': buschanges_count
            })

        # 2. AUTHORIZED: Fetch Cities
        des = City.objects.all()
        
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckrouteeee.html', {
                'des': des,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })
        
        return Response({'cities': [city.depcity for city in des]}, status=status.HTTP_200_OK)
    @extend_schema(responses={204: None})
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. SEARCH LOGIC
        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        routes = Route.objects.filter(date=date, depcity=depcity, descity=descity)

        if routes.exists():
            serialized_route = RoutSerializer(routes, many=True)
            
            if is_html:
                return render(request, 'users/rooteeee.html', {
                    'routes': serialized_route.data,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            
            return Response({'routes': serialized_route.data}, status=status.HTTP_200_OK)
        
        else:
            # 5. HANDLE NO RESULTS
            error_msg = 'No booked tickets for this travel'
            
            if is_html:
                des = City.objects.all()
                return render(request, 'users/cheeckrouteeee.html', {
                    'error': error_msg,
                    'des': des,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            
            return Response({'error': error_msg}, status=status.HTTP_404_NOT_FOUND)







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.shortcuts import render
from .models import Ticket, Route, Buschange
from .serializers import TickSerializer, RoutSerializer
@extend_schema(tags=['Ticket Management'])
class DeleteTickets(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    serializer_class = TicketSerializer 

    @extend_schema(
        operation_id="delete_tickets_form_lookup", # UNIQUE ID
        responses={200: TicketSerializer(many=True)}, 
        description="Finds tickets to display in the deletion form."
    )
    def post(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. DATA EXTRACTION
        date = request.data.get('date')
        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        # 3. QUERYING
        ticket_query = Ticket.objects.filter(
            plate_no=plate_no, 
            date=date, 
            depcity=depcity, 
            descity=descity
        )
        
        # 4. LOGIC: Found tickets to delete?
        if ticket_query.exists():
            serialized_tickets = TickSerializer(ticket_query, many=True)
            
            if is_html:
                return render(request, 'users/deleteticket.html', {
                    'route': serialized_tickets.data,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            return Response({'route': serialized_tickets.data}, status=status.HTTP_200_OK)

        # 5. LOGIC: No tickets found (Fallback to Route list)
        else:
            routes = Route.objects.filter(date=date, depcity=depcity, descity=descity)
            serialized_routes = RoutSerializer(routes, many=True)
            error_msg = 'No booked tickets for this travel'

            if is_html:
                return render(request, 'users/rooteeee.html', {
                    'error': error_msg, 
                    'routes': serialized_routes.data,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            
            return Response({
                'error': error_msg, 
                'routes': serialized_routes.data
            }, status=status.HTTP_404_NOT_FOUND)






from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from .models import Ticket, Buschange # Import Buschange for notifications
class DeleteTicketsView(APIView):
    
    @extend_schema(
        operation_id="delete_tickets_action_api", # UNIQUE ID
        request=None,
        responses={204: None},
        description="Processes the database deletion of a specific ticket."
    )
    def post(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. EXTRACT DATA
        date = request.data.get('date')
        plate_no = request.data.get('plate_no')
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        phone = request.data.get('phone')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        # 3. PERFORM DELETION
        # deleted_count returns how many records were actually removed
        deleted_count, _ = Ticket.objects.filter(
            plate_no=plate_no,
            date=date,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            depcity=depcity,
            descity=descity
        ).delete()

        # 4. FETCH REMAINING TICKETS
        # This is used to re-render the list so the user sees the updated state
        remaining_tickets = Ticket.objects.filter(
            depcity=depcity,
            descity=descity,
            plate_no=plate_no,
            date=date
        )

        # 5. RESPONSE LOGIC
        if is_html:
            context = {
                'buschanges_count': buschanges_count,
                'username': request.session.get('username'),
                'route': remaining_tickets
            }

            if deleted_count > 0:
                context['success'] = 'Ticket deleted successfully.'
            else:
                context['error'] = 'No ticket found to delete.'

            return render(request, 'users/deleteticket.html', context)

        # API JSON Response
        if deleted_count > 0:
            return Response({'success': 'Ticket deleted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No ticket found to delete.'}, status=status.HTTP_404_NOT_FOUND)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Route, City, Buschange
from .serializers import RoutSerializer, TicketSearchRequestSerializer

@extend_schema(tags=['Booking & Tickets'])
class TicketInfoView(APIView):
    serializer_class = TicketSearchRequestSerializer

    @extend_schema(summary="Get ticket search page or city list")
    def get(self, request):
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to search tickets.',
                'buschanges_count': buschanges_count
            })

        des = City.objects.all()

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckrouteee.html', {
                'des': des,
                'buschanges_count': buschanges_count,
                'username': request.session.get('username')
            })

        return Response({'cities': [city.depcity for city in des]}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Search for routes by date and cities",
        request=TicketSearchRequestSerializer,
        responses={200: RoutSerializer(many=True), 404: dict}
    )
    def post(self, request):
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Session expired. Please login again.',
                'buschanges_count': buschanges_count
            })

        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        routes = Route.objects.filter(date=date, depcity=depcity, descity=descity)

        if routes.exists():
            serialized_route = RoutSerializer(routes, many=True)
            if is_html:
                return render(request, 'users/rootee.html', {
                    'routes': serialized_route.data,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            return Response({'routes': serialized_route.data}, status=status.HTTP_200_OK)
        
        else:
            error_msg = 'No booked tickets for this travel'
            if is_html:
                des = City.objects.all()
                return render(request, 'users/cheeckrouteee.html', {
                    'error': error_msg,
                    'des': des,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            return Response({'error': error_msg}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Ticket, Route, Buschange
from .serializers import (
    TickSerializer, RoutSerializer, 
    SelectBusRequestSerializer, SelectBusResponseSerializer
)
@extend_schema(tags=['Booking & Tickets'])
class SelectBusView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    serializer_class = SelectBusRequestSerializer

    @extend_schema(
        summary="Search for tickets or available routes",
        request=SelectBusRequestSerializer,
        responses={200: SelectBusResponseSerializer}
    )
    def post(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. VALIDATION
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            if is_html:
                return render(request, 'users/rootee.html', {
                    'error': 'Invalid search parameters.',
                    'buschanges_count': buschanges_count
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 3. DATA EXTRACTION
        date = serializer.validated_data.get('date')
        plate_no = serializer.validated_data.get('plate_no')
        depcity = serializer.validated_data.get('depcity')
        descity = serializer.validated_data.get('descity')

        # 4. QUERYING
        ticket_qs = Ticket.objects.filter(plate_no=plate_no, date=date, depcity=depcity, descity=descity)
        route_qs = Route.objects.filter(date=date, depcity=depcity, descity=descity)
        # 5. RESPONSE LOGIC
        context = {
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }
        if ticket_qs.exists():
            data = TickSerializer(ticket_qs, many=True).data
            context['route'] = data   
            if is_html:
                return Response(context, template_name='users/ticketoch.html')
            return Response(context, status=status.HTTP_200_OK)
        else:
            alternative_data = RoutSerializer(route_qs, many=True).data
            context.update({
                'error': 'No booked tickets for this travel',
                'routes': alternative_data
            })
            
            if is_html:
                return Response(context, template_name='users/rootee.html')
            return Response(context, status=status.HTTP_200_OK)




"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema
from .models import Ticket, City, Bus, Route
from .serializers import UpdateTicketRequestSerializer

@extend_schema(tags=['Booking & Tickets'])
class UpdateTicketViews(APIView):
    serializer_class = UpdateTicketRequestSerializer

    @extend_schema(summary="Get ticket update page")
    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tickets.html', {'des': des})
        return Response({'cities': [c.depcity for c in des]}, status=status.HTTP_200_OK)

    @extend_schema(summary="Check availability for a new travel date", request=UpdateTicketRequestSerializer)
    def post(self, request):
        data = request.data
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        depcity = data.get('depcity')
        descity = data.get('descity')
        phone = data.get('phone')
        price = data.get('price')
        email = data.get('email')
        gender = data.get('gender')
        passenger_type = data.get('passenger_type')
        plate_no = data.get('plate_no')
        side_no = data.get('side_no')
        da = data.get('da')  # Original date
        new_date = data.get('new_date')

        error_message = None
        try:
            if new_date:
                if new_date == da:
                    error_message = "Error: The new date is the same as your current travel date."
                else:
                    incoming_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                    if incoming_date < timezone.now().date():
                        error_message = "Error: Past dates are not allowed."
            else:
                error_message = "Please select a new travel date."
        except ValueError:
            error_message = "Invalid date format. Use YYYY-MM-DD."
        if not error_message:
            available_routes = Route.objects.filter(depcity=depcity, descity=descity, date=new_date)

            if available_routes.exists():
                routes_list = []
                for r in available_routes:
                    buses = Bus.objects.filter(plate_no=r.plate_no)
                    level = buses.first().level if buses.exists() else "N/A"
                    total_seats = sum(int(b.no_seats) for b in buses if str(b.no_seats).isdigit())

                    booked = Ticket.objects.filter(
                        depcity=r.depcity, descity=r.descity,
                        date=r.date, plate_no=r.plate_no
                    ).count()

                    remaining = max(0, total_seats - booked)
                    routes_list.append({
                        'route': r,
                        'levels': level,
                        'remaining_seats': "Full" if remaining <= 0 else remaining
                    })
                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    return render(request, 'users/rooote.html', {
                        'routes': routes_list, 'firstname': firstname, 'lastname': lastname, 'passenger_type': passenger_type,
                        'phone': phone, 'email': email, 'price': price, 'da': da,
                        'plate_no': plate_no, 'side_no': side_no, 'depcity': depcity,
                        'descity': descity, 'gender': gender, 'new_date': new_date
                    })
                return Response({'routes': routes_list}, status=status.HTTP_200_OK)
            else:
                error_message = "No buses are reserved for the selected date."
        ticket = Ticket.objects.filter(
            firstname=firstname, lastname=lastname,
            depcity=depcity, descity=descity, date=da
        ).first()

        context = {
            'des': City.objects.all(),
            'error': error_message,
            'ticket': ticket,
            'level': Bus.objects.filter(plate_no=plate_no).values_list('level', flat=True).first() if plate_no else None,
            #'qr_code_path': ticket.generate_qr_code() if ticket else None
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tickets.html', context)
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
"""




from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Ticket, City, Bus, Route
from .serializers import UpdateTicketRequestSerializer
@extend_schema(tags=['Booking & Tickets'])
class UpdateTicketViews(APIView):
    serializer_class = UpdateTicketRequestSerializer

    @extend_schema(summary="Get ticket update page")
    def get(self, request):
        des = City.objects.all()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tickets.html', {'des': des})
        return Response({'cities': [c.name for c in des]}, status=status.HTTP_200_OK)

    @extend_schema(summary="Check availability for a new travel date", request=UpdateTicketRequestSerializer)
    def post(self, request):
        data = request.data
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        depcity = data.get('depcity')
        descity = data.get('descity')
        phone = data.get('phone')
        price = data.get('price')
        email = data.get('email')
        gender = data.get('gender')
        passenger_type = data.get('passenger_type')
        plate_no = data.get('plate_no')
        side_no = data.get('side_no')
        da = data.get('da')  # Original date
        new_date = data.get('new_date')

        error_message = None
        try:
            if new_date:
                if new_date == da:
                    error_message = "Error: The new date is the same as your current travel date."
                else:
                    incoming_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                    if incoming_date < timezone.now().date():
                        error_message = "Error: Past dates are not allowed."
            else:
                error_message = "Please select a new travel date."
        except ValueError:
            error_message = "Invalid date format. Use YYYY-MM-DD."

        if not error_message:
            available_routes = Route.objects.filter(depcity=depcity, descity=descity, date=new_date)
            if available_routes.exists():
                routes_list = []
                for r in available_routes:
                    buses = Bus.objects.filter(plate_no=r.plate_no)

                    # Look up dynamic metadata properties from database query matching plate_no
                    level = buses.first().level if buses.exists() else "N/A"
                    bus_name = buses.first().name if buses.exists() else "Wedehager Premium"

                    total_seats = sum(int(b.no_seats) for b in buses if str(b.no_seats).isdigit())

                    booked = Ticket.objects.filter(
                        depcity=r.depcity, descity=r.descity,
                        date=r.date, plate_no=r.plate_no
                    ).count()

                    remaining = max(0, total_seats - booked)

                    routes_list.append({
                        'route': r,
                        'levels': level,
                        'name': bus_name, # Mapped securely for the user portal loop
                        'remaining_seats': remaining
                    })

                if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                    return render(request, 'users/rooote.html', {
                        'routes': routes_list, 'firstname': firstname, 'lastname': lastname, 'passenger_type': passenger_type,
                        'phone': phone, 'email': email, 'price': price, 'da': da,
                        'plate_no': plate_no, 'side_no': side_no, 'depcity': depcity,
                        'descity': descity, 'gender': gender, 'new_date': new_date
                    })
                return Response({'routes': routes_list}, status=status.HTTP_200_OK)
            else:
                error_message = "No buses are reserved for the selected date."

        ticket = Ticket.objects.filter(
            firstname=firstname, lastname=lastname,
            depcity=depcity, descity=descity, date=da
        ).first()

        context = {
            'des': City.objects.all(),
            'error': error_message,
            'ticket': ticket,
            'level': Bus.objects.filter(plate_no=plate_no).values_list('level', flat=True).first() if plate_no else None,
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/tickets.html', context)
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import Buschange, Route, Bus, Ticket, City
from .serializers import RouteSerializer, SelectRequestSerializer, SelectResponseSerializer
from drf_spectacular.utils import extend_schema

class SelectView(APIView):
    serializer_class = SelectRequestSerializer

    @extend_schema(summary="Get bus changes count")
    def get(self, request):
        buschanges_count = Buschange.objects.count()
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/roote.html', {'buschanges_count': buschanges_count})
        return Response({'buschanges_count': buschanges_count}, status=status.HTTP_200_OK)

    @extend_schema(
        request=SelectRequestSerializer,
        responses={200: SelectResponseSerializer},
        summary="Lookup seats for a specific route"
    )
    def post(self, request):
        plate_no = request.data.get('plate_no')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')

        buschanges_count = Buschange.objects.count()
        routes = Route.objects.filter(depcity=depcity, descity=descity, date=date, plate_no=plate_no)

        if not routes.exists():
            error_message = "There is no Travel for this information!"
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/tickets.html', {
                    'des': City.objects.all(),
                    'buschanges_count': buschanges_count,
                    'error': error_message
                })
            return Response({'error': error_message}, status=status.HTTP_404_NOT_FOUND)

        bus = Bus.objects.filter(plate_no=plate_no).first()
        if not bus:
            return Response({'error': 'Bus not found'}, status=status.HTTP_404_NOT_FOUND)
        levels = bus.level
        total_seats = int(bus.no_seats)

        booked_tickets = Ticket.objects.filter(
            depcity=depcity, descity=descity, date=date, plate_no=plate_no
        ).values_list('no_seat', flat=True)

        booked_seats = list(set(int(seat) for seat in booked_tickets if seat))
        booked_seat_count = len(booked_seats)
        remaining_seats = total_seats - booked_seat_count
        unbooked_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_seats]

        if remaining_seats <= 0:
            if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
                return render(request, 'users/roote.html', {
                    'error': 'This Bus is Full!',
                    'levels': levels,
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'This Bus is Full!'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_routes = RouteSerializer(routes, many=True).data
        response_data = {
            'routes': serialized_routes,
            'levels': levels,
            'remaining_seats': remaining_seats,
            'unbooked_seats': unbooked_seats,
            'booked_seats': booked_seats,
            'all_seats': list(range(1, total_seats + 1))
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/ticket.html', response_data)

        return Response(response_data, status=status.HTTP_200_OK)












"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema
from .models import City, Route, Bus, Ticket, Buschange
from .serializers import BookRequestSerializer, BookResponseSerializer
@extend_schema(tags=['Booking & Tickets'])
class BookView(APIView):
    serializer_class = BookRequestSerializer

    @extend_schema(summary="Get available cities and bus changes")
    def get(self, request):
        buschanges_count = Buschange.objects.count()
        des = City.objects.all()

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckroutee.html', {
                'des': des,
                'buschanges_count': buschanges_count
            })

        return Response({
            'des': [city.name for city in des],
            'buschanges_count': buschanges_count
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Search for available routes",
        request=BookRequestSerializer,
        responses={200: BookResponseSerializer}
    )
    def post(self, request):
        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        try:
            incoming_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return self.handle_error(request, "Invalid date format. Use YYYY-MM-DD.", status.HTTP_400_BAD_REQUEST)

        if incoming_date < timezone.now().date():
            return self.handle_error(request, "Error: Past dates are not allowed.", status.HTTP_400_BAD_REQUEST)
        rout_qs = Route.objects.filter(depcity=depcity, descity=descity, date=date)
        buschanges_count = Buschange.objects.count()
        routes_list = []
        last_found_levels = None

        if rout_qs.exists():
            for route in rout_qs:
                buses = Bus.objects.filter(plate_no=route.plate_no)
                levels = buses.first().level if buses.exists() else "N/A"
                last_found_levels = levels
                total_seats = sum(int(bus.no_seats or 0) for bus in buses)

                booked_tickets = Ticket.objects.filter(
                    depcity=route.depcity,
                    descity=route.descity,
                    date=route.date,
                    plate_no=route.plate_no
                ).count()

                remaining_seats = total_seats - booked_tickets

                if remaining_seats > 0:
                    routes_list.append({
                        'route': route, # This allows access via item.route.depcity in HTML
                        'levels': levels,
                        'remaining_seats': remaining_seats
                    })
        if not routes_list:
            return self.handle_error(request, "There is no Travel for this information!", status.HTTP_404_NOT_FOUND)
        context = {
            'routes': routes_list,
            'levels': last_found_levels,
            'buschanges_count': buschanges_count
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/roote.html', context)

        return Response(context, status=status.HTTP_200_OK)

    def handle_error(self, request, message, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckroutee.html', {
                'des': City.objects.all(),
                'buschanges_count': Buschange.objects.count(),
                'error': message
            })
        return Response({"error": message}, status=status_code)
"""



from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import City, Route, Bus, Ticket, Buschange
from .serializers import BookRequestSerializer, BookResponseSerializer
@extend_schema(tags=['Booking & Tickets'])
class BookView(APIView):
    serializer_class = BookRequestSerializer

    @extend_schema(summary="Get available cities and bus changes")
    def get(self, request):
        buschanges_count = Buschange.objects.count()
        des = City.objects.all()

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckroutee.html', {
                'des': des,
                'buschanges_count': buschanges_count
            })

        return Response({
            'des': [city.name for city in des],
            'buschanges_count': buschanges_count
        }, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Search for available routes",
        request=BookRequestSerializer,
        responses={200: BookResponseSerializer}
    )
    def post(self, request):
        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        try:
            incoming_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return self.handle_error(request, "Invalid date format. Use YYYY-MM-DD.", status.HTTP_400_BAD_REQUEST)

        if incoming_date < timezone.now().date():
            return self.handle_error(request, "Error: Past dates are not allowed.", status.HTTP_400_BAD_REQUEST)

        rout_qs = Route.objects.filter(depcity=depcity, descity=descity, date=date)
        buschanges_count = Buschange.objects.count()
        routes_list = []
        last_found_levels = None

        if rout_qs.exists():
            for route in rout_qs:
                buses = Bus.objects.filter(plate_no=route.plate_no)

                # Dynamic field extraction based on plate_no identification
                levels = buses.first().level if buses.exists() else "N/A"
                bus_name = buses.first().name if buses.exists() else "Luxury Fleet"

                last_found_levels = levels
                total_seats = sum(int(bus.no_seats or 0) for bus in buses)

                booked_tickets = Ticket.objects.filter(
                    depcity=route.depcity,
                    descity=route.descity,
                    date=route.date,
                    plate_no=route.plate_no
                ).count()

                remaining_seats = total_seats - booked_tickets

                if remaining_seats > 0:
                    routes_list.append({
                        'route': route,            # Accessible via item.route
                        'levels': levels,          # Accessible via item.levels
                        'name': bus_name,          # Accessible via item.name (Dynamically mapped)
                        'remaining_seats': remaining_seats
                    })

        if not routes_list:
            return self.handle_error(request, "There is no Travel for this information!", status.HTTP_404_NOT_FOUND)

        context = {
            'routes': routes_list,
            'levels': last_found_levels,
            'buschanges_count': buschanges_count
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/roote.html', context)
        return Response(context, status=status.HTTP_200_OK)

    def handle_error(self, request, message, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/cheeckroutee.html', {
                'des': City.objects.all(),
                'buschanges_count': Buschange.objects.count(),
                'error': message
            })
        return Response({"error": message}, status=status_code)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from .models import CustomUser, Buschange
from .serializers import AdminSerializer, AdminDeleteRequestSerializer
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['User Management'])
class AdminDeleteViews(APIView):
    serializer_class = AdminSerializer

    def get(self, request):
        # 1. INITIAL SECURITY CHECK
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # If the user is NOT the master admin 'henok', redirect to profile
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Restricted Access: Management privileges required.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        admins = CustomUser.objects.all()
        context = {
            'admins': admins,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if is_html:
            return render(request, 'users/admindelet.html', context)
        return Response(AdminSerializer(admins, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete an admin user",
        request=AdminDeleteRequestSerializer,
        responses={200: AdminSerializer(many=True)},
        description="Delete an admin user. Requires 'henok' clearance."
    )
    def post(self, request):
        # 1. INITIAL SECURITY CHECK
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA EXTRACTION & VALIDATION
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        username = request.data.get('username')

        # Protect last admin
        if CustomUser.objects.count() <= 1:
            error_msg = "Security Protocol: System requires at least one active controller."
            if is_html:
                return render(request, 'users/admindelet.html', {
                    'admins': CustomUser.objects.all(),
                    'error': error_msg,
                    'buschanges_count': buschanges_count
                })
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # 4. PERFORM ACTION
        deleted_count, _ = CustomUser.objects.filter(
            first_name=first_name,
            last_name=last_name,
            username=username
        ).delete()
        # 5. FINAL RESPONSE
        admins = CustomUser.objects.all()
        context = {
            'admins': admins,
            'buschanges_count': buschanges_count,
            'username': current_user.username,
            'success': "Access successfully revoked." if deleted_count > 0 else None,
            'error': "Controller not found in registry." if deleted_count == 0 else None
        }
        if is_html:
            return render(request, 'users/admindelet.html', context)
        return Response({'admins': AdminSerializer(admins, many=True).data}, status=status.HTTP_200_OK)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .models import Worker, Buschange, CustomUser # Added CustomUser
from .serializers import (
    WorkerDeleteRequestSerializer,
    WorkerListSerializer,
    WorkerDeleteResponseSerializer
)

@extend_schema(tags=['Bus & Driver Management'])
class Workerdelet(APIView):
    serializer_class = WorkerDeleteRequestSerializer

    @extend_schema(
        summary="List all workers available for deletion",
        responses={200: WorkerDeleteResponseSerializer}
    )
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to manage workers.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' has the authority to remove personnel from the database
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: Master Admin clearance required to delete personnel.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        workers = Worker.objects.all()
        context = {
            'admins': workers, 
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if is_html:
            if not workers.exists():
                context['error'] = "Worker Registry: No personnel records found."
            return render(request, 'users/workerdelete.html', context)

        workers_data = WorkerListSerializer(workers, many=True).data
        return Response({'admins': workers_data}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a specific worker",
        request=WorkerDeleteRequestSerializer,
        responses={200: WorkerDeleteResponseSerializer}
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please re-authenticate.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA EXTRACTION & DELETION
        fname = request.data.get('fname')
        lname = request.data.get('lname')
        username = request.data.get('username')

        deleted_count, _ = Worker.objects.filter(
            fname=fname,
            lname=lname,
            username=username
        ).delete()

        # 4. REFRESH REGISTRY & PREPARE CONTEXT
        updated_workers = Worker.objects.all()
        context = {
            'admins': updated_workers,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if deleted_count > 0:
            context['success'] = "Registry Update: Personnel record purged successfully."
            res_status = status.HTTP_200_OK
        else:
            context['error'] = "Registry Error: Target worker not found."
            res_status = status.HTTP_404_NOT_FOUND

        # 5. RESPONSE
        if is_html:
            return render(request, 'users/workerdelete.html', context)
        return Response(context, status=res_status)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .models import CustomUser, Sc, Buschange  # Added CustomUser for privilege check
from .serializers import ScDeleteRequestSerializer
@extend_schema(tags=['SC Management'])
class ScDeleteViews(APIView):
    serializer_class = ScDeleteRequestSerializer
    @extend_schema(summary="List all SCs for deletion page")
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login to manage SC registry.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Restriction Logic: Only 'henok' can decommission Share Companies
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: Master Admin clearance required for SC Management.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        sc_list = Sc.objects.all()
        context = {
            'admins': sc_list,  # Using 'admins' to match your template variable name
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if not sc_list.exists():
            context['error'] = "No Share Companies currently registered in the system."
        if is_html:
            return render(request, 'users/scdelet.html', context)
        return Response({"sc_registry": list(sc_list.values())}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Decommission a Share Company",
        request=ScDeleteRequestSerializer,
        responses={200: dict, 404: dict}
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please re-authenticate.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA EXTRACTION
        firstname = request.data.get('firstname')
        name = request.data.get('name')
        lastname = request.data.get('lastname')

        # 4. PERFORM DELETION (Decommissioning)
        deleted_count, _ = Sc.objects.filter(
            firstname=firstname,
            lastname=lastname,
            name=name
        ).delete()
        # 5. REFRESH REGISTRY & PREPARE CONTEXT
        sc_list = Sc.objects.all()
        context = {
            'admins': sc_list,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if deleted_count > 0:
            context['success'] = "Share Company successfully decommissioned from registry."
            res_status = status.HTTP_200_OK
        else:
            context['error'] = "Entity not found. Verification failed."
            res_status = status.HTTP_404_NOT_FOUND
        # 6. RESPONSE
        if is_html:
            return render(request, 'users/scdelet.html', context)        
        return Response({'message': context.get('success') or context.get('error')}, status=res_status)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from .models import Route, Ticket, Buschange, CustomUser  # Added CustomUser
from .serializers import RouteSerializer, RouteDeleteRequestSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Routes & Cities'])
class RouteDeleteViews(APIView):
    serializer_class = RouteSerializer
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login to manage logistical routes.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: You do not have clearance to modify route logistics.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        routes = Route.objects.all()
        context = {
            'routes': routes,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if is_html:
            if routes.exists():
                return render(request, 'users/routedelete.html', context)
            context['error'] = "Logistics Registry: No active routes found."
            return render(request, 'users/routedelete.html', context)

        return Response(RouteSerializer(routes, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a route",
        request=RouteDeleteRequestSerializer,
        responses={200: RouteSerializer(many=True)},
        description="Delete a route. Requires 'henok' clearance and zero active ticket bookings."
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Authentication required.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA EXTRACTION
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')

        # 4. INTEGRITY CHECK (Check for active bookings)
        booked_tickets = Ticket.objects.filter(
            depcity=depcity, descity=descity, date=date,
            plate_no=plate_no, side_no=side_no
        ).exists()

        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if booked_tickets:
            context['error'] = "Deletion Blocked: Active bookings detected for this route."
            res_status = status.HTTP_400_BAD_REQUEST
        else:
            # 5. PERFORM DELETION
            rows_deleted, _ = Route.objects.filter(
                depcity=depcity, descity=descity, date=date,
                plate_no=plate_no, side_no=side_no
            ).delete()

            if rows_deleted > 0:
                context['success'] = "Logistics Update: Route successfully purged from registry."
                res_status = status.HTTP_200_OK
            else:
                context['error'] = "Registry Error: Matching route could not be located."
                res_status = status.HTTP_404_NOT_FOUND

        # 6. FINAL RESPONSE
        context['routes'] = Route.objects.all()
        if is_html:
            return render(request, 'users/routedelete.html', context)

        return Response({
            'message': context.get('success') or context.get('error'),
            'data': RouteSerializer(context['routes'], many=True).data
        }, status=res_status)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Ticket, Route, Buschange # Added Buschange
from .serializers import TicketSearchSerializer, TickSerializer
@extend_schema(tags=['Booking & Tickets'])
class ShowTicketsViews(APIView):
    serializer_class = TicketSearchSerializer
    @extend_schema(summary="Show initial ticket search page")
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to view tickets.',
                'buschanges_count': buschanges_count
            })

        return render(request, 'users/ticketoche.html', {
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        })

    @extend_schema(
        summary="Search for booked tickets",
        request=TicketSearchSerializer,
        responses={200: TickSerializer(many=True)}
    )
    def post(self, request):
        # 2. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 3. DATA EXTRACTION
        plate_no = request.data.get('plate_no')
        side_no = request.data.get('side_no')
        date = request.data.get('date')
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')

        # 4. QUERYING
        route_tickets = Ticket.objects.filter(
            plate_no=plate_no,
            side_no=side_no,
            date=date,
            depcity=depcity,
            descity=descity
        )
        
        # Fallback query if no tickets are found
        alt_routes = Route.objects.filter(side_no=side_no)

        # 5. RESPONSE LOGIC
        if is_html:
            if route_tickets.exists():
                return render(request, 'users/ticketoche.html', {
                    'route': route_tickets,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })
            else:
                return render(request, 'users/rooteee.html', {
                    'error': 'There are no booked tickets for this route',
                    'routes': alt_routes,
                    'buschanges_count': buschanges_count,
                    'username': request.session.get('username')
                })

        # API JSON Response
        if route_tickets.exists():
            data = TickSerializer(route_tickets, many=True).data
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "There are no booked tickets for this route"},
                status=status.HTTP_404_NOT_FOUND
            )





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import City, Buschange # Added Buschange for notification count
from .serializers import CitySerializer
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['Routes & Cities'])
class CityDeleteViews(APIView):
    serializer_class = CitySerializer
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage cities.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA
        cities = City.objects.all()
        context = {
            'cities': cities,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/citydelet.html', context)
        
        serializer = self.serializer_class(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. DELETION LOGIC
        depcity_name = request.data.get('depcity')
        
        try:
            city_instance = City.objects.get(depcity=depcity_name)
            city_instance.delete()
            success_msg = f'City "{depcity_name}" Deleted Successfully'
            res_status = status.HTTP_200_OK
            error_msg = None
        except City.DoesNotExist:
            success_msg = None
            error_msg = 'City not found. No deletion performed.'
            res_status = status.HTTP_404_NOT_FOUND

        # 5. REFRESH LIST & PREPARE CONTEXT
        cities = City.objects.all()
        context = {
            'cities': cities,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username'),
            'success': success_msg,
            'error': error_msg
        }
        # 6. RESPONSE
        if is_html:
            return render(request, 'users/citydelet.html', context)
        return Response({
            'message': success_msg or error_msg,
            'remaining_cities': CitySerializer(cities, many=True).data
        }, status=res_status)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from .models import City, Buschange, CustomUser  # Added CustomUser
from .serializers import CitySerializer
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['Routes & Cities'])
class CityDeleteViews(APIView):
    serializer_class = CitySerializer
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login to manage terminal hubs.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Restriction: Only 'henok' has the authority to purge cities from the network
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Alert: Master Admin clearance required for City Registry management.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        cities = City.objects.all()
        context = {
            'cities': cities,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if is_html:
            return render(request, 'users/citydelet.html', context)
        serializer = self.serializer_class(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Re-authentication required for destructive actions.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        # 3. DELETION LOGIC (Registry Decommissioning)
        depcity_name = request.data.get('depcity')
        try:
            city_instance = City.objects.get(depcity=depcity_name)
            city_instance.delete()
            success_msg = f'Hub Registry Update: "{depcity_name}" successfully decommissioned.'
            res_status = status.HTTP_200_OK
            error_msg = None
        except City.DoesNotExist:
            success_msg = None
            error_msg = 'Hub Registry Error: Target city not found in system database.'
            res_status = status.HTTP_404_NOT_FOUND

        # 4. REFRESH LIST & PREPARE CONTEXT
        cities = City.objects.all()
        context = {
            'cities': cities,
            'buschanges_count': buschanges_count,
            'username': current_user.username,
            'success': success_msg,
            'error': error_msg
        }
        # 5. FINAL RESPONSE
        if is_html:
            return render(request, 'users/citydelet.html', context)

        return Response({
            'message': success_msg or error_msg,
            'remaining_cities': CitySerializer(cities, many=True).data
        }, status=res_status)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from .models import Feedback, Buschange, CustomUser  # Added CustomUser
from .serializers import CommentDeleteSerializer
from drf_spectacular.utils import extend_schema
@extend_schema(tags=['Feedback Management'])
class CommentDeleteViews(APIView):
    serializer_class = CommentDeleteSerializer

    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login to manage feedback registry.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Master Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to delete passenger feedback
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Restricted: Master Admin clearance required to purge feedback.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        comments = Feedback.objects.all()
        context = {
            'comments': comments,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if is_html:
            return render(request, 'users/commentdelet.html', context)

        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a feedback comment",
        request=CommentDeleteSerializer,
        responses={200: CommentDeleteSerializer(many=True)},
        description="Delete feedback. Requires 'henok' master clearance."
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Authentication required for data purging.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. VALIDATION & DELETION (Registry Maintenance)
        serializer = CommentDeleteSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']
            phone = serializer.validated_data['phone']
            registration_id = serializer.validated_data['registration_id']

            try:
                comment = Feedback.objects.get(
                    registration_id=registration_id,
                    name=name,
                    email=email,
                    phone=phone
                )
                comment.delete()
                success_msg = 'Feedback Registry Updated: Record successfully purged.'
                error_msg = None
                res_status = status.HTTP_200_OK
            except Feedback.DoesNotExist:
                success_msg = None
                error_msg = 'Registry Error: No matching feedback entry located.'
                res_status = status.HTTP_404_NOT_FOUND

            # 4. REFRESH LIST & PREPARE CONTEXT
            comments = Feedback.objects.all()
            context = {
                'comments': comments,
                'buschanges_count': buschanges_count,
                'username': current_user.username,
                'success': success_msg,
                'error': error_msg
            }

            if is_html:
                return render(request, 'users/commentdelet.html', context)

            return Response(
                {
                    'message': success_msg or error_msg,
                    'comments': CommentDeleteSerializer(comments, many=True).data
                },
                status=res_status
            )

        # Handle Serializer Errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .serializers import UserSerializer
from .models import Buschange, CustomUser  # Added CustomUser for clearance check
class UrRegisterView(APIView):
    serializer_class = UserSerializer
    @extend_schema(summary="Show registration page")
    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to access user registration.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Restriction: Only 'henok' can authorize new account creation
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required to register new users.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED: Render the registration page
        return render(request, 'users/register.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    @extend_schema(
        summary="Register a new user",
        request=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please re-authenticate.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION & REGISTRATION
        serializer = UserSerializer(data=request.data)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if serializer.is_valid():
            serializer.save()
            context['success'] = 'User Account initialized successfully in the master registry.'

            if is_html:
                return render(request, 'users/register.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)

        # 4. HANDLE VALIDATION ERRORS
        context['error'] = serializer.errors
        if is_html:
            return render(request, 'users/register.html', context)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




"""
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange
from .serializers import (BusChangeInputSerializer, BusChangeResponseSerializer)

@extend_schema(tags=['Bus & Driver Management'])
class ChangesBusView(APIView):

    @extend_schema(
        summary="Get list of all routes and buses matching tier levels",
        responses={200: BusChangeResponseSerializer}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to change buses.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA WITH EXACT LEVEL FIELDS
        routes = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        context = {
            'routes': routes,
            'buses': buses,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)

        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Execute bus change validation based on matching level hierarchies",
        request=BusChangeInputSerializer,
        responses={200: BusChangeResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. VALIDATION
        serializer = BusChangeInputSerializer(data=request.data)
        routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses_list = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        if not serializer.is_valid():
            return self._handle_response(request, {
                'error': serializer.errors,
                'routes': routes_list,
                'buses': buses_list
            }, status.HTTP_400_BAD_REQUEST)

        # 5. DATA EXTRACTION
        data = serializer.validated_data
        depcity = data['depcity']
        descity = data['descity']
        date_obj = data['date']
        side_no = data['side_no']
        new_side_no = data['new_side_no']

        try:
            # Check if target route exists
            route = Route.objects.get(depcity=depcity, descity=descity, date=date_obj, side_no=side_no)

            # Find the level profile of the original assigned bus
            current_bus = Bus.objects.filter(sideno=side_no).first()
            if not current_bus:
                return self._handle_response(request, {
                    'error': f"Original bus with side number {side_no} not found in repository.",
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # Find the new bus profile
            new_bus_info = Bus.objects.filter(sideno=new_side_no).first()
            if not new_bus_info:
                return self._handle_response(request, {
                    'error': 'Selected new side number does not exist.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # CRITICAL ENFORCEMENT: Level strings must match exactly
            if str(current_bus.level).strip().lower() != str(new_bus_info.level).strip().lower():
                return self._handle_response(request, {
                    'error': f"Level mismatch! You can only swap with a '{current_bus.level}' bus.",
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # Check availability conflicts for the targeted swap date
            if Route.objects.filter(side_no=new_side_no, date=date_obj).exists():
                return self._handle_response(request, {
                    'error': 'This replacement bus is already reserved on this date.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            new_plate_no = new_bus_info.plate_no
            total_seats = int(new_bus_info.no_seats) if new_bus_info.no_seats else 0

            # 6. UPDATE LOGIC (Route & Associated Tickets)
            route.plate_no = new_plate_no
            route.side_no = new_side_no
            route.save()

            # Handle Return Routing Logistics (Addisababa Next-Day Sequence)
            if depcity.strip() == "Addisababa":
                next_day = date_obj + timedelta(days=1)
                Route.objects.filter(depcity=descity, descity=depcity, date=next_day, side_no=side_no).update(
                    plate_no=new_plate_no, side_no=new_side_no
                )

            # Update structural manifests
            Ticket.objects.filter(date=date_obj, side_no=side_no).update(
                plate_no=new_plate_no, side_no=new_side_no
            )

            # Log Audit Trail
            Buschange.objects.create(
                plate_no=side_no,
                side_no=side_no,
                new_plate_no=new_plate_no,
                new_side_no=new_side_no,
                date=date_obj,
                depcity=depcity,
                descity=descity
            )

            # Refresh list dataset context parameters
            new_routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
            return self._handle_response(request, {
                'success': 'Bus level verified and swapped successfully.',
                'total_seats': total_seats,
                'routes': new_routes_list,
                'buses': buses_list
            }, status.HTTP_200_OK)

        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': "Original transaction route deployment mapping not found.",
                'routes': routes_list, 'buses': buses_list
            }, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status_code)
"""


from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange
from .serializers import (BusChangeInputSerializer, BusChangeResponseSerializer)

@extend_schema(tags=['Bus & Driver Management'])
class ChangesBusView(APIView):

    @extend_schema(
        summary="Get list of all routes and buses",
        responses={200: BusChangeResponseSerializer}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to change buses.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA WITH COMPATIBLE TEMPLATE PROPERTY FIELDS
        routes = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        context = {
            'routes': routes,
            'buses': buses,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)

        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Execute bus change",
        request=BusChangeInputSerializer,
        responses={200: BusChangeResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. VALIDATION
        serializer = BusChangeInputSerializer(data=request.data)
        routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses_list = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        if not serializer.is_valid():
            return self._handle_response(request, {
                'error': serializer.errors,
                'routes': routes_list,
                'buses': buses_list
            }, status.HTTP_400_BAD_REQUEST)

        # 5. DATA EXTRACTION
        data = serializer.validated_data
        depcity = data['depcity']
        descity = data['descity']
        date_obj = data['date']
        side_no = data['side_no']
        new_side_no = data['new_side_no']

        try:
            # Check availability
            if Route.objects.filter(side_no=new_side_no, date=date_obj).exists():
                return self._handle_response(request, {
                    'error': 'This bus is already reserved for this date.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            bus_info = Bus.objects.filter(sideno=new_side_no).first()
            if not bus_info:
                return self._handle_response(request, {
                    'error': 'Invalid side number.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            new_plate_no = bus_info.plate_no
            total_seats = int(bus_info.no_seats) if bus_info.no_seats else 0

            # 6. UPDATE LOGIC (Route & Tickets)
            route = Route.objects.get(depcity=depcity, descity=descity, date=date_obj, side_no=side_no)
            route.plate_no = new_plate_no
            route.side_no = new_side_no
            route.save()

            # Handle Addisababa Return Logic
            if depcity.strip() == "Addisababa":
                next_day = date_obj + timedelta(days=1)
                Route.objects.filter(depcity=descity, descity=depcity, date=next_day, side_no=side_no).update(
                    plate_no=new_plate_no, side_no=new_side_no
                )

            # Update all associated tickets
            Ticket.objects.filter(date=date_obj, side_no=side_no).update(
                plate_no=new_plate_no, side_no=new_side_no
            )

            # Log the change
            Buschange.objects.create(
                plate_no=side_no,
                side_no=side_no,
                new_plate_no=new_plate_no,
                new_side_no=new_side_no,
                date=date_obj,
                depcity=depcity,
                descity=descity
            )

            # Refresh list for UI
            new_routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
            return self._handle_response(request, {
                'success': 'Bus changed successfully.',
                'total_seats': total_seats,
                'routes': new_routes_list,
                'buses': buses_list
            }, status.HTTP_200_OK)

        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': "Original route not found.",
                'routes': routes_list, 'buses': buses_list
            }, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status_code)



"""
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange
from .serializers import (BusChangeInputSerializer, BusChangeResponseSerializer)

@extend_schema(tags=['Bus & Driver Management'])
class ChangesBusView(APIView):
    
    @extend_schema(
        summary="Get list of all routes and buses matching tier levels",
        responses={200: BusChangeResponseSerializer}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to change buses.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA WITH EXACT LEVEL FIELDS
        routes = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        # Include level, name, sideno, and plate_no to manage dependencies via JS
        buses = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        context = {
            'routes': routes,
            'buses': buses,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)

        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Execute bus change validation based on matching level hierarchies",
        request=BusChangeInputSerializer,
        responses={200: BusChangeResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. VALIDATION
        serializer = BusChangeInputSerializer(data=request.data)
        routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses_list = list(Bus.objects.all().values('level', 'name', 'sideno', 'plate_no', 'no_seats'))

        if not serializer.is_valid():
            return self._handle_response(request, {
                'error': serializer.errors,
                'routes': routes_list,
                'buses': buses_list
            }, status.HTTP_400_BAD_REQUEST)

        # 5. DATA EXTRACTION
        data = serializer.validated_data
        depcity = data['depcity']
        descity = data['descity']
        date_obj = data['date']
        side_no = data['side_no']
        new_side_no = data['new_side_no']

        try:
            # Check if target route exists
            route = Route.objects.get(depcity=depcity, descity=descity, date=date_obj, side_no=side_no)
            
            # Find the level profile of the original assigned bus
            current_bus = Bus.objects.filter(sideno=side_no).first()
            if not current_bus:
                return self._handle_response(request, {
                    'error': f"Original bus with side number {side_no} not found in repository.",
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # Find the new bus profile
            new_bus_info = Bus.objects.filter(sideno=new_side_no).first()
            if not new_bus_info:
                return self._handle_response(request, {
                    'error': 'Selected new side number does not exist.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # CRITICAL ENFORCEMENT: Level strings must match exactly
            if str(current_bus.level).strip().lower() != str(new_bus_info.level).strip().lower():
                return self._handle_response(request, {
                    'error': f"Level mismatch! You can only swap with a '{current_bus.level}' bus.",
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            # Check availability conflicts for the targeted swap date
            if Route.objects.filter(side_no=new_side_no, date=date_obj).exists():
                return self._handle_response(request, {
                    'error': 'This replacement bus is already reserved on this date.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            new_plate_no = new_bus_info.plate_no
            total_seats = int(new_bus_info.no_seats) if new_bus_info.no_seats else 0

            # 6. UPDATE LOGIC (Route & Associated Tickets)
            route.plate_no = new_plate_no
            route.side_no = new_side_no
            route.save()

            # Handle Return Routing Logistics (Addisababa Next-Day Sequence)
            if depcity.strip() == "Addisababa":
                next_day = date_obj + timedelta(days=1)
                Route.objects.filter(depcity=descity, descity=depcity, date=next_day, side_no=side_no).update(
                    plate_no=new_plate_no, side_no=new_side_no
                )

            # Update structural manifests
            Ticket.objects.filter(date=date_obj, side_no=side_no).update(
                plate_no=new_plate_no, side_no=new_side_no
            )

            # Log Audit Trail
            Buschange.objects.create(
                plate_no=side_no,
                side_no=side_no,
                new_plate_no=new_plate_no,
                new_side_no=new_side_no,
                date=date_obj,
                depcity=depcity,
                descity=descity
            )

            # Refresh list dataset context parameters
            new_routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
            return self._handle_response(request, {
                'success': 'Bus level verified and swapped successfully.',
                'total_seats': total_seats,
                'routes': new_routes_list,
                'buses': buses_list
            }, status.HTTP_200_OK)

        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': "Original transaction route deployment mapping not found.",
                'routes': routes_list, 'buses': buses_list
            }, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status_code)

"""

"""
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange
from .serializers import (BusChangeInputSerializer, BusChangeResponseSerializer)
@extend_schema(tags=['Bus & Driver Management'])
class ChangesBusView(APIView):
    @extend_schema(
        summary="Get list of all routes and buses",
        responses={200: BusChangeResponseSerializer}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to change buses.',
                'buschanges_count': buschanges_count
            })
        # 2. FETCH DATA
        routes = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses = list(Bus.objects.all().values('sideno', 'plate_no', 'no_seats'))

        context = {
            'routes': routes,
            'buses': buses,
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)

        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Execute bus change",
        request=BusChangeInputSerializer,
        responses={200: BusChangeResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. VALIDATION
        serializer = BusChangeInputSerializer(data=request.data)
        routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
        buses_list = list(Bus.objects.all().values('sideno', 'plate_no', 'no_seats'))

        if not serializer.is_valid():
            return self._handle_response(request, {
                'error': serializer.errors,
                'routes': routes_list,
                'buses': buses_list
            }, status.HTTP_400_BAD_REQUEST)

        # 5. DATA EXTRACTION
        data = serializer.validated_data
        depcity = data['depcity']
        descity = data['descity']
        date_obj = data['date']
        date_str = date_obj.strftime('%Y-%m-%d')
        side_no = data['side_no']
        new_side_no = data['new_side_no']
        try:
            # Check availability
            if Route.objects.filter(side_no=new_side_no, date=date_obj).exists():
                return self._handle_response(request, {
                    'error': 'This bus is already reserved for this date.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            bus_info = Bus.objects.filter(sideno=new_side_no).first()
            if not bus_info:
                return self._handle_response(request, {
                    'error': 'Invalid side number.',
                    'routes': routes_list, 'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)

            new_plate_no = bus_info.plate_no
            total_seats = int(bus_info.no_seats) if bus_info.no_seats else 0

            # 6. UPDATE LOGIC (Route & Tickets)
            route = Route.objects.get(depcity=depcity, descity=descity, date=date_obj, side_no=side_no)
            route.plate_no = new_plate_no
            route.side_no = new_side_no
            route.save()

            # Handle Addisababa Return Logic
            if depcity.strip() == "Addisababa":
                next_day = date_obj + timedelta(days=1)
                Route.objects.filter(depcity=descity, descity=depcity, date=next_day, side_no=side_no).update(
                    plate_no=new_plate_no, side_no=new_side_no
                )

            # Update all associated tickets
            Ticket.objects.filter(date=date_obj, side_no=side_no).update(
                plate_no=new_plate_no, side_no=new_side_no
            )

            # Log the change
            Buschange.objects.create(
                plate_no=side_no,
                side_no=side_no,
                new_plate_no=new_plate_no,
                new_side_no=new_side_no,
                date=date_obj,
                depcity=depcity,
                descity=descity
            )
            # Refresh list for UI
            new_routes_list = list(Route.objects.all().values('depcity', 'descity', 'date', 'side_no', 'plate_no'))
            return self._handle_response(request, {
                'success': 'Bus changed successfully.',
                'total_seats': total_seats,
                'routes': new_routes_list,
                'buses': buses_list
            }, status.HTTP_200_OK)
        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': "Original route not found.",
                'routes': routes_list, 'buses': buses_list
            }, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        # Add notification and user info to every response
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status_code)
"""




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .models import Sc, Service_fee, Buschange, CustomUser  # Added CustomUser
from .serializers import (
    ScSerializer,
    ServiceFeeSerializer,
    ServiceUpdateInputSerializer,
    ServiceFeeSimpleSerializer
)
class Serviceupdate(APIView):
    @extend_schema(
        tags=['Service Management'],
        summary="List all service fees",
        responses={200: ServiceFeeSimpleSerializer(many=True)}
    )
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to manage service fees.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to view or manage global service fees
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: Master Admin clearance required for financial management.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        routes = Sc.objects.all()
        buses = Service_fee.objects.all()

        context = {
            'routes': ScSerializer(routes, many=True).data,
            'buses': ServiceFeeSerializer(buses, many=True).data,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if is_html:
            return render(request, 'users/update_service_fee.html', context)

        return Response(context['buses'], status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Service Management'],
        summary="Update an existing service fee",
        request=ServiceUpdateInputSerializer,
        responses={200: ServiceFeeSimpleSerializer}
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA EXTRACTION
        service_fee_val = request.data.get('service_fee')
        new_service_fee = request.data.get('new_service_fee')

        # Prepare base context for response
        routes = Sc.objects.all()
        buses = Service_fee.objects.all()
        context_data = {
            'routes': ScSerializer(routes, many=True).data,
            'buses': ServiceFeeSerializer(buses, many=True).data,
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        # 4. UPDATE LOGIC (Financial Protocol Adjustment)
        try:
            # Check for duplicate tariff values
            if Service_fee.objects.filter(service_fee=new_service_fee).exists():
                context_data['error'] = 'Tariff Registry: This service fee already exists.'
                return self._handle_response(request, context_data, status.HTTP_400_BAD_REQUEST)

            # Perform Update
            sc_fee_instance = Service_fee.objects.get(service_fee=service_fee_val)
            sc_fee_instance.service_fee = new_service_fee
            sc_fee_instance.save()

            # Refresh registry for the view
            context_data['buses'] = ServiceFeeSerializer(Service_fee.objects.all(), many=True).data
            context_data['success'] = 'Financial Update: Service fee modified successfully.'
            return self._handle_response(request, context_data)

        except Service_fee.DoesNotExist:
            context_data['error'] = 'Registry Error: Original service fee record not found.'
            return self._handle_response(request, context_data, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code=status.HTTP_200_OK):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/update_service_fee.html', context)
        return Response(context, status=status_code)








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Buschange # Added Buschange for notification count
from .serializers import ActivateRequestSerializer, ActivateResponseSerializer
@extend_schema(tags=['Bus & Driver Management'])
class Activate(APIView):
    serializer_class = ActivateRequestSerializer

    @extend_schema(
        summary="Load activation search page",
        responses={200: ActivateResponseSerializer}
    )
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage status.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA
        buses = Bus.objects.all()
        context = {
            'buses': list(buses),
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/status.html', context)

        return Response({'message': 'Please POST a date to search for routes.'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Fetch routes by date",
        request=ActivateRequestSerializer,
        responses={200: ActivateResponseSerializer}
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. DATA EXTRACTION
        date = request.data.get('date')
        routes = Route.objects.filter(date=date)
        buses = Bus.objects.all()

        # 5. RESPONSE PREPARATION
        context = {
            'buschanges_count': buschanges_count,
            'username': request.session.get('username'),
            'buses': list(buses)
        }

        if is_html:
            if routes.exists():
                context['routes'] = list(routes)
                return render(request, 'users/activity.html', context)
            else:
                context['error'] = 'No routes found for the specified date.'
                return render(request, 'users/status.html', context)

        # API JSON Response
        if routes.exists():
            data = [{
                'departure': r.depcity,
                'destination': r.descity,
                'date': r.date,
                'side_no': r.side_no
            } for r in routes]

            return Response({
                'routes': data,
                'buses_count': buses.count()
            }, status=status.HTTP_200_OK)

        return Response(
            {'error': 'No routes found for the specified date.'},
            status=status.HTTP_404_NOT_FOUND
        )







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema

from .models import Route, Bus, Buschange # Added Buschange for notification count
from .serializers import ActivateStatusUpdateSerializer
@extend_schema(tags=['Bus & Driver Management'])
class Activates(APIView):
    serializer_class = ActivateStatusUpdateSerializer

    @extend_schema(summary="Get all active routes and buses")
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()

        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to manage route status.',
                'buschanges_count': buschanges_count
            })

        # 2. FETCH DATA
        routes = Route.objects.all().values()
        buses = Bus.objects.all().values()
        
        context = {
            'routes': list(routes),
            'buses': list(buses),
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/activity.html', context)
        
        return Response({'routes': list(routes), 'buses': list(buses)}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update the active status of a route",
        request=ActivateStatusUpdateSerializer
    )
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 4. DATA EXTRACTION
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date_str = request.data.get('date')
        kilometer = request.data.get('kilometer')
        price = request.data.get('price')
        plate_no = request.data.get('plate_no')
        
        # Robust Boolean Conversion
        raw_is_active = request.data.get('is_active')
        is_active = str(raw_is_active).lower() in ['true', '1', 'on']

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return self._handle_response(request, {
                'error': 'Invalid date format. Use YYYY-MM-DD.'
            }, status_code=status.HTTP_400_BAD_REQUEST)

        # 5. UPDATE LOGIC
        try:
            route_instance = Route.objects.get(
                depcity=depcity,
                descity=descity,
                date=target_date,
                kilometer=kilometer,
                plate_no=plate_no,
                price=price
            )
            route_instance.is_active = is_active
            route_instance.save()

            # Refresh lists for UI
            updated_routes = Route.objects.filter(date=target_date).values()
            all_buses = Bus.objects.all().values()

            return self._handle_response(request, {
                'success': f"Route status updated to {'Active' if is_active else 'Inactive'}.",
                'routes': list(updated_routes),
                'buses': list(all_buses)
            })

        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': 'Route not found with the specified details.'
            }, status_code=status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code=status.HTTP_200_OK):
        # 6. UNIFIED RESPONSE CONTEXT
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/activity.html', context)
        return Response(context, status=status_code)






from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange, Sc, CustomUser # Added CustomUser
from .serializers import ScUpdateSerializer
@extend_schema(tags=['SC Management'])
class Scchange(APIView):
    serializer_class = ScUpdateSerializer
    @extend_schema(summary="Get all SC and Bus data")
    def get(self, request):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to manage SC accounts.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to manage Share Company global data
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: Master Admin clearance required for SC credential management.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED DATA FETCH
        routes = Sc.objects.all().values()
        buses = Bus.objects.all().values()
        context = {
            'routes': list(routes),
            'buses': list(buses),
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if is_html:
            return render(request, 'users/scchange.html', context)
        return Response(context, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update SC Email",
        request=ScUpdateSerializer,
        responses={200: ScUpdateSerializer}
    )
    def post(self, request):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please re-authenticate.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        # 3. DATA EXTRACTION
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        name = request.data.get('name')
        email = request.data.get('email')
        new_email = request.data.get('new_email')
        # Initial lists for context
        routes_list = list(Sc.objects.all().values())
        buses_list = list(Bus.objects.all().values())

        try:
            # 4. UNIQUE EMAIL CHECK (Data Integrity)
            if Sc.objects.filter(email=new_email).exclude(email=email).exists():
                return self._handle_response(request, {
                    'error': 'Security Alert: This email is already reserved for another registry.',
                    'routes': routes_list,
                    'buses': buses_list
                }, status.HTTP_400_BAD_REQUEST)
            # 5. UPDATE LOGIC
            sc_user = Sc.objects.get(
                firstname=firstname,
                name=name,
                lastname=lastname,
                email=email
            )
            sc_user.email = new_email
            sc_user.save()

            # Refresh data after update
            updated_routes = list(Sc.objects.all().values())
            return self._handle_response(request, {
                'success': 'Credential Registry: SC email updated successfully!',
                'routes': updated_routes,
                'buses': buses_list
            }, status.HTTP_200_OK)
        except Sc.DoesNotExist:
            return self._handle_response(request, {
                'error': 'Registry Error: SC record not found. Verify details.',
                'routes': routes_list,
                'buses': buses_list
            }, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code=status.HTTP_200_OK):
        context['buschanges_count'] = Buschange.objects.count()
        # Security: Pull username from database session, not request params
        user_id = request.session.get('user_id')
        try:
            context['username'] = CustomUser.objects.get(id=user_id).username
        except:
            context['username'] = "Master Admin"

        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/scchange.html', context)
        return Response(context, status=status_code)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import City, Buschange
from .serializers import (
    BusChangeSearchSerializer,
    BusChangeResponseSerializer,
    BusChangeDetailSerializer
)
@extend_schema(tags=['Bus & Driver Management'])
class ChangeBusesViews(APIView):
    serializer_class = BusChangeSearchSerializer

    @extend_schema(
        summary="Get cities for bus change search",
        responses={200: BusChangeResponseSerializer}
    )
    def get(self, request):
        des = City.objects.all()
        city_list = [city.name for city in des] # Use city.depcity if that is your model field

        return self._handle_response(request, {'des': des, 'city_names': city_list}, status.HTTP_200_OK)

    @extend_schema(
        summary="Search bus changes by date",
        request=BusChangeSearchSerializer,
        responses={
            200: BusChangeResponseSerializer,
            404: BusChangeResponseSerializer
        }
    )
    def post(self, request):
        date = request.data.get('date')
        buschanges = Buschange.objects.filter(date=date)

        if buschanges.exists():
            count = buschanges.count()
            serialized_buschanges = BusChangeDetailSerializer(buschanges, many=True).data
            context = {
                'count': count,
                'buschange': serialized_buschanges if 'text/html' not in request.META.get('HTTP_ACCEPT', '') else buschanges
            }
            return self._handle_response(request, context, status.HTTP_200_OK)
        else:
            buschanges_count = Buschange.objects.count()
            des = City.objects.all()
            context = {
                'buschanges_count': buschanges_count,
                'error1': "NO change buses for this travel date!",
                'des': des
            }
            return self._handle_response(request, context, status.HTTP_404_NOT_FOUND)

    def _handle_response(self, request, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/busschange.html', context)
        else:
            return Response(context, status=status_code)











from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from .models import City, Service_fee, Buschange, CustomUser # Added CustomUser
from .serializers import ServiceSerializer
class ServicInsertView(generics.GenericAPIView):
    queryset = Service_fee.objects.all()
    serializer_class = ServiceSerializer
    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to register service fees.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        # 2. PRIVILEGE VERIFICATION (Master Admin Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Restriction: Only 'henok' can define the global service fee
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Access Denied: Master Admin clearance required for financial initialization.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        # 3. AUTHORIZED: Render form
        return render(request, 'users/service_fee.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. VALIDATION & LOGIC
        serializer = self.get_serializer(data=request.data)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if serializer.is_valid():
            # Business Rule: Only one service fee allowed in the system registry
            if Service_fee.objects.exists():
                context['error'] = 'Tariff Conflict: A service fee is already registered. Please update the existing value.'
                res_status = status.HTTP_400_BAD_REQUEST
            else:
                serializer.save()
                context['success'] = 'Financial protocol updated: Service fee registered successfully.'
                res_status = status.HTTP_201_CREATED
        else:
            context['error'] = serializer.errors
            res_status = status.HTTP_400_BAD_REQUEST
        # 4. RESPONSE
        if is_html:
            return render(request, 'users/service_fee.html', context)
        return Response(context, status=res_status)



"""
from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Sc, Buschange, CustomUser  # Added CustomUser
from .serializers import scSerializer
class ScInsertViews(generics.GenericAPIView):
    queryset = Sc.objects.all()
    serializer_class = scSerializer
    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to access the Registry.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to initialize new Share Companies
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required to register new entities.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')
        # 3. AUTHORIZED: Render entry form
        return render(request, 'users/scc.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION
        serializer = self.get_serializer(data=request.data)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }
        if serializer.is_valid():
            name = serializer.validated_data['name']
            side = serializer.validated_data['side']
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            level = serializer.validated_data['level']
            # Business Logic: Uniqueness checks
            #if Sc.objects.filter(name__iexact=name).exists():
            #    context['error'] = 'Share Company Name already exists in National Registry.'
            if (
    (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(name__iexact=name, level__in=['1st', '2nd', '3rd']).exists()) or
    (level == 'Special Bus' and Sc.objects.filter(name__iexact=name, level='Special Bus').exists())
):
                context['error'] = f'Campany name "{name}" level "{level}" is already registered for this level category.'
                #context['error'] = f'Company name {name_html} level {level_html} is already registered for this level category.'
            #elif Sc.objects.filter(side__iexact=side).exists():
            #    context['error'] = 'Division Side ID already registered.'


            elif (
    (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(side__iexact=side, level__in=['1st', '2nd', '3rd']).exists()) or
    (level == 'Special Bus' and Sc.objects.filter(side__iexact=side, level='Special Bus').exists())
):
                context['error'] = f'Side "{side}" is already registered for this level category.'
            elif Sc.objects.filter(username__iexact=username).exists():
                context['error'] = 'System Username is already taken.'
            elif Sc.objects.filter(email__iexact=email).exists():
                context['error'] = 'Official Email is already registered.'
            if 'error' in context:
                if is_html: return render(request, 'users/scc.html', context)
                return Response({'error': context['error']}, status=status.HTTP_400_BAD_REQUEST)
            # 4. SAVE & RESPONSE
            serializer.save()
            context['success'] = 'Share Company Registored successfully.'   
            if is_html:
                return render(request, 'users/scc.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)
        # 5. HANDLE SERIALIZER ERRORS
        context['errors'] = serializer.errors
        if is_html:
            return render(request, 'users/scc.html', context)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""






"""
from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Sc, Buschange, CustomUser
from .serializers import scSerializer
class ScInsertViews(generics.GenericAPIView):
    queryset = Sc.objects.all()
    serializer_class = scSerializer

    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to access the Registry.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to initialize new Share Companies
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required to register new entities.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED: Render entry form
        return render(request, 'users/scc.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION (FIXED: Passed both POST payload and FILES data dict dictionary arrays)
        serializer = self.get_serializer(data=request.data, files=request.FILES)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            side = serializer.validated_data.get('side')
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            level = serializer.validated_data.get('level')

            # Business Logic: Uniqueness checks category verification
            if (
                (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(name__iexact=name, level__in=['1st', '2nd', '3rd']).exists()) or
                (level == 'Special Bus' and Sc.objects.filter(name__iexact=name, level='Special Bus').exists())
            ):
                context['error'] = f'Company name "{name}" is already registered for this level category.'

            elif (
                (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(side__iexact=side, level__in=['1st', '2nd', '3rd']).exists()) or
                (level == 'Special Bus' and Sc.objects.filter(side__iexact=side, level='Special Bus').exists())
            ):
                context['error'] = f'Side "{side}" is already registered for this level category.'

            elif Sc.objects.filter(username__iexact=username).exists():
                context['error'] = 'System Username is already taken.'

            elif email and Sc.objects.filter(email__iexact=email).exists():
                context['error'] = 'Official Email is already registered.'

            if 'error' in context:
                if is_html:
                    return render(request, 'users/scc.html', context)
                return Response({'error': context['error']}, status=status.HTTP_400_BAD_REQUEST)

            # 4. SAVE & RESPONSE (Triggers custom model file naming pipeline)
            serializer.save()
            context['success'] = 'Share Company Registered successfully.'
            if is_html:
                return render(request, 'users/scc.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)

        # 5. HANDLE SERIALIZER ERRORS
        context['errors'] = serializer.errors
        if is_html:
            return render(request, 'users/scc.html', context)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

from django.shortcuts import render, redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Sc, Buschange, CustomUser
from .serializers import scSerializer

class ScInsertViews(generics.GenericAPIView):
    queryset = Sc.objects.all()
    serializer_class = scSerializer
    # CRITICAL: Ensures DRF natively parses both text fields and binary image file uploads smoothly
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        # 1. INITIAL SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Unauthorized! Please login to access the Registry.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION (International Clearance)
        try:
            current_user = CustomUser.objects.get(id=user_id)
            # Only 'henok' is authorized to initialize new Share Companies
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count,
                        'error': 'Security Protocol: Master Admin clearance required to register new entities.'
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. AUTHORIZED: Render entry form
        return render(request, 'users/scc.html', {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        })

    def post(self, request, *args, **kwargs):
        # 1. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. PRIVILEGE VERIFICATION
        try:
            current_user = CustomUser.objects.get(id=user_id)
            if current_user.username != "henok":
                if is_html:
                    return render(request, 'users/profile.html', {
                        'user': current_user,
                        'buschanges_count': buschanges_count
                    })
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return redirect('login')

        # 3. DATA VALIDATION (FIXED: Standard DRF data instantiation maps files automatically)
        serializer = self.get_serializer(data=request.data)
        context = {
            'buschanges_count': buschanges_count,
            'username': current_user.username
        }

        if serializer.is_valid():
            # SAFE GET EXTRACTION: Prevents Python crash if fields are empty
            name = serializer.validated_data.get('name')
            side = serializer.validated_data.get('side')
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            level = serializer.validated_data.get('level')

            # Business Logic: Uniqueness checks category verification
            if (
                (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(name__iexact=name, level__in=['1st', '2nd', '3rd']).exists()) or
                (level == 'Special Bus' and Sc.objects.filter(name__iexact=name, level='Special Bus').exists())
            ):
                context['error'] = f'Company name "{name}" is already registered for this level category.'

            elif (
                (level in ['1st', '2nd', '3rd'] and Sc.objects.filter(side__iexact=side, level__in=['1st', '2nd', '3rd']).exists()) or
                (level == 'Special Bus' and Sc.objects.filter(side__iexact=side, level='Special Bus').exists())
            ):
                context['error'] = f'Side "{side}" is already registered for this level category.'

            elif Sc.objects.filter(username__iexact=username).exists():
                context['error'] = 'System Username is already taken.'

            elif email and Sc.objects.filter(email__iexact=email).exists():
                context['error'] = 'Official Email is already registered.'

            if 'error' in context:
                if is_html:
                    return render(request, 'users/scc.html', context)
                return Response({'error': context['error']}, status=status.HTTP_400_BAD_REQUEST)

            # 4. SAVE & RESPONSE
            serializer.save()
            context['success'] = 'Share Company Registered successfully.'
            if is_html:
                return render(request, 'users/scc.html', context)
            return Response({'success': context['success']}, status=status.HTTP_201_CREATED)

        # 5. HANDLE SERIALIZER ERRORS
        context['errors'] = serializer.errors
        if is_html:
            return render(request, 'users/scc.html', context)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from .models import Bus, Route, Ticket, Buschange
@extend_schema(tags=['Bus & Driver Management'])
class ChangeBusView(APIView):
    def get(self, request):
        # 1. SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        if not user_id:
            request.session.flush()
            return render(request, 'users/login.html', {
                'error': 'Unauthorized! Please login to perform bus changes.',
                'buschanges_count': buschanges_count
            })
        # 2. FETCH DATA
        routes = Route.objects.all().values()
        buses = Bus.objects.all().values()
        context = {
            'routes': list(routes),
            'buses': list(buses),
            'buschanges_count': buschanges_count,
            'username': request.session.get('username')
        }
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status.HTTP_200_OK)
    def post(self, request):
        # 3. POST SECURITY GATE
        user_id = request.session.get('user_id')
        buschanges_count = Buschange.objects.count()
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')
        if not user_id:
            request.session.flush()
            if is_html:
                return render(request, 'users/login.html', {
                    'error': 'Session expired. Please login again.',
                    'buschanges_count': buschanges_count
                })
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        # 4. DATA EXTRACTION
        depcity = request.data.get('depcity')
        descity = request.data.get('descity')
        date = request.data.get('date')
        side_no = request.data.get('side_no')
        new_side_no = request.data.get('new_side_no')
        try:
            # 5. INTEGRITY CHECKS
            # Check if new bus is already busy
            if Route.objects.filter(side_no=new_side_no, date=date).exists():
                return self._handle_response(request, {
                    'error': 'This bus is already reserved for a route on this date.'
                }, status.HTTP_400_BAD_REQUEST)
            bus_info = Bus.objects.filter(sideno=new_side_no).first()
            if not bus_info:
                return self._handle_response(request, {
                    'error': 'Invalid side number selected.'
                }, status.HTTP_400_BAD_REQUEST)
            new_plate_no = bus_info.plate_no
            total_seats = int(bus_info.no_seats) if bus_info.no_seats else 0
            # Seat Capacity Check
            booked_tickets_count = Ticket.objects.filter(date=date, side_no=side_no).count()
            if booked_tickets_count > total_seats:
                return self._handle_response(request, {
                    'error': f'Cannot change to this bus. It only has {total_seats} seats, but {booked_tickets_count} tickets are already booked.'
                }, status.HTTP_400_BAD_REQUEST)
            # 6. TRANSACTION LOGIC
            route = Route.objects.get(depcity=depcity, descity=descity, date=date, side_no=side_no)
            route.plate_no = new_plate_no
            route.side_no = new_side_no
            route.save()
            # Handle Addisababa Reciprocal Route (Next Day)
            if depcity.strip() == "Addisababa":
                try:
                    next_day = (timezone.datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                    reciprocal_route = Route.objects.get(
                        depcity=descity, descity=depcity, date=next_day, side_no=side_no
                    )
                    reciprocal_route.plate_no = new_plate_no
                    reciprocal_route.side_no = new_side_no
                    reciprocal_route.save()
                except Route.DoesNotExist:
                    pass # Or handle if reciprocal route is mandatory
            # Update Tickets
            Ticket.objects.filter(date=date, side_no=side_no).update(
                plate_no=new_plate_no, side_no=new_side_no
            )
            # Log the change
            Buschange.objects.create(
                plate_no=side_no, side_no=side_no, new_plate_no=new_plate_no,
                new_side_no=new_side_no, date=date, depcity=depcity, descity=descity
            )
            # Calculate Seat Availability for Response
            booked_tickets = Ticket.objects.filter(date=date, side_no=new_side_no).values_list('no_seat', flat=True)
            booked_seats = set(int(seat) for seat in booked_tickets if seat)
            remaining_seats = total_seats - len(booked_seats)
            return self._handle_response(request, {
                'success': 'Bus changed successfully.',
                'total_seats': total_seats,
                'booked_seats': len(booked_seats),
                'remaining_seats': remaining_seats,
                'routes': list(Route.objects.all().values()), # Refresh lists
                'buses': list(Bus.objects.all().values())
            }, status.HTTP_200_OK)
        except Route.DoesNotExist:
            return self._handle_response(request, {
                'error': "The specified route does not exist."
            }, status.HTTP_404_NOT_FOUND)
    def _handle_response(self, request, context, status_code=status.HTTP_200_OK):
        # 7. UNIFIED RESPONSE HANDLER
        context['buschanges_count'] = Buschange.objects.count()
        context['username'] = request.session.get('username')
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/buschange.html', context)
        return Response(context, status=status_code)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Bus, Worker, Route
def updatebus(request):
    buses = Bus.objects.all()  # Fetch all bus records
    success_message = None
    error_message = None
    if request.method == "POST":
        plate_no = request.POST.get('plate_no')
        new_sideno = request.POST.get('new_sideno')
        no_seats = request.POST.get('no_seats')
        try:
            bus = Bus.objects.get(plate_no=plate_no)
            if Bus.objects.filter(sideno=new_sideno).exists():
                error_message = 'This side no already exists.'
            else:
                bus.sideno = new_sideno
                bus.no_seats = no_seats
                bus.save()
                Worker.objects.filter(plate_no=plate_no).update(side_no=new_sideno)
                Route.objects.filter(plate_no=plate_no).update(side_no=new_sideno)
                success_message = 'Side No changed successfully!'
        except Bus.DoesNotExist:
            error_message = 'Bus not found.'
    return render(request, 'users/busupdate.html', {
        'buses': buses,
        'success_message': success_message,
        'error_message': error_message,
    })

from django.shortcuts import render
from rest_framework.decorators import api_view
from django.utils import timezone
from datetime import timedelta
from .models import Bus, Route, Ticket, Buschange
from .serializers import BusChangeSerializer
@api_view(['GET', 'POST'])
def changebus(request):
    context = {}
    if request.method == 'POST':
        serializer = BusChangeSerializer(data=request.data)
        if serializer.is_valid():
            depcity = request.data.get('depcity')
            descity = request.data.get('descity')
            date = request.data.get('date')
            side_no = request.data.get('side_no')
            new_side_no = request.data.get('new_side_no')
            try:
                if Route.objects.filter(side_no=new_side_no, date=date).exists():
                    context['error'] = 'This bus is already reserved for this route on this date.'
                else:
                    bus_info = Bus.objects.filter(sideno=new_side_no).first()
                    if not bus_info:
                        context['error'] = 'Invalid side number selected.'
                    else:
                        new_plate_no = bus_info.plate_no
                        total_seats = int(bus_info.no_seats) if bus_info.no_seats else 0

                        booked_tickets_count = Ticket.objects.filter(date=date, side_no=side_no).count()
                        if booked_tickets_count > total_seats:
                            context['error'] = 'Not enough seats available for this change.'
                        else:
                            route = Route.objects.get(depcity=depcity, descity=descity, date=date, side_no=side_no)
                            route.plate_no = new_plate_no
                            route.side_no = new_side_no
                            route.save()
                            if depcity.strip() == "Addisababa":
                                reciprocal_route = Route.objects.get(
                                    depcity=descity,
                                    descity=depcity,
                                    date=(timezone.datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'),
                                    side_no=side_no
                                )
                                reciprocal_route.plate_no = new_plate_no
                                reciprocal_route.side_no = new_side_no
                                reciprocal_route.save()

                            Ticket.objects.filter(date=date, side_no=side_no).update(
                                plate_no=new_plate_no,
                                side_no=new_side_no
                            )
                            booked_tickets = Ticket.objects.filter(date=date, side_no=new_side_no).values_list('no_seat', flat=True)
                            booked_seats = set(int(seat) for seat in booked_tickets)
                            booked_seat_count = len(booked_seats)
                            remaining_seats = total_seats - booked_seat_count
                            unbooked_seats = [seat for seat in range(1, total_seats + 1) if seat not in booked_seats]

                            Buschange.objects.create(
                                plate_no=side_no,
                                side_no=side_no,
                                new_plate_no=new_plate_no,
                                new_side_no=new_side_no,
                                date=date,
                                depcity=depcity,
                                descity=descity
                            )
                            context.update({
                                'success': 'Bus changed successfully.',
                                'total_seats': total_seats,
                                'booked_seats': booked_seat_count,
                                'remaining_seats': remaining_seats,
                                'unbooked_seats': unbooked_seats,
                                'booked_seat_list': booked_seats})

            except Route.DoesNotExist:
                context['error'] = "The specified route does not exist."
        else:
            context['error'] = serializer.errors
    return render(request, 'users/buschange.html', context)




from django.shortcuts import redirect
def changebus_redirect(request):
    return redirect('changebus')  # Replace with the actual URL name

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib import messages
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
@extend_schema(responses=TotalBalanceResponseSerializer) # Add this line
class ChangePasswordViews(LoginRequiredMixin, APIView):
    def get(self, request):
        return self._handle_response(request, {}, status.HTTP_200_OK)
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: {"detail": "Password updated."}}
    )
    def post(self, request):
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')
        re_new_password = request.data.get('reNewPassword')
        user = authenticate(username=request.user.username, password=current_password)
        if user is not None:
            if new_password == re_new_password:
                if current_password == new_password:
                    return self._handle_response(request, {
                        'error': "New password cannot be the same as the current password."
                    }, status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(new_password)  # Set the new password securely
                    user.save()  # Save the user instance
                    update_session_auth_hash(request, user)  # Important!
                    return self._handle_response(request, {
                        'success': "Your password has been changed successfully."
                    }, status.HTTP_200_OK)
            else:
                return self._handle_response(request, {
                    'error': "New passwords do not match."
                }, status.HTTP_400_BAD_REQUEST)
        else:
            return self._handle_response(request, {
                'error': "Current password is incorrect."
            }, status.HTTP_400_BAD_REQUEST)

    def _handle_response(self, request, context, status_code):
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'users/profile2.html', context)
        else:
            return Response(context, status=status_code)


from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .serializers import ChangePasswordSerializer, PasswordStatusSerializer
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Get password change page",
        responses={200: None},
        description="Renders the profile/password change HTML template."
    )
    def get(self, request):
        return render(request, 'users/profile2.html', {})

    @extend_schema(
        summary="Change user password",
        request=ChangePasswordSerializer,
        responses={
            200: PasswordStatusSerializer,
            400: PasswordStatusSerializer,
            403: PasswordStatusSerializer
        },
        description="Updates password. Supports both JSON API and HTML Form submissions."
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        is_html = 'text/html' in request.META.get('HTTP_ACCEPT', '')

        # 1. Validate Input (ISO 27002 Integrity)
        if not serializer.is_valid():
            if is_html:
                for field, errors in serializer.errors.items():
                    messages.error(request, f"{field}: {errors[0]}")
                return redirect('change_password')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Verify Identity (Proclamation 808/2013)
        current_pw = serializer.validated_data.get('currentPassword')
        user = authenticate(username=request.user.username, password=current_pw)
        if user is None:
            msg = "Current password is incorrect."
            if is_html:
                messages.error(request, msg)
                return redirect('change_password')
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
        # 3. Apply Change & Save
        request.user.set_password(serializer.validated_data['newPassword'])
        request.user.save()
        update_session_auth_hash(request, request.user)
        if is_html:
            messages.success(request, "Password updated successfully.")
            return redirect('profile')
        # 4. JSON Response (Fixed for Schema Audit)
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK
        )


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser  # Adjust the import as necessary
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')
        re_new_password = request.POST.get('reNewPassword')
        user = authenticate(username=request.user.username, password=current_password)
        if user is not None:
            if new_password == re_new_password:
                if current_password == new_password:
                    messages.error(request, "New password cannot be the same as the current password.")
                else:
                    user.set_password(new_password)  # Set the new password securely
                    user.save()  # Save the user instance
                    update_session_auth_hash(request, user)  # Important!
                    messages.success(request, "Your password has been changed successfully.")
                    return redirect('profile')  # Change this to 'profile' to redirect to the profile view
            else:
                messages.error(request, "New passwords do not match.")
        else:
            messages.error(request, "Current password is incorrect.")
    return render(request, 'users/profile2.html')  # Render the change password form if GET request



from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import render
from django.conf import settings
def password_reset_request(request):
    if request.method == 'POST':
        form = UsernameEmailForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            user = None
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None
            if user:
                subject = "Password Reset Requested"
                email_template_name = "users/password_reset_email.html"
                c = {
                    "email": user.email,
                    'domain': request.META['HTTP_HOST'],
                    'site_name': 'Your Site Name',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                send_mail(subject, email, settings.DEFAULT_FROM_EMAIL, [user.email])                
                return render(request, 'users/password_reset_done.html')  # Create this template
    form = UsernameEmailForm()
    return render(request, 'users/password_reset.html', {'form': form})

