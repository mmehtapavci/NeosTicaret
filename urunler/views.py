from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from .forms import *
from django.contrib import messages
import iyzipay
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import pprint
from django.core.cache import cache

# Create your views here.
api_key = 'sandbox-1g0SUo4hsdDb8NoBwTHLYccmlaS9pUsZ'    # canlıya alındığında hepsinin başındaki sendbox- silinecek.
secret_key = 'sandbox-B0KbPcWjAqQeIN5jAPmlKW9pgsWooEv7'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()

def payment(request):
    context = dict()
    kullanici = request.user
    odeme = Odeme.objects.get(user = kullanici, odendiMi = False)
    fiyat =odeme.total
    buyer={
        'id': 'BY789',
        'name': 'kullanici.username',
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': 'email@email.com',
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': str(kullanici.last_login),
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address={
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items=[
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request={
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': int(fiyat),
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    #print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    print(json_content["token"])
    token = json_content['token']
    cache.set('token', token)
    print("************************")
    sozlukToken.append(json_content["token"])
    return HttpResponse(f'<div id="iyzipay-checkout-form" class="responsive">{json_content["checkoutFormContent"]}</div>')


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')
    token = cache.get('token')

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': sozlukToken[0]
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda 
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    #print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    #print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)



def success(request):
    odeme = Odeme.objects.get(user = request.user, odendiMi = False)
    odeme.odendiMi = True
    odeme.save()
    sepetim = Sepet.objects.filter(ekleyen = request.user, odendiMi = False)
    for i in sepetim:
        i.odendiMi = True
        i.save()
    messages.success(request, 'Ödeme Başarılı')
    return redirect('index')


def fail(request):
    messages.error(request, 'Ödeme Başarısız. Tekrar Deneyin.')
    return redirect('sepetim')



def index(request):
    urunler = Urun.objects.all()
    search = ''
    if request.GET.get('search'):
        search = request.GET.get('search')
        urunler = Urun.objects.filter(
            Q(isim__icontains = search) |
            Q(kategori__isim__icontains = search)
        )
    if request.method == 'POST':
        if request.user.is_authenticated:
            urunId = request.POST['urunId']
            adet = request.POST['adet']
            urunum = Urun.objects.get(id = urunId)
            if Sepet.objects.filter(ekleyen = request.user, urun = urunum, odendiMi =False).exists():
                sepet = Sepet.objects.get(ekleyen = request.user, urun = urunum, odendiMi = False)
                sepet.adet += int(adet)
                # sepet.total = urunum.fiyat * sepet.adet   models.py'dan yapıldı
                sepet.save()

            else:
                sepet = Sepet.objects.create(
                    ekleyen = request.user,
                    urun = urunum,
                    adet = adet,
                    total = urunum.fiyat * int(adet)
                )
                sepet.save()
            return redirect('index')
        else:
            messages.warning(request, 'Giriş Yapınız')
            return redirect('login')
    
    context = {
        'urunler':urunler,
        'search': search
    }
    return render(request, 'index.html', context)

def urun(request, urunId):
    urunum = Urun.objects.get(id = urunId)
    context = { 
        'urun': urunum
    }
    return render(request, 'detail.html', context)

def olustur(request):
    # kategoriler = Kategori.objects.all()
    # if request.method == 'POST':
    #     resim = request.FILES['resim']
    #     isim = request.POST['isim']
    #     aciklama = request.POST['aciklama']
    #     fiyat = request.POST['fiyat']
    #     kategori = request.POST['kategori']
    #     urun =  Urun.objects.create(
    #         kategori_id = kategori,
    #         isim = isim,
    #         aciklama = aciklama,
    #         fiyat = fiyat,
    #         resim = resim
    #     )
    #     urun.save()
    #     print("Ürün Oluştıruldu")
    #     return redirect('olustur')
    form = UrunForm()
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    context = {
        # 'kategoriler':kategoriler
        'form':form
    }
    return render (request, 'olustur.html', context)

def sepetim(request):
    urunler = Sepet.objects.filter(ekleyen = request.user, odendiMi = False)
    toplam = 0
    for i in urunler:
        toplam += i.total
    if request.method == 'POST':
        if 'odeme' not in request.POST:
            sepetId = request.POST['sepetId']
            sepet = Sepet.objects.get(id = sepetId)
        if 'sil' in request.POST:
            sepet.delete()
            messages.success(request, 'Ürün Silindi')
            return redirect('sepetim')
        elif 'guncelle' in request.POST:
            adet = request.POST['adet']
            if adet == '0':
                sepet.delete()
            else:
                sepet.adet = adet
                # sepet.total = sepet.urun.fiyat * int(adet)
                sepet.save()
                messages.success(request, 'Sepet Güncellendi')
            return redirect('sepetim')
        elif 'odeme' in request.POST:
            if Odeme.objects.filter(user = request.user, odendiMi = False).exists():
                pass
            else:
                odeme = Odeme.objects.create(
                    user = request.user,
                    total = toplam
            )
                odeme.urunler.add(*urunler)
                odeme.save()
            return redirect('payment')
    
    context = {
        'urunler':urunler,
        'toplam':toplam
    }
    return render (request, 'sepetim.html', context)