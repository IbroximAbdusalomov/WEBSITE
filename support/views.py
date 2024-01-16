from django.shortcuts import render, redirect
from django.views import View
from .models import SupportTicket
from .forms import SupportTicketForm


class SupportView(View):
    template_name = "support/support_form.html"

    def get(self, request, *args, **kwargs):
        form = SupportTicketForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.user = request.user
            support_ticket.save()
            return redirect("support_success")
        return render(request, self.template_name, {"form": form})


class SupportSuccessView(View):
    template_name = "support/support_success.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
