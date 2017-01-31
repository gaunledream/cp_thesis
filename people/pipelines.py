from .models import  Member
from django.core.mail import send_mail
from community.models import Village, School
import requests
from django.conf import settings


def save_profile(backend, user, response, *args, **kwargs):
    """this method is used to collect village/school from facebook and notify the admin about the creation of the new
    community"""
    if backend.name == 'facebook':
        profile = user.get_profile()
        if profile is None:
            profile = Member(id=user.id)
        access_token = response["access_token"]
        fullname = response["name"]
        uid = response["id"]
        profile.uid = uid
        from_email =  response["email"]
        profile.name = fullname
        profile.access_token = access_token
        print (not profile.village or not profile.school), "not profile.village or not profile.school"
        if not profile.village or not profile.school:
            get_query = "https://graph.facebook.com/v2.5/" + uid + "?fields=education,hometown,email&access_token=" + access_token
            fbresponse = requests.get(get_query).json()
            if not profile.village:  
                try:
                    town = fbresponse["hometown"]["name"]
                except:
                    town = "default" + str(user)
                village_instance, village_created = Village.objects.get_or_create(name=town)
                if village_created:#take to address select page
                    village_instance.created_by = profile
                    village_instance.save()
                    send_mail("Village Creation", str(village_instance) + " is created! Please, verify it! Thank you!", from_email, [settings.ADMINS])
                profile.village = village_instance
            print not profile.school, "not profile.school"
            if not profile.school:
                try:
                    for education in fbresponse["education"]:
                        if education["type"] == "High School":
                            school = education["school"]["name"]
                except:
                    school = "default" + str(user)
                school_instance, school_created = School.objects.get_or_create(name=school)#school has village_instance but it would be updated only after verifying the address.
                if school_created:#take to address select page
                    school_instance.created_by = profile
                    school_instance.save()
                    send_mail("Village Creation", str(school_instance) + " is created! Please, verify it! Thank you!", from_email, [settings.ADMINS])
                profile.school = school_instance
        profile.uid = uid
        profile.name = fullname
        profile.access_token = access_token
        profile.save()