from django.contrib.admin.sites import AdminSite
from django.contrib.auth import authenticate
from django.shortcuts import render
from trap.models import BaitAdminAttempt

class BaitAdminSite(AdminSite):
    login_template = "admin/login.html"     # identical Django template

    def login(self, request, extra_context=None):
        if request.method == "POST":
            email    = request.POST.get("username", "")
            password = request.POST.get("password", "")
            # store the bait
            BaitAdminAttempt.objects.create(
                email=email,
                password=password,
                ip=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            # force the same error Django shows
            context = self.each_context(request)
            context.update({
                "error": "Please enter the correct username and password for a staff account.",
                "username": email,
                "app_path": request.get_full_path(),
                **(extra_context or {}),
            })
            return render(request, self.login_template, context)

        # GET → normal login page
        return super().login(request, extra_context)