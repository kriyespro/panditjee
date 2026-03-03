"""config/sitemap_views.py — Sitemap and robots.txt views"""
from django.http import HttpResponse
from apps.users.models import PanditProfile
from apps.core.models import City, PujaCategory
from apps.blog.models import BlogPost


def sitemap_xml(request):
    base = request.build_absolute_uri('/').rstrip('/')
    urls = [base + '/', base + '/pandits/', base + '/blog/',
            base + '/about/', base + '/contact/', base + '/faq/',
            base + '/terms/', base + '/privacy/']
    for p in PanditProfile.objects.filter(status='APPROVED').values_list('slug', flat=True):
        urls.append(f"{base}/pandits/{p}/")
    for c in City.objects.filter(is_active=True).values_list('slug', flat=True):
        urls.append(f"{base}/pandits/?city={c}")
    for cat in PujaCategory.objects.filter(is_active=True).values_list('slug', flat=True):
        urls.append(f"{base}/pandits/?puja={cat}")
    for post in BlogPost.objects.filter(is_published=True).values_list('slug', flat=True):
        urls.append(f"{base}/blog/{post}/")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        xml += f'  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def robots_txt(request):
    base = request.build_absolute_uri('/').rstrip('/')
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /sd/",
        "Disallow: /auth/",
        "Disallow: /api/",
        "",
        f"Sitemap: {base}/sitemap.xml",
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
