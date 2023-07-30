from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, IntegerField, CharField, BooleanField
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    telephone = CharField(max_length=50)
    email = EmailField(unique=True)
    score = IntegerField(default=50, validators=[
        # MaxValueValidator(50),
        MinValueValidator(0)
    ])

    trust = BooleanField(default=False)

    # stars

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


'''
uskuna_hammasi - Hammasi
uskuna_umumiy
uskuna_plastmassa
uskuna_tekstil
uskuna_agro
uskuna_metall
uskuna_qadoqlash
uskuna_sanoat
uskuna_ombor
uskuna_oziq
uskuna_kimyoviy
uskuna_energiya
uskuna_xizmat
uskuna_qurilish
uskuna_yogoch
uskuna_yordamchi
uskuna_mashinasozlik


xomashyo_plastmassa
xomashyo_tekstil
xomashyo_mineral
xomashyo_metall
xomashyo_oziq
xomashyo_kosmetika
xomashyo_sanoat
xomashyo_xojalik
xomashyo_boshqa

xizmat_umumiy
xizmat_plastmassa
xizmat_tekstil
xizmat_agro
xizmat_metall
xizmat_qadoqlash
xizmat_sanoat
xizmat_ombor
xizmat_oziq
xizmat_kimyoviy
xizmat_energiya
xizmat_xizmat
xizmat_qurilish
xizmat_yogoch
xizmat_yordamchi
xizmat_mashinasozlik

texnolog_umumiy
texnolog_plastmassa
texnolog_tekstil
texnolog_agro
texnolog_metall
texnolog_qadoqlash
texnolog_sanoat
texnolog_ombor
texnolog_oziq
texnolog_kimyoviy
texnolog_energiya
texnolog_xizmat
texnolog_qurilish
texnolog_yogoch
texnolog_yordamchi
texnolog_mashinasozlik
'''
