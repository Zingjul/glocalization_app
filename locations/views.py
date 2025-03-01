from django.shortcuts import render
from django.views.generic import FormView
from .forms import LocationForm

class LocationView(FormView):
    template_name = 'location_form.html'  # Template to render
    form_class = LocationForm  # Form class to use
    # success_url = '/success/'  # URL to redirect to after successful form submission (optional)

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.GET or None)  # Handle GET requests (form pre-population)
        context = {'form': form}
        return self.render_to_response(context)

    # If you need to handle POST requests (form submission):
    # def post(self, request, *args, **kwargs):
    #     form = self.form_class(request.POST)  # Use request.POST for form submission
    #     if form.is_valid():
    #         # Process the form data (e.g., save to database)
    #         # ... your logic here ...
    #         return self.form_valid(form) # Redirect on success
    #     else:
    #         return self.form_invalid(form) # Re-render form with errors

    # def form_valid(self, form):
    #     # Called when form is valid.  Can redirect or render a different template
    #     # Example:
    #     # return HttpResponseRedirect(self.success_url)  # Redirect
    #     # Or render a different template
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     # Called when form is invalid. Re-render the form with errors
    #     return self.render_to_response(self.get_context_data(form=form))