from checker import (
    SITES,
    build_url,
    check_headers,
    check_site,
    is_https,
    retry_check,
    scan_sites,
    show_response,
)

# Rulează acest fișier, nu checker.py: demonstrațiile sunt în main.py.
# Partea 1: apeluri pentru build_url și is_https
print("Partea 1, build_url:", build_url("example.com", "login"), flush=True)
print("Partea 1, build_url:", build_url("example.com", "/login"), flush=True)

print("Partea 1, is_https:", is_https("https://example.com"), flush=True)
print("Partea 1, is_https:", is_https("http://example.com"), flush=True)

# Partea 2: apeluri pentru show_response
print("Partea 2, show_response, site disponibil:", flush=True)
show_response("https://example.com")
print("Partea 2, show_response, adresă invalidă:", flush=True)
show_response("http://this-site-does-not-exist.invalid")

# Partea 3: apeluri pentru check_site
for site in SITES:
    print(f"Partea 3, check_site ({site}): {check_site(site)}", flush=True)
print(
    "Partea 3, check_site (adresă invalidă):",
    check_site("http://this-site-does-not-exist.invalid"),
    flush=True,
)

# Partea 4: apelul scan_sites()
print("Partea 4, scan_sites:", flush=True)
scan_sites()

# Partea 5: apeluri pentru check_headers
print("Partea 5, check_headers (antete parțiale):", check_headers(SITES[10]), flush=True)
print("Partea 5, check_headers (antete parțiale):", check_headers(SITES[11]), flush=True)
print(
    "Partea 5, check_headers (adresă invalidă):",
    check_headers("http://this-site-does-not-exist.invalid"),
    flush=True,
)

# Partea 6: apeluri pentru retry_check
print(
    "Partea 6, retry_check (200):",
    retry_check("https://httpbin.org/status/200"),
    flush=True,
)
print(
    "Partea 6, retry_check (404):",
    retry_check("https://httpbin.org/status/404"),
    flush=True,
)
print(
    "Partea 6, retry_check (500, 2 încercări):",
    retry_check("https://httpbin.org/status/500", attempts=2),
    flush=True,
)
print(
    "Partea 6, retry_check (adresă invalidă):",
    retry_check("http://this-site-does-not-exist.invalid"),
    flush=True,
)
