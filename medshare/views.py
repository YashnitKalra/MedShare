from django.shortcuts import render, redirect
from django.http import HttpResponse
from math import radians, cos, sin, asin, sqrt, ceil
from random import randint
import json
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from .models import *
import datetime
from django.db.models import Q, F

def generateOTP():
    return "".join([str(randint(1,9)) for _ in range(6)])

def emailExists(email):
    return User.objects.filter(email = email).exists()

def usernameExists(username):
    return User.objects.filter(username = username).exists()

def sendMail(subject,message,to):
    fromMail = "no-reply"
    send_mail(subject, message, fromMail, to)

def distance(lat1, lon1, lat2, lon2):
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2)
       
    # Haversine formula  
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return(c * r) # calculate the result

def isValidSession(request):
    if "id" in request.session and "username" in request.session:
        if request.session['id'] is not None and request.session['username'] is not None:
            return True
    return False

def strToDate(stringDate):
    return datetime.datetime.strptime(stringDate,"%Y-%m-%d").date()

def getRemainingDays(date):
    return (date - datetime.datetime.today().date()).days

# *********************Create your views here.***********************
def medshare(request):
    if request.method=="GET":
        if isValidSession(request):
            user = General_User.objects.get(User__id = request.session['id'])
            return render(request, "dashboard.html", {"area": user.Area_Name, "count": user.Requests_Remaining})
        return render(request, "medshare.html")
    elif request.method=="POST":
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
        try:
            gen_user = General_User.objects.get(User__username = username)
        except:
            return render(request, "message.html", {"messages": ["Username not found"]})
        user = auth.authenticate(username = username, password = password)
        if user is None:
            return render(request, "message.html", {"messages": ["Incorrect Password"]})
        else:
            auth.login(request, user)
            request.session['id'] = user.id
            request.session['username'] = user.username
            return redirect("/")
        

def signup(request):
    if request.method=="GET":
        return render(request, "signup.html")
    elif request.method=="POST":
        firstname, lastname = request.POST['firstname'].strip(), request.POST['lastname'].strip()
        username, email = request.POST['username'].strip(), request.POST['email'].strip()
        password, area = request.POST['password1'].strip(), request.POST['area2'].strip()
        lat, lon = float(request.POST['lat'].strip()), float(request.POST['lon'].strip())
        if not emailExists(request.POST['email']) and not usernameExists(request.POST['username']):
            user = User.objects.create(first_name = firstname, last_name = lastname, username = username, email = email, password = make_password(password))
            user.save()
            gen_user = General_User.objects.create(User = user, Area_Name = area, Latitude = lat, Longitude = lon)
            gen_user.save()
            request.session['id'] = user.id
            request.session['username'] = user.username
        else:
            return render(request, "message.html", {"messages": ["Email or Username already exists"]})
        return redirect("/")

def sendOtp(request):
    if request.method=="POST":
        email = request.POST['email']
        if emailExists(email):
            return HttpResponse(json.dumps({"error":True, "message":"Email already Exists"}))
        otp = generateOTP()
        # sendMail("Welcome To MedShare", f"Your One-Time-Password is {otp}", [email])
        print(otp)
        return HttpResponse(json.dumps({"error":False, "otp": make_password(otp)}))

def verifyOtp(request):
    if request.method=="POST":
        otp = request.POST['otp']
        otp2 = request.POST['otp2'] # encrypted
        return HttpResponse(json.dumps({"error": not check_password(otp,otp2)}))

def verifyUsername(request):
    if request.method=="POST":
        username = request.POST['username']
        if len(username)<3:
            return HttpResponse(json.dumps({'error':True, "message":"Enter atleast 3 characters"}))
        elif usernameExists(username):
            return HttpResponse(json.dumps({"error":True, "message":"Username already taken"}))
        return HttpResponse(json.dumps({"error":False}))

def logout(request):
    try:
        auth.logout(request)
    except:
        pass
    try:
        del request.session['id']
        del request.session['username']
    except:
        pass
    return redirect("/")

def uploadMedicinalProduct(request):
    if request.method=="POST":
        if isValidSession(request):
            product = request.POST['productName'].strip()
            description = request.POST['description'].strip()
            date = request.POST['expiryDate'].strip()
            quantity = int(request.POST['quantity'].strip())
            if len(product)==0:
                return HttpResponse(json.dumps({"error":True, "message":"Invalid Product Name"}))
            elif len(date)==0:
                return HttpResponse(json.dumps({"error":True, "message":"Invalid Expiry Date"}))
            elif quantity<1:
                return HttpResponse(json.dumps({"error":True, "message":"Invalid Product Quantity"}))
            else:
                date = strToDate(date)
                days = getRemainingDays(date)
                id = request.session['id']
                if days<=0:
                    return HttpResponse(json.dumps({"error":True, "message":"Your product is already expired"}))
                else:
                    gen_user = General_User.objects.get(User__id = id)
                    mp = Medicinal_Product.objects.create(General_User = gen_user, Name = product, Description=description, Expiry_Date=date, Quantity=quantity)
                    mp.save()
                    return HttpResponse(json.dumps({"error":False}))
        else:
            return redirect("/")
    
def searchProducts(request):
    if isValidSession(request):
        if request.method=="GET":
            productName, sortBy = request.GET['product'].strip(), request.GET['sortBy']
            gen_user = General_User.objects.get(User__id=request.session['id'])
            products = Medicinal_Product.objects.filter(
                Name__icontains = productName, Expiry_Date__gt=datetime.datetime.today().date(), Quantity__gt=0
            ).exclude(General_User = gen_user)
            result = []
            for product in products:
                dist = distance(gen_user.Latitude, gen_user.Longitude, product.General_User.Latitude, product.General_User.Longitude)
                if dist<=30:
                    result.append([
                        product.Name,
                        product.Description,
                        getRemainingDays(product.Expiry_Date),
                        product.General_User.Area_Name.split(",")[0],
                        ceil(dist) if dist>=1 else 1,
                        product.id,
                        product.Quantity
                    ])
            if sortBy=="0":
                result.sort(key = lambda x:x[4])
            else:
                result.sort(key = lambda x:x[2])
            if len(result)==0:
                return HttpResponse(json.dumps({"found":False}))
            else:
                return HttpResponse(json.dumps({"found":True, "products":result, "area":gen_user.Area_Name}))
    else:
        return redirect("/")

def requestProduct(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        id = int(request.POST['id'])
        quantity = int(request.POST['quantity'])
        if quantity<1:
            return HttpResponse(json.dumps({"error":True, "message": "Error: Minimum Quantity should be 1"}))
        gen_user = General_User.objects.get(User__id = request.session['id'])
        if gen_user.Requests_Remaining==0:
            return HttpResponse(json.dumps({"error":True, "message": "Error: Maximum Limit reached for this month"}))
        med_product = Medicinal_Product.objects.get(id=id)
        if med_product.Quantity<quantity:
            return HttpResponse(json.dumps({"error":True, "message": "Error: Quantity Exceeded the Available Quantity"}))
        donation = Donation.objects.create(Medicinal_Product=med_product, Donator=med_product.General_User, Receiver=gen_user, Date=datetime.datetime.now().date(), Quantity=quantity)
        med_product.Quantity -= quantity
        med_product.save()
        General_User.objects.filter(User=gen_user).update(Requests_Remaining=gen_user.Requests_Remaining-1)
        donation.save()
        return HttpResponse(json.dumps({"error":False, "remaining": med_product.Quantity}))
    else:
        return redirect('/')

def requests(request):
    if isValidSession(request) and request.method=="GET":
        id = request.session['id']
        req = Donation.objects.filter(Q(Donator__User__id=id) | Q(Receiver__User__id=id))
        received = []
        sent = []
        for r in req:
            med_name = r.Medicinal_Product.Name
            remainingDays = getRemainingDays(r.Medicinal_Product.Expiry_Date)
            # check if product is expired or not
            if remainingDays<1:
                remainingDays = "Expired"
            if r.Donator.User.id==id:
                received.append([r.id, r.Receiver.User.username, med_name, remainingDays, r.Quantity, r.Date, r.status[r.Status+2][1]])
            else:
                sent.append([r.id, med_name, remainingDays, r.Quantity, r.status[r.Status+2][1], r.Date])
        return render(request, "requests.html", {"received":received[::-1], "sent":sent[::-1]})
    else:
        return redirect("/")

def withdrawRequest(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        donation_id = request.POST['id']
        donation = Donation.objects.get(id=donation_id)
        if donation.Status!=0:
            return HttpResponse(json.dumps({'error':True, 'message': "Error: Please Refresh, Donator has either accepted/rejected your request."}))
        med_product = donation.Medicinal_Product
        med_product.Quantity += donation.Quantity
        gen_user = donation.Receiver
        gen_user.Requests_Remaining += 1
        donation.delete()
        med_product.save()
        gen_user.save()
        return HttpResponse(json.dumps({'error':False}))
    else:
        return redirect("/")

def acceptRequest(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        dontation_id = request.POST['id']
        try:
            donation = Donation.objects.get(id=dontation_id)
        except:
            return HttpResponse(json.dumps({'error':True, 'message': "Error: Please Refresh, The request might have been withdrawn."}))
        donation.Status = 1
        donation.save()
        return HttpResponse(json.dumps({'error':False}))
    else:
        return redirect("/")

def rejectRequest(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        donation_id = request.POST['id']
        try:
            donation = Donation.objects.get(id=donation_id)
        except:
            return HttpResponse(json.dumps({'error':True, 'message': "Error: Please Refresh, The request might have been WITHDRAWN."}))
        donation.Status = -1
        donation.save()
        receiver = donation.Receiver
        receiver.Requests_Remaining += 1
        receiver.save()
        med_prod = donation.Medicinal_Product
        med_prod.Quantity += donation.Quantity
        med_prod.save()
        return HttpResponse(json.dumps({'error':False}))
    else:
        return redirect("/")

def cancelRequest(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        donation_id = request.POST['id']
        donation = Donation.objects.get(id=donation_id)
        if donation.Status==1:
            donation.Status = -2
            donation.save()
            med_prod = donation.Medicinal_Product
            med_prod.Quantity += donation.Quantity
            med_prod.save()
            return HttpResponse(json.dumps({'error':False}))
        else:
            return HttpResponse(json.dumps({'error':True, "message": "Error: Please Refresh the Page"}))
    else:
        return redirect("/")

def sendOtpToReceiver(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        donation_id = request.POST['id']
        donation = Donation.objects.get(id=donation_id)
        if donation.Status==1:
            otp = generateOTP()
            sendMail(
                "MedShare Exchange Confirmation",
                f"Your one-time-password is {otp}\n\nTell this OTP to the donator.",
                [donation.Receiver.User.email]
            )
            return HttpResponse(json.dumps({'error':False, 'otp':make_password(otp)}))
        else:
            return HttpResponse(json.dumps({'error':True, 'message':"Error: Please Refresh, The request might have been CANCELLED"}))
    else:
        return redirect("/")

def confirmExchange(request):
    if request.is_ajax() and request.method=="POST" and isValidSession(request):
        dontation_id = request.POST['id']
        otp = request.POST['otp']
        otp2 = request.POST['otp2'] # encrypted
        donation = Donation.objects.get(id=dontation_id)
        if donation.Status==1:
            if check_password(otp, otp2):
                donation.Status = 2
                donation.save()
                return HttpResponse(json.dumps({"error":False}))
            else:
                return HttpResponse(json.dumps({'error':True, 'message':"Error: Invalid OTP"}))
        else:
            return HttpResponse(json.dumps({'error':True, 'message':"Error: Please Refresh, The request might have been CANCELLED"}))
    else:
        return redirect('/')

def myDonations(request):
    if request.method=="GET" and isValidSession(request):
        med_prods = Medicinal_Product.objects.filter(General_User__User__id = request.session['id'])
        data = {}
        for med_prod in med_prods:
            data[med_prod.id] = [med_prod.Name, med_prod.Description, med_prod.Expiry_Date, med_prod.Quantity]
        return render(request, "myDonations.html", {"donations": data})
    return redirect("/")

def profile(request):
    if request.method=="GET" and isValidSession(request):
        user = General_User.objects.get(User__id = request.session['id'])
        data = {
            "name": f"{user.User.first_name} {user.User.last_name}",
            "email": user.User.email, 'username': user.User.username, "area": user.Area_Name,
            "successful_donations": Donation.objects.filter(Donator__User__id = request.session['id'], Status = 2).count(),
            "donations_received": Donation.objects.filter(Receiver__User__id = request.session['id'], Status = 2).count()
        }
        return render(request, "profile.html", data)
    return redirect("/")

def contactUs(request):
    return render(request, 'contactUs.html')