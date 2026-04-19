"""Debug CSS loading on Vercel"""
import requests
import re

print('🔍 Checking Vercel Frontend CSS...')
try:
    r = requests.get('https://resume-checker-h4mi.vercel.app/', timeout=5)
    html = r.text
    
    # Look for CSS references
    css_links = re.findall(r'<link[^>]*href=["\']([^"\']*\.css)["\']', html)
    print(f'\n📌 Found CSS files: {len(css_links)}')
    for link in css_links:
        print(f'   - {link}')
    
    # Try to fetch the main CSS
    if css_links:
        base = 'https://resume-checker-h4mi.vercel.app'
        for link in css_links:
            css_url = link if link.startswith('http') else base + link
            try:
                css_r = requests.get(css_url, timeout=5)
                print(f'\n📄 {link}: {css_r.status_code}')
                if '#F8F6F2' in css_r.text or 'F8F6F2' in css_r.text:
                    print('   ✅ Modern CSS colors found!')
                elif '#D95F2B' in css_r.text or 'D95F2B' in css_r.text:
                    print('   ✅ Modern accent color found!')
                else:
                    print('   ⚠️  CSS loaded but no modern colors detected')
                    if css_r.text:
                        print(f'   Size: {len(css_r.text)} bytes')
                        print(f'   First 150 chars: {css_r.text[:150]}...')
            except Exception as e:
                print(f'   ❌ Could not fetch: {e}')
    else:
        print('   ⚠️  No CSS files found in HTML')
    
except Exception as e:
    print(f'Error: {e}')
