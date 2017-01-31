from django import forms


class GuestDonationForm(forms.Form):
    email = forms.EmailField()
    reemail = forms.EmailField(label='Verify Email')

    def clean_reemail(self):
        email = self.cleaned_data.get("email")
        reemail = self.cleaned_data.get("reemail")

        if email == reemail:
            return reemail
        else:
            raise forms.ValidationError("Email needs to be same")